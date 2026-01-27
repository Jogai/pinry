![Pinstle Logo](https://www.whistlehog.com/pinstle-saver-ios/PinstleLogo@2x.png)

# Pinry (Pinstle Fork)

A tiling image board system for people who want to save, tag, and share images, videos and webpages in an easy to skim through format.

This is a heavily modified fork of [Pinry](https://github.com/pinry/pinry) with a modernized dark theme UI and various improvements.

**iOS App:** [Pinstle on the App Store](https://apps.apple.com/us/app/pinstle/id6754937420)
**Android App:** [Pinstle APK](https://github.com/sciamop/pinry-saver-android/releases/tag/v1.0.3)
**Firefox Extension:** [Pinry Saver](https://addons.mozilla.org/en-US/firefox/addon/pinry-saver/)

![Main View](https://pinry.whistlehog.com/media/7/4/740bf5af9ff48c417afae3dbbd7c374a/Screenshot_2026-01-27_main.jpg)

![Add Pin Modal](https://pinry.whistlehog.com/media/d/9/d939a14e530a492dc464a43e2f530e07/Screenshot_2026-01-27_155055.jpg)

## What's Different in This Fork

### Dark Theme UI Overhaul
- Complete dark theme redesign (#1a1a1a background, #2d2d2d surfaces)
- Hot pink accent color (#ff42ff) throughout
- Rubik font for headings, Open Sans for body text
- Fully rounded (pill-shaped) form inputs and buttons

### Redesigned Add Pin Modal
- Clean single-column layout
- Horizontal form fields with labels on the left
- Integrated board selection with tag-style input
- Private checkbox in header row
- Streamlined upload drop zone

### New Floating Action Button (FAB)
- Hot pink FAB in bottom-right corner for quick pin creation
- Animated logo icon on hover
- Auto-hides below modals

### Pin Preview Improvements
- Enhanced hover states and transitions
- Better image handling
- Improved edit/delete controls

### Security Fixes
- Various security hardening measures
- Updated dependencies

### Infrastructure
- Production-ready docker-compose.yml
- Updated Poetry dependencies
- Python 3.9-3.12 compatibility

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
