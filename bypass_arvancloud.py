import execjs
import requests

def get_cookie(html_text):
    start = 0
    end = len(html_text)
    start = html_text.find("var _0x4541")
    end = html_text.find("var hash = E(E(_0x2d84('0x1')));")
    html_text = html_text[start:end].strip().lower()
    ctx = execjs.compile(html_text)
    try:
        result = ctx.eval('_0x4541')
    except Exception as e:
        print("You must install nodejs in your system and add it yo your path")
    return result[1]

def get(url, timeout=15, headers={}, cookies={}):
    response = requests.get(url, timeout=15, headers=headers, cookies=cookies)
    # check if response is from  arvancloud protection layer then bypass it cookie 
    if 'arvancloud' in response.text:
        cookie = get_cookie(response.text)
        response = requests.get(url, timeout=15, headers=headers, cookies={'__arcsjs': cookie})
            
    return response