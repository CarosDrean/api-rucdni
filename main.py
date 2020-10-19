import cv2
import requests
import numpy
import pytesseract
from PIL import Image
from scipy.ndimage.filters import gaussian_filter
from PIL import ImageFilter
from os import remove
from bs4 import BeautifulSoup

url = 'https://app1.susalud.gob.pe/registro/'
url_sunat = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/'


def test():
    s = requests.session()
    r = s.get('https://logincovid19.minsa.gob.pe/accounts/login/')
    c = r.cookies.get_dict()
    print(c)
    headers = {'X-CSRFToken': '%s' % c['csrftoken']}
    data = {
        'username': '22102135',
        'password': 'HOLO2020'
    }
    r = s.post('https://logincovid19.minsa.gob.pe/accounts/login/', data=data, headers=headers)
    print(r.cookies.get_dict())
    r = s.get('https://siscovid.minsa.gob.pe/static/js/paciente/buscar.js')
    r = s.get('https://siscovid.minsa.gob.pe/crear/?tipo=01&numero=76738571')
    print(r.text)


def make_request():
    s = requests.session()
    captcha_url = url + 'Home/GeneraCaptcha'
    get_img(s, captcha_url)
    txt_captcha = solve_captcha()
    petition(s, txt_captcha)


def make_request_sunat():
    s = requests.session()
    captcha_url = url_sunat + 'captcha?accion=image&nmagic=9578'
    get_img(s, captcha_url)
    txt_captcha = solve_captcha()
    petition_sunat(s, txt_captcha)


def petition_sunat(s, txt_captcha):
    post_data = {
        'accion': 'consPorRuc',
        'nroRuc': '20606100362',
        'contexto': 'ti-it',
        'modo': '1',
        'rbtnTipo': '1',
        'search1': '20606100362',
        'tipdoc': '1',
        'codigo': '%s' % txt_captcha[:-2]
    }
    post_url = url_sunat + 'jcrS03Alias'
    r = s.post(post_url, data=post_data)
    if 'Surgieron problemas al procesar la consulta por número de ruc.' not in r.text and txt_captcha.strip():
        print('Data obtenida:')
        print(r.text)
    else:
        print('Volviendo a intentar...')


def petition(s, txt_captcha):
    post_data = {
        'cboPais': 'PER',
        'cboTDoc': '1',
        'txtNroDoc': '76738571',
        'txtCaptcha': '%s' % txt_captcha[:-2]
    }
    post_url = url + 'Home/ConsultaAfiliadoPersona'
    r = s.post(post_url, data=post_data)
    if 'El texto de la imagen es incorrecto, intente nuevamente' not in r.text and txt_captcha.strip():
        print('Data obtenida:')
        scrapping_data(r)
    else:
        print('Volviendo a intentar...')
        make_request()


def scrapping_data(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    data = list(soup.children)[0].get_text()
    data_array = data.split(':')
    name = data_array[1][1:]
    print(name)


def get_img(s, captcha_url):
    file_name = 'captcha.jpg'
    # aqui necesitamos cookies o por los parametros quiza requiere algo mas
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
    print(text)
    return text


if __name__ == '__main__':
    test()
    # make_request_sunat()

