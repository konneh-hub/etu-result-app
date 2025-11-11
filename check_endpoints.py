#!/usr/bin/env python
import requests
from urllib.parse import urljoin
import sys

BASE_URL = 'http://127.0.0.1:8000'
PATHS = [
    '/',
    '/register/student/',
    '/register/lecturer/',
    '/register/admin/',
    '/dashboard/'
]

def check_url(url):
    try:
        r = requests.get(url, allow_redirects=True)
        status = r.status_code
        if status == 200:
            print(f"✓ {url} -> {status}")
        else:
            print(f"✗ {url} -> {status}")
        return status == 200
    except Exception as e:
        print(f"✗ {url} -> Error: {e}")
        return False

def main():
    results = []
    for path in PATHS:
        url = urljoin(BASE_URL, path)
        results.append(check_url(url))
    
    if all(results):
        print("\nAll endpoints respond OK")
        sys.exit(0)
    else:
        print("\nSome endpoints failed")
        sys.exit(1)

if __name__ == '__main__':
    main()