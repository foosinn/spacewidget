from flask import Flask, Response, render_template, send_file
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
from contextlib import contextmanager
from functools import wraps
import requests


URL = 'http://status.bckspc.de/spacestatus.php'
app = Flask(__name__)


def error_save_cache(maxsize=128, cache=None):
    sentinel = object()
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                cache = result
            except Exception:
                maxsize
                if cache:
                    result = cache
                else:
                    result = 'unknown', 0
            return result
        return wrapper
    return decorator



def tint(image: Image, color) -> Image:
    """Tint an image."""
    if color == 'open':
        color = (0, 255, 128)
    elif color == 'closed':
        color = (255, 0, 0)
    elif color == 'unknown':
        color = (255, 128, 0)

    _, _, _, alpha = image.split()
    image = ImageOps.grayscale(image)
    image = ImageOps.colorize(image, (0, 0, 0), (255, 255, 255), color)
    image.putalpha(alpha)
    return image


def addtext(image: Image, textlist: list, fontsize=10, offset=(8, 10)) -> Image:
    """Add text to an image."""
    draw = ImageDraw.Draw(image)
    x, y = image.size
    for i, text in enumerate(textlist):
        dy = (i - 1) * fontsize - (len(textlist) * fontsize) / 2
        tx, ty = draw.textsize(text)
        px, py = (x - tx) / 2 + offset[0], (y - ty) / 2 + dy + offset[1]
        draw.text((px, py), text)
    return image


def send_img(image: Image):
    """Flask response for image."""
    img_buffer = BytesIO()
    image.save(img_buffer, 'PNG')
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png')


@error_save_cache(maxsize=128)
def space_status():
    """Get space status."""
    req = requests.get(URL)
    req = req.json()
    status = 'open' if req['state']['open'] else 'closed'
    if not req['sensors']['people_now_present']:
        return 'closed', 0
    else:
        count = req['sensors']['people_now_present'][0]['value']
        return status, count


@app.route('/')
def index():
    image = Image.open('logo.png')
    status, count = space_status()
    textlist = ['Space is %s' % status, '%s members present' % count]
    image = addtext(image, textlist=textlist)
    image = tint(image, status)
    return send_img(image)

