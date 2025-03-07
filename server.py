import sys
import cloudscraper
import time
import random
from pathlib import Path
from urllib.parse import unquote
from flask import Flask, request, Response

CHROME_VERSIONS = [
    '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
    '"Not_A Brand";v="8", "Chromium";v="118", "Google Chrome";v="118"',
]

PLATFORMS = ['"Windows"', '"Windows NT"', '"macOS"']

FETCH_MODES = ['cors', 'navigate', 'no-cors']
FETCH_DESTS = ['empty', 'document', 'object']

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    },
    delay=1,
    allow_brotli=True
)

def load_proxies():
    proxy_file = Path("var/proxies.txt")
    if not proxy_file.exists():
        print("Warning: var/proxies.txt not found")
        return []
        
    proxies = []
    with open(proxy_file, "r", encoding="utf-8-sig") as f:  # Use utf-8-sig to automatically handle BOM
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Remove any BOM character if present
            line = line.lstrip('\ufeff')
                
            # Проверяем, содержит ли строка формат логин:пароль@IP:порт
            if '@' in line:
                # Уже в правильном формате для requests
                proxies.append(f"http://{line}")
            else:
                # Старый формат (только IP:порт)
                proxies.append(f"http://{line}")
    
    return proxies

PROXY_LIST = load_proxies()


def set_user_agent(headers):
    chrome_version = headers.get('Sec-Ch-Ua', CHROME_VERSIONS[0])
    version = chrome_version.split('Chrome";v="')[1].split('"')[0]
    headers['User-Agent'] = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36'
    return headers


def set_security_headers(headers):
    headers['Sec-Ch-Ua'] = random.choice(CHROME_VERSIONS)
    headers['Sec-Ch-Ua-Mobile'] = '?0'
    headers['Sec-Ch-Ua-Platform'] = random.choice(PLATFORMS)
    headers['Sec-Fetch-Dest'] = random.choice(FETCH_DESTS)
    headers['Sec-Fetch-Mode'] = random.choice(FETCH_MODES)
    headers['Sec-Fetch-Site'] = 'same-origin'
    return headers


def set_origin_and_ref(headers, origin, ref):
    headers['Origin'] = origin
    headers['Referer'] = ref
    return headers


def generate_origin_and_ref(url, headers):
    data = url.split('/')
    first = data[0]
    base = data[2]
    c_url = f"{first}//{base}/"
    headers = set_origin_and_ref(headers, c_url, c_url)
    return headers


app = Flask(__name__)

HOP_BY_HOP_HEADERS = {
    'connection',
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailers',
    'transfer-encoding',
    'upgrade',
}


def clean_headers(response):
    headers = {}
    for name, value in response.headers.items():
        if name.lower() not in HOP_BY_HOP_HEADERS:
            headers[name] = value
    headers.pop('content-encoding', None)
    headers.pop('content-length', None)
    return headers


def generate_proxy_response(response) -> Response:
    content_type = response.headers.get('content-type', '')

    if 'text' in content_type or 'html' in content_type:
        # Явно указываем кодировку UTF-8 для текстового содержимого
        content = response.content.decode('utf-8', errors='replace')
    else:
        content = response.content

    headers = clean_headers(response)

    # For JSON content
    if 'application/json' in content_type:
        return Response(content, status=response.status_code, content_type='application/json; charset=utf-8')

    # For HTML content
    if 'text/html' in content_type:
        return Response(content, status=response.status_code, content_type='text/html; charset=utf-8')

    # For all other content types
    return Response(
        content,
        status=response.status_code,
        headers=headers
    )


def get_headers():
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    headers = set_security_headers(headers)  # First set security headers
    headers = set_user_agent(headers)        # Then set user agent to match
    return headers


def get_proxy_request_url(req, url):
    full_url = unquote(url.strip('"'))
    # Add http:// protocol if it's missing
    if not full_url.startswith(('http://', 'https://')):
        full_url = 'http://' + full_url
    
    if req.query_string:
        full_url = f"{full_url}?{req.query_string.decode('utf-8')}"
    return full_url


def get_proxy_request_headers(req, url):
    # Start with our base headers
    headers = get_headers()
    # Always use gzip encoding
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    # Generate origin and referer
    headers = generate_origin_and_ref(url, headers)
    return headers


# Cloudflare bypassed request
@app.route("/api/proxy/<path:url>", methods=["GET"])
def handle_proxy(url):
    if request.method == 'GET':
        full_url = get_proxy_request_url(request, url)
        headers = get_proxy_request_headers(request, url)
        
        # Выбираем прокси заранее для логирования
        proxies = None
        using_proxy = "direct connection"
        if PROXY_LIST:
            proxy = random.choice(PROXY_LIST)
            print(proxy, file=sys.stdout)
            proxies = {
                'http': proxy,
                'https': proxy
            }
            using_proxy = proxy

        print(f"Starting request to: {full_url.split('?')[0]} via {using_proxy}", file=sys.stdout)
        
        try:
            start = time.time()
            response = scraper.get(full_url, headers=headers, proxies=proxies)
            end = time.time()
            elapsed = end - start
            
            print(f"Completed request to {full_url.split('?')[0]} - Status: {response.status_code} in {elapsed:.6f} seconds", file=sys.stdout)
            response.raise_for_status()

            return generate_proxy_response(response)

        except Exception as e:
            print(f"Failed request to {full_url.split('?')[0]} via {using_proxy} - Error: {str(e)}")
            return {'error': str(e), 'proxies': proxies }, 500


if __name__ == "__main__":
    print('Starting cloudflare bypass proxy server')
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
