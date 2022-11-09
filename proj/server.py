from fastapi import FastAPI, Request, HTTPException
from mongo.mongo import Mongo
from base64 import b64encode, b64decode
from utilities.utilities import logged

app = FastAPI()
mongo = Mongo()
app.title = 'ASET Post-quantum Cryptography'
app.contact = {
    'name': 'GitHub project',
    'url': 'https://github.com/raresradua/ASET-post-quantic-cryptography'
}
app.version = '1.0.0'


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
        collection.insert_one({'username': username, 'password': password, 'token': b64encode(bytes(username + 'DDD' + password, 'utf-8'))})
    else:
        return {
            'detail': 'user already exists'
        }
    return {
        'token': b64encode(bytes(username + 'DDD' + password, 'utf-8'))
    }


@app.post('/generate_keys')
@logged
async def generate_keys(request: Request):
    payload = await request.json()
    if not payload.get('cryptosystem'):
        return {
            'detail': 'You must choose either "reed" or "goppa"'
        }
    user = mongo.get_collection().find_one({'token': payload.get('token')})
    # TODO: add crypto system, generate key for it, update user
    pub, prv = 'public_key', 'private_key'
    mongo.get_collection().update_one({'token': bytes(payload.get('token'), 'utf-8')}, {"$set": {payload.get('cryptosystem'): {'pub': pub, 'prv': prv}}})
    return {
        'public_key': pub,
        'private_key': prv,
        'cryptosystem': payload.get('cryptosystem'),
        'message': 'public_key and private_key to encrypt and decrypt information'
    }

@app.post('/profile')
@logged
async def profile(request: Request):
    payload = await request.json()
    username, password = b64decode(bytes(payload.get('token'), 'utf-8')).split(b'DDD')
    return {
        'username': username.decode('utf-8'),
        'password': password.decode('utf-8')
    }


@app.post('/upload')
@logged
async def upload_file():
    raise NotImplementedError


@app.post('/encrypt')
@logged
async def encrypt():
    raise NotImplementedError


@app.post('/decrypt')
@logged
async def decrypt():
    raise NotImplementedError


@app.get('/get_file/{file_id}')
@logged
async def get_file(file_id: str):
    raise NotImplementedError


@app.get('/get_files')
async def get_files():
    raise NotImplementedError
