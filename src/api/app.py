import os
import random
import string
import traceback

import aiofiles
from sanic import Sanic, json
from sanic.exceptions import NotFound
from sanic.request import File, Request
from sanic.response import file as response_file
from werkzeug.utils import secure_filename

from . import config

app = Sanic(__name__)


async def write(file: File, path: str):
    async with aiofiles.open(path, 'wb') as f:
        await f.write(file.body)

    await f.close()


def is_valid(file) -> bool:
    return len(file.body) < config.FILE_MAX_SIZE \
           and secure_filename(file.name).endswith(config.FILE_EXTENSION) and file.type == config.FILE_TYPE


def random_filename() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + config.FILE_EXTENSION


@app.post('/upload')
async def upload(request: Request):
    api_key: str = request.form.get('api_key', '')
    image: File = request.files.get('image', None)

    if api_key != config.API_KEY:
        return json(dict(ok=False, reason='api-key', message='Invalid API Key.'), status=403)

    if not image:
        return json(dict(ok=False, reason='file', message='Invalid file.'), status=400)

    if not is_valid(image):
        return json(dict(ok=False, reason='file', message='Invalid file.'), status=400)

    filename = random_filename()
    path = os.path.join(config.UPLOAD_FOLDER, filename)

    await write(image, path)

    return json(dict(ok=True, url=config.DOMAIN + '/' + os.path.splitext(filename)[0]))


@app.get('/<filename>')
async def fetch(request, filename: str):
    filename = secure_filename(filename)

    if not filename.endswith(config.FILE_EXTENSION):
        filename += config.FILE_EXTENSION

    path = os.path.join(config.UPLOAD_FOLDER, filename)

    if not os.path.isfile(path):
        raise NotFound(message='Image not found.')

    return await response_file(location=path, mime_type=config.FILE_TYPE)


@app.exception(NotFound)
async def not_found(request, exc):
    return json(dict(ok=False, reason='not_found', message='404 Not Found'), status=404)


@app.exception(Exception)
async def exception(request, exc):
    traceback.print_exc()
    return json(dict(ok=False, reason='exception', message='Internal Server Error'), status=500)


def run():
    app.run(host='0.0.0.0')
