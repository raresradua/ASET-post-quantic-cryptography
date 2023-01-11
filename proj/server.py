import datetime
import uuid

from fastapi import FastAPI, Request, HTTPException, Depends
from mongo.mongo import Mongo
from utilities.utilities import logged
from auth.auth_handler import signJWT, decodeJWT
from auth.auth_bearer import JWTBearer
from passlib.hash import sha256_crypt
from codes.goppa_code import GoppaCode
from codes.reed_solomon import ReedSolomon
from codes.attack import generate_errors, attack_cipher
from utilities.utilities import get_vec_from_str

app = FastAPI()
mongo = Mongo()
app.title = 'ASET Post-quantum Cryptography'
app.contact = {
    'name': 'GitHub project',
    'url': 'https://github.com/raresradua/ASET-post-quantic-cryptography'
}
app.version = '1.0.0'

goppa = GoppaCode()
reed = ReedSolomon()
cryptosystems = {
    'goppa': goppa,
    'reed': reed
}


@app.get('/')
async def home():
    return {
        "message": "Welcome :)"
    }


@app.post('/register')
async def register(request: Request):
    payload = await request.json()
    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        raise HTTPException(400, 'Username and password must be provided.')
    collection = mongo.get_collection()
    user = collection.find_one({'username': username})
    if not user:
        collection.insert_one({'username': username, 'password': sha256_crypt.encrypt(password)})
        mongo.db_cursor['statistics'].insert_one(
            {'event': 'register', 'data': {'username': username}, 'time': datetime.datetime.utcnow()})
    else:
        return {
            'detail': 'user already exists'
        }
    return {
        'detail': 'user successfully created'
    }


@app.post('/login')
async def get_token_login(request: Request):
    payload = await request.json()
    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        raise HTTPException(400, 'Username and password must be provided.')
    collection = mongo.get_collection()
    user = collection.find_one({'username': username})
    if not user:
        mongo.db_cursor['statistics'].insert_one(
            {'event': 'login', 'data': {'username': username, 'login': 'failed', 'reason': 'user does not exist'},
             'time': datetime.datetime.utcnow()})
        return {
            'detail': 'user does not exist'
        }
    else:
        if sha256_crypt.verify(password, user['password']):
            mongo.db_cursor['statistics'].insert_one(
                {'event': 'login', 'data': {'username': username, 'login': 'success'},
                 'time': datetime.datetime.utcnow()})
            return signJWT(username)
        mongo.db_cursor['statistics'].insert_one(
            {'event': 'login', 'data': {'username': username, 'login': 'failed', 'reason': 'invalid login credentials'},
             'time': datetime.datetime.utcnow()})
        return {
            'detail': 'invalid login credentials'
        }


@app.post('/generate_keys', dependencies=[Depends(JWTBearer())])
@logged
async def generate_keys(request: Request):
    payload = await request.json()
    if not payload.get('cryptosystem') or payload.get('cryptosystem') not in ['reed', 'goppa']:
        return {
            'detail': 'You must choose either "reed" or "goppa"'
        }
    user = decodeJWT(request.headers.get('Authorization').split(' ')[1])
    if not user:
        return {
            'detail': 'Invalid token.'
        }
    keys = cryptosystems[payload.get('cryptosystem')].generate_keys()
    pub, prv = keys['public_key'], keys['private_key']
    mongo.get_collection().update_one({'username': user['username']},
                                      {"$set": {payload.get('cryptosystem'): {'pub': pub, 'prv': prv}}})
    mongo.db_cursor['statistics'].insert_one(
        {'event': 'key_generation', 'data': {'username': user['username'], 'cryptosystem': payload['cryptosystem']},
         'time': datetime.datetime.utcnow()})
    return {
        'public_key': pub,
        'private_key': prv,
        'cryptosystem': payload.get('cryptosystem'),
        'message': 'public_key and private_key to encrypt and decrypt information'
    }


@app.post('/profile', dependencies=[Depends(JWTBearer())])
@logged
async def profile(request: Request):
    headers = request.headers.get('Authorization')
    user = decodeJWT(headers.split(' ')[1])
    collection = mongo.get_collection()
    mongo.db_cursor['statistics'].insert_one(
        {'event': 'profile_access', 'data': {'username': user['username']}, 'time': datetime.datetime.utcnow()})
    return collection.find_one({'username': user['username']}, {'_id': 0})


@app.post('/encrypt')
@logged
async def encrypt(request: Request):
    payload = await request.json()
    user = decodeJWT(request.headers.get('Authorization').split(' ')[1])
    if not user:
        mongo.db_cursor['statistics'].insert_one(
            {'event': 'encrypt', 'data': {'username': user['username'], 'encrypt': 'failed', 'reason': 'invalid token'},
             'time': datetime.datetime.utcnow()})
        return {
            'detail': 'Invalid token.'
        }
    if 'message' not in payload or 'cryptosystem' not in payload or 'to' not in payload:
        mongo.db_cursor['statistics'].insert_one({'event': 'encrypt',
                                                  'data': {'username': user['username'], 'encrypt': 'failed',
                                                           'reason': 'missing message or to field'},
                                                  'time': datetime.datetime.utcnow()})
        return {
            'detail': 'Missing message or cryptosystem or to field'
        }
    if payload['cryptosystem'] not in ['reed', 'goppa']:
        mongo.db_cursor['statistics'].insert_one({'event': 'encrypt',
                                                  'data': {'username': user['username'], 'encrypt': 'failed',
                                                           'reason': 'invalid cryptosystem value'},
                                                  'time': datetime.datetime.utcnow()})
        return {
            'detail': 'Invalid cryptosystem value'
        }

    dest_info = mongo.db_cursor['users'].find_one({'username': payload['to']})
    if not dest_info or not dest_info.get(payload.get('cryptosystem')):
        mongo.db_cursor['statistics'].insert_one({'event': 'encrypt',
                                                  'data': {'username': user['username'], 'encrypt': 'failed',
                                                           'reason': 'invalid username or no pk for username'},
                                                  'time': datetime.datetime.utcnow()})
        return {
            'detail': 'Invalid username or username does not have a public key for cryptosystem: {}'.format(
                payload.get('cryptosystem'))
        }
    message_id = str(uuid.uuid4())
    enc_message = cryptosystems[payload['cryptosystem']].encrypt_message(payload['message'],
                                                                         dest_info[payload['cryptosystem']][
                                                                             'pub'])
    retr = {'message_id': message_id, 'message': enc_message, 'to': dest_info['username'], 'from': user['username']}
    mongo.db_cursor['messages'].insert_one(
        {'message_id': message_id, 'message': enc_message, 'to': dest_info['username'], 'from': user['username'],
         'cryptosystem': payload['cryptosystem']})
    mongo.db_cursor['statistics'].insert_one({'event': 'encrypt',
                                              'data': {'username': user['username'], 'encrypt': 'success',
                                                       'encrypted': retr},
                                              'time': datetime.datetime.utcnow()})

    return {
        'done': retr
    }


@app.post('/decrypt')
@logged
async def decrypt(request: Request):
    payload = await request.json()
    user = decodeJWT(request.headers.get('Authorization').split(' ')[1])
    if not user:
        mongo.db_cursor['statistics'].insert_one(
            {'event': 'decrypt', 'data': {'username': user['username'], 'encrypt': 'failed', 'reason': 'invalid token'},
             'time': datetime.datetime.utcnow()})
        return {
            'detail': 'Invalid token.'
        }
    if 'message_id' not in payload:
        mongo.db_cursor['statistics'].insert_one({'event': 'decrypt',
                                                  'data': {'username': user['username'], 'encrypt': 'failed',
                                                           'reason': 'no message id found'},
                                                  'time': datetime.datetime.utcnow()})
        return {
            'detail': 'Message id not in request'
        }

    message_info = mongo.db_cursor['messages'].find_one({'message_id': payload['message_id']})
    if not message_info:
        mongo.db_cursor['statistics'].insert_one({'event': 'decrypt',
                                                  'data': {'username': user['username'], 'encrypt': 'failed',
                                                           'reason': 'invalid message id',
                                                           'message_id': payload['message_id']},
                                                  'time': datetime.datetime.utcnow()})
        return {
            'detail': 'Could not find information for message id: {}'.format(payload['message_id'])
        }

    if message_info['to'] != user['username']:
        mongo.db_cursor['statistics'].insert_one({'event': 'decrypt',
                                                  'data': {'username': user['username'], 'encrypt': 'failed',
                                                           'reason': 'message is not meant for this person',
                                                           'message_id': payload['message_id']},
                                                  'time': datetime.datetime.utcnow()})
        return {
            'detail': 'This message was not meant for you. It was meant for {}'.format(message_info['to'])
        }

    cryptosystem = message_info.get('cryptosystem')

    user_info = mongo.db_cursor['users'].find_one({'username': user['username']})
    print(user_info)
    if not user_info.get(cryptosystem):
        mongo.db_cursor['statistics'].insert_one({'event': 'decrypt',
                                                  'data': {'username': user['username'], 'encrypt': 'failed',
                                                           'reason': 'user does not have a key for this crytptosystem',
                                                           'cryptosystem': cryptosystem,
                                                           'message_id': payload['message_id']},
                                                  'time': datetime.datetime.utcnow()})
        return {
            'detail': 'No relevant key found for cryptosystem {}'.format(cryptosystem)
        }

    ciph, err = message_info['message']
    dec = cryptosystems[cryptosystem].decrypt_message(ciph, err, user_info[cryptosystem]['pub'])
    mongo.db_cursor['statistics'].insert_one({'event': 'decrypt',
                                              'data': {'username': user['username'], 'encrypt': 'success',
                                                       'reason': 'ok',
                                                       'message_id': payload['message_id'],
                                                       'decrypted': dec},
                                              'time': datetime.datetime.utcnow()})
    return {
        'decrypted': dec
    }


@app.get('/get_message/{message_id}')
async def get_message(message_id: str):
    mongo.db_cursor['statistics'].insert_one({'event': 'get_message',
                                              'data': {'message_id': message_id},
                                              'time': datetime.datetime.utcnow()})

    return {'message': mongo.db_cursor['messages'].find_one({'message_id': message_id}, {'_id': 0}) or {
        'detail': 'Message with id {} was not found'.format(message_id)}}


@app.get('/get_messages')
async def get_messages():
    mongo.db_cursor['statistics'].insert_one({'event': 'get_messages',
                                              'data': {},
                                              'time': datetime.datetime.utcnow()})

    return {'messages': list(mongo.db_cursor['messages'].find({}, {'_id': 0})) or []}


@app.get('/attack/{message_id}')
async def attack(message_id: str):
    message_info = mongo.db_cursor['messages'].find_one({'message_id': message_id})
    if not message_info:
        mongo.db_cursor['statistics'].insert_one({'event': 'attack',
                                                  'data': {'message_id': message_id, 'attack': 'failed',
                                                           'reason': 'no message was found with this id'},
                                                  'time': datetime.datetime.utcnow()})

        return {
            'detail': 'No relevant message with this id was found: {}'.format(message_id)
        }
    ciph, err = message_info['message']
    from_user = message_info['to']
    crypto = message_info['cryptosystem']
    pub = mongo.db_cursor['users'].find_one({'username': from_user})[crypto]['pub']
    dec_err = get_vec_from_str(cryptosystems[crypto].fernet_cryptosys.decrypt(err).decode('utf-8'))
    good_errors = generate_errors(dec_err, pub['t'])

    mongo.db_cursor['statistics'].insert_one(
        {'event': 'attack', 'data': {'message_id': message_id, 'attack': 'success'},
         'time': datetime.datetime.utcnow()})
    return {
        'attack_results': attack_cipher(good_errors, cryptosystems[crypto].n, ciph, crypto, pub)
    }


@app.post('/statistics')
async def statistics(request: Request):
    req = await request.json()
    if 'event' not in req.keys() and req['event'] not in ['attack', 'get_message', 'get_messages', 'profile', 'encrypt',
                                                          'decrypt', 'register', 'login', 'key_generation']:
        return {
            'detail': 'event field must be present with the values in [attack, get_message, get_messages, profile_access, encrypt, decrypt, register, login, key_generation]'
        }

    if 'when' not in req.keys() and req['when'] not in ['today', 'last_7_days', 'last_30_days']:
        return {
            'detail': 'when field must be present with the value in [today, last_7_days, last_30_days]'
        }

    match req['when']:
        case 'today':
            return list(mongo.db_cursor['statistics'].find(
                {'event': req['event'], 'time': {'$gte': (datetime.datetime.utcnow() - datetime.timedelta(days=1))}}, {'_id': 0}))
        case 'last_7_days':
            return list(mongo.db_cursor['statistics'].find(
                {'event': req['event'], 'time': {'$gte': (datetime.datetime.utcnow() - datetime.timedelta(days=7))}}, {'_id': 0}))
        case 'last_30_days':
            return list(mongo.db_cursor['statistics'].find(
                {'event': req['event'], 'time': {'$gte': (datetime.datetime.utcnow() - datetime.timedelta(days=30))}}, {'_id': 0}))
