# Eastern Technical University — Student Results

This is a small Django app to manage student results for Eastern Technical University.

Quick start (Windows, PowerShell):

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (Django 5.x used in this project):

```powershell
pip install -r requirements.txt
```

If `requirements.txt` is not present, install Django directly:

```powershell
pip install django
```

3. Run migrations and create a superuser (an `admin` user was already created programmatically in `scripts/create_admin.py` but you can create your own):

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4. Start the development server:

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ to view the student list. Admin is at http://127.0.0.1:8000/admin/.

Running tests

```powershell
python manage.py test
```

Notes

- Static files are loaded from CDN (Bootstrap). Local CSS is in `eturesultapp/static/eturesultapp/css/site.css`.
- To update branding, replace the text/logo in `eturesultapp/templates/eturesultapp/base.html` and add a logo under `static/eturesultapp/img/`.

If you want I can:
- Add a `requirements.txt`, CI, or Dockerfile
- Improve styling/colors/logo to match ETU
- Add REST API endpoints with Django REST Framework

