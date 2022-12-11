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
from proj.utilities.utilities import get_vec_from_str


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
        return {
            'detail': 'user does not exist'
        }
    else:
        if sha256_crypt.verify(password, user['password']):
            return signJWT(username)
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
    return collection.find_one({'username': user['username']}, {'_id': 0})


@app.post('/encrypt')
@logged
async def encrypt(request: Request):
    payload = await request.json()
    user = decodeJWT(request.headers.get('Authorization').split(' ')[1])
    if not user:
        return {
            'detail': 'Invalid token.'
        }
    if 'message' not in payload or 'cryptosystem' not in payload or 'to' not in payload:
        return {
            'detail': 'Missing message or cryptosystem or to field'
        }
    if payload['cryptosystem'] not in ['reed', 'goppa']:
        return {
            'detail': 'Invalid cryptosystem value'
        }

    dest_info = mongo.db_cursor['users'].find_one({'username': payload['to']})
    if not dest_info or not dest_info.get(payload.get('cryptosystem')):
        return {
            'detail': 'Invalid username or username does not have a public key for cryptosystem: {}'.format(
                payload.get('cryptosystem'))
        }
    message_id = str(uuid.uuid4())
    enc_message = cryptosystems[payload['cryptosystem']].encrypt_message(payload['message'],
                                                                         dest_info[payload['cryptosystem']][
                                                                             'pub'])
    retr = {'message_id': message_id, 'message': enc_message, 'to': dest_info['username'], 'from': user['username']}
    mongo.db_cursor['messages'].insert_one({'message_id': message_id, 'message': enc_message, 'to': dest_info['username'], 'from': user['username'], 'cryptosystem': payload['cryptosystem']})
    return {
        'done': retr
    }


@app.post('/decrypt')
@logged
async def decrypt(request: Request):
    payload = await request.json()
    user = decodeJWT(request.headers.get('Authorization').split(' ')[1])
    if not user:
        return {
            'detail': 'Invalid token.'
        }
    if 'message_id' not in payload:
        return {
            'detail': 'Message id not in request'
        }

    message_info = mongo.db_cursor['messages'].find_one({'message_id': payload['message_id']})
    if not message_info:
        return {
            'detail': 'Could not find information for message id: {}'.format(payload['message_id'])
        }

    if message_info['to'] != user['username']:
        return {
            'detail': 'This message was not meant for you. It was meant for {}'.format(message_info['to'])
        }

    cryptosystem = message_info.get('cryptosystem')

    user_info = mongo.db_cursor['users'].find_one({'username': user['username']})
    print(user_info)
    if not user_info.get(cryptosystem):
        return {
            'detail': 'No relevant key found for cryptosystem {}'.format(cryptosystem)
        }

    ciph, err = message_info['message']
    dec = cryptosystems[cryptosystem].decrypt_message(ciph, err, user_info[cryptosystem]['pub'])
    return {
        'decrypted': dec
    }


@app.get('/get_message/{message_id}')
async def get_message(message_id: str):
    return {'message': mongo.db_cursor['messages'].find_one({'message_id': message_id}, {'_id': 0}) or {'detail': 'Message with id {} was not found'.format(message_id)}}


@app.get('/get_messages')
async def get_messages():
    return {'messages': list(mongo.db_cursor['messages'].find({}, {'_id': 0})) or []}

@app.get('/attack/{message_id}')
async def attack(message_id: str):
    message_info = mongo.db_cursor['messages'].find_one({'message_id': message_id})
    if not message_info:
        return {
            'detail': 'No relevant message with this id was found: {}'.format(message_id)
        }
    ciph, err = message_info['message']
    from_user = message_info['to']
    crypto = message_info['cryptosystem']
    pub = mongo.db_cursor['users'].find_one({'username': from_user})[crypto]['pub']
    dec_err = get_vec_from_str(cryptosystems[crypto].fernet_cryptosys.decrypt(err).decode('utf-8'))
    good_errors = generate_errors(dec_err, pub['t'])

    return {
        'attack_results': attack_cipher(good_errors, cryptosystems[crypto].n, ciph, crypto, pub)
    }
