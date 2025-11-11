import requests
urls=['http://127.0.0.1:8000/courses/','http://127.0.0.1:8000/results/','http://127.0.0.1:8000/lecturers/','http://127.0.0.1:8000/students/']
for u in urls:
    try:
        r=requests.get(u)
        print(u, r.status_code)
    except Exception as e:
        print(u, 'ERR', e)
