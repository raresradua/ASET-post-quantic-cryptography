from fastapi import FastAPI
from proj.mongo.mongo import Mongo

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


@app.post('/auth')
async def auth():
    raise NotImplementedError


@app.post('/upload')
async def upload_file():
    raise NotImplementedError


@app.post('/encrypt')
async def encrypt():
    raise NotImplementedError


@app.post('/decrypt')
async def decrypt():
    raise NotImplementedError


@app.get('/get_file/{file_id}')
async def get_file(file_id: str):
    raise NotImplementedError


@app.get('/get_files')
async def get_files():
    raise NotImplementedError
