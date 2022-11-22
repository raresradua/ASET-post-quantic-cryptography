from fastapi import FastAPI, Request, HTTPException, APIRouter, Depends
from mongo.mongo import Mongo
from base64 import b64encode, b64decode
from utilities.utilities import logged
from auth.auth_handler import signJWT, decodeJWT
from auth.auth_bearer import JWTBearer
from passlib.hash import sha256_crypt

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
        collection.insert_one({'username': username, 'password': sha256_crypt.encrypt(password), 'token': b64encode(bytes(username + 'DDD' + password, 'utf-8'))})
    else:
        return {
            'detail': 'user already exists'
        }
    return {
        'token': b64encode(bytes(username + 'DDD' + password, 'utf-8'))
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
    if not payload.get('cryptosystem'):
        return {
            'detail': 'You must choose either "reed" or "goppa"'
        }
    user = decodeJWT(request.headers.get('Authorization').split(' ')[1])
    if not user:
        return {
            'detail': 'Invalid token.'
        }
    pub, prv = 'public_key', 'private_key'
    mongo.get_collection().update_one({'username': user['username']}, {"$set": {payload.get('cryptosystem'): {'pub': pub, 'prv': prv}}})
    return {
        'public_key': pub,
        'private_key': prv,
        'cryptosystem': payload.get('cryptosystem'),
        'message': 'public_key and private_key to encrypt and decrypt information'
    }


@app.post('/profile')
@logged
async def profile(request: Request):
    headers = request.headers.get('Authorization')
    user = decodeJWT(headers.split(' ')[1])
    collection = mongo.get_collection()
    return collection.find_one({'username': user['username']}, {'_id': 0})

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
