import cv2
from PIL import Image
from scipy.ndimage.filters import gaussian_filter
import numpy
import pytesseract
from PIL import ImageFilter
from os import remove
import requests

url = 'https://app1.susalud.gob.pe/registro/'


def make_request():
    s = requests.session()
    captcha_url = url + 'Home/GeneraCaptcha'
    get_img(s, captcha_url)
    txt_captcha = solve_captcha()
    petition(s, txt_captcha)


def petition(s, txt_captcha):
    post_data = {
        'cboPais': 'PER',
        'cboTDoc': '1',
        'txtNroDoc': '76738571',
        'txtCaptcha': '%s' % txt_captcha[:-2]
    }
    post_url = url + 'Home/ConsultaAfiliadoPersona'
    r = s.post(post_url, data=post_data)
    print(r.text)
    if 'El texto de la imagen es incorrecto, intente nuevamente' not in r.text and txt_captcha.strip():
        print('pasaste la prueba')
    else:
        print('vuelve a intentarlo')
        make_request()


def get_img(s, captcha_url):
    file_name = 'captcha.jpg'
    captcha = s.get(captcha_url)
    f = open(file_name, 'wb')
    f.write(captcha.content)
    f.close()


def solve_captcha():
    th1 = 140
    th2 = 140
    sig = 1.5

    original = Image.open("captcha.jpg")
    original.save("original.png")
    black_and_white = original.convert("L")
    black_and_white.save("black_and_white.png")
    first_threshold = black_and_white.point(lambda p: p > th1 and 255)
    first_threshold.save("first_threshold.png")
    blur = numpy.array(first_threshold)
    blurred = gaussian_filter(blur, sigma=sig)
    blurred = Image.fromarray(blurred)
    blurred.save("blurred.png")
    final = blurred.point(lambda p: p > th2 and 255)
    final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
    final = final.filter(ImageFilter.SHARPEN)
    final.save("final.png")

    img = cv2.imread("final.png")
    text = pytesseract.image_to_string(img)

    remove('original.png')
    remove('black_and_white.png')
    remove('first_threshold.png')
    remove('blurred.png')
    remove('final.png')
    print(text[:-2])
    return text


if __name__ == '__main__':
    make_request()

