import sys
import cloudscraper
import time
import random
import threading
import signal
import os
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import unquote
from flask import Flask, request, Response

CHROME_VERSIONS = [
    '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
    '"Not_A Brand";v="8", "Chromium";v="118", "Google Chrome";v="118"',
    '"Not_A Brand";v="99", "Chromium";v="116", "Google Chrome";v="116"',
    '"Not_A Brand";v="99", "Chromium";v="117", "Google Chrome";v="117"',
]

PLATFORMS = ['"Windows"', '"Windows NT"', '"macOS"', '"Linux"', '"Android"']

FETCH_MODES = ['cors', 'navigate', 'no-cors', 'same-origin']
FETCH_DESTS = ['empty', 'document', 'object', 'iframe', 'image']
FETCH_SITES = ['same-origin', 'same-site', 'cross-site', 'none']

ACCEPT_LANGUAGES = [
    'en-US,en;q=0.9', 
    'en-GB,en;q=0.9,en-US;q=0.8', 
    'en-CA,en;q=0.9,fr-CA;q=0.8',
    'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'de-DE,de;q=0.9,en;q=0.8',
    'fr-FR,fr;q=0.9,en;q=0.8',
    'es-ES,es;q=0.9,en;q=0.8'
]

ACCEPT_ENCODINGS = [
    'gzip, deflate, br',
    'br, gzip, deflate',
    'gzip, br, deflate'
]

# Health monitoring
last_successful_request = datetime.now()
health_check_interval = 60  # seconds
max_request_age = 300  # seconds (5 minutes without successful requests triggers restart)
health_monitor_running = True

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
    
    # Создаем разнообразные User-Agent
    platform = headers.get('Sec-Ch-Ua-Platform', '"Windows"').strip('"')
    
    if platform == 'Windows' or platform == 'Windows NT':
        os_version = random.choice(['10.0', '11.0'])
        headers['User-Agent'] = f'Mozilla/5.0 (Windows NT {os_version}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.{random.randint(0, 9999)}.{random.randint(0, 99)} Safari/537.36'
    elif platform == 'macOS':
        os_version = random.choice(['10_15_7', '11_2_3', '12_0_1', '13_1'])
        headers['User-Agent'] = f'Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.{random.randint(0, 9999)}.{random.randint(0, 99)} Safari/537.36'
    elif platform == 'Linux':
        headers['User-Agent'] = f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.{random.randint(0, 9999)}.{random.randint(0, 99)} Safari/537.36'
    elif platform == 'Android':
        android_version = random.choice(['10', '11', '12', '13'])
        device = random.choice(['SM-G970F', 'SM-G973F', 'Pixel 6', 'Pixel 7'])
        headers['User-Agent'] = f'Mozilla/5.0 (Linux; Android {android_version}; {device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.{random.randint(0, 9999)}.{random.randint(0, 99)} Mobile Safari/537.36'
    else:
        # Fallback
        headers['User-Agent'] = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.{random.randint(0, 9999)}.{random.randint(0, 99)} Safari/537.36'
    
    return headers


def set_security_headers(headers):
    headers['Sec-Ch-Ua'] = random.choice(CHROME_VERSIONS)
    headers['Sec-Ch-Ua-Mobile'] = random.choice(['?0', '?1']) if random.random() > 0.8 else '?0'
    headers['Sec-Ch-Ua-Platform'] = random.choice(PLATFORMS)
    headers['Sec-Fetch-Dest'] = random.choice(FETCH_DESTS)
    headers['Sec-Fetch-Mode'] = random.choice(FETCH_MODES)
    headers['Sec-Fetch-Site'] = random.choice(FETCH_SITES)
    
    # Случайно добавлять дополнительные заголовки
    if random.random() > 0.7:
        headers['Sec-Fetch-User'] = '?1'
    
    # Случайно варьировать порядок заголовков
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

def health_monitor():
    """Monitor application health and restart if necessary"""
    global health_monitor_running
    
    while health_monitor_running:
        time.sleep(health_check_interval)
        now = datetime.now()
        time_since_last_request = (now - last_successful_request).total_seconds()
        
        print(f"Health check: {time_since_last_request:.1f} seconds since last successful request", file=sys.stdout)
        
        if time_since_last_request > max_request_age:
            print(f"Application appears to be unresponsive for {time_since_last_request:.1f} seconds. Restarting...", file=sys.stderr)
            # Force restart by sending SIGTERM to self
            os.kill(os.getpid(), signal.SIGTERM)
            break


def get_headers():
    headers = {
        'Accept': random.choice([
            'application/json, text/plain, */*',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'application/json,text/html,application/xml;q=0.9,*/*;q=0.8'
        ]),
        'Accept-Language': random.choice(ACCEPT_LANGUAGES),
        'Accept-Encoding': random.choice(ACCEPT_ENCODINGS),
        'Connection': random.choice(['keep-alive', 'close']) if random.random() > 0.9 else 'keep-alive',
    }
    
    # Случайно добавлять Cache-Control
    if random.random() > 0.6:
        headers['Cache-Control'] = random.choice(['max-age=0', 'no-cache', 'no-store'])
    
    # Случайно добавлять DNT (Do Not Track)
    if random.random() > 0.7:
        headers['DNT'] = '1'
    
    # Случайно добавлять Pragma
    if random.random() > 0.8:
        headers['Pragma'] = 'no-cache'
        
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
    global last_successful_request
    
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
            # Добавить случайную задержку перед запросом
            if random.random() > 0.7:
                delay = random.uniform(0.1, 0.5)
                time.sleep(delay)
            
            start = time.time()
            
            # Случайно варьировать параметры запроса
            request_kwargs = {
                'headers': headers,
                'proxies': proxies,
                'allow_redirects': random.choice([True, False]) if random.random() > 0.9 else True,
                'timeout': random.uniform(10, 30)
            }
            
            response = scraper.get(full_url, **request_kwargs)
            
            end = time.time()
            elapsed = end - start
            
            # Update last successful request timestamp
            if response.status_code < 500:
                last_successful_request = datetime.now()
            
            print(f"Completed request to {full_url.split('?')[0]} - Status: {response.status_code} in {elapsed:.6f} seconds", file=sys.stdout)
            response.raise_for_status()

            return generate_proxy_response(response)

        except Exception as e:
            print(f"Failed request to {full_url.split('?')[0]} via {using_proxy} - Error: {str(e)}")
            return {'error': str(e), 'proxies': proxies }, 500


def signal_handler(sig, frame):
    global health_monitor_running
    print("Shutting down gracefully...")
    health_monitor_running = False
    sys.exit(0)

if __name__ == "__main__":
    print('Starting cloudflare bypass proxy server')
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start health monitoring in a separate thread
    health_thread = threading.Thread(target=health_monitor, daemon=True)
    health_thread.start()
    
    # Add a health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "ok", "last_successful_request": last_successful_request.isoformat()}, 200
    
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
