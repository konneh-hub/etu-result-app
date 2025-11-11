import urllib.request
import time

# Give server a moment to start
time.sleep(0.5)

urls = [
    'http://127.0.0.1:8000/',
    'http://127.0.0.1:8000/accounts/login/',
    'http://127.0.0.1:8000/dashboard/',
]

for u in urls:
    try:
        r = urllib.request.urlopen(u, timeout=5)
        print(f'{u} -> {r.getcode()}')
    except Exception as e:
        print(f'{u} -> ERROR: {e}')
