# pinry

A tiling image board system for people who want to save, tag, and share images, videos and webpages in an easy to skim through format.

## Development Setup

### Requirements

- Python 3.9-3.12
- NodeJS 18
- pnpm

### Option 1: Poetry (Recommended)

```bash
# If you get keyring errors, set this env var:
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

poetry install
```

### Option 2: venv

```bash
# Create venv
python3 -m venv .venv
.venv/bin/pip install --upgrade pip

# Install dependencies
.venv/bin/pip install 'requests>=2.27.1' 'django>2.2.17,<3' 'pillow>=8.1.1' markdown \
  'django-filter==2.4.0' 'coreapi>=2.3.3' 'psycopg2-binary==2.9.9' 'django-taggit==1.3.0' \
  'django-braces>=1.15.0' 'django-compressor>=4.0' 'mock>=4.0.3' 'gunicorn>=20.1.0' \
  'djangorestframework>=3.13.1' setuptools 'django-extensions<4'
```

### Frontend

```bash
cd pinry-spa
pnpm install
```

### Running the Development Server

Backend (Poetry):
```bash
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Backend (venv):
```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Frontend:
```bash
cd pinry-spa
pnpm serve
```

## Python 3.12 Compatibility Notes

- Django 2.2.x requires `setuptools` package for the `distutils` module (removed in Python 3.12)
- `django-extensions` must be <4.0 to maintain Django 2.2 compatibility
- `coreapi` shows a pkg_resources deprecation warning (harmless, can be ignored)
