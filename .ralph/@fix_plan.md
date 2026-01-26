# Pinry Modernization Fix Plan

## Executive Summary

Pinry is a Pinterest-like image bookmarking application that is approximately a decade out of date. This plan addresses security vulnerabilities, outdated dependencies, and modernization requirements while maintaining the application's core identity.

**Current Stack:**
- Backend: Django 2.2.28 (EOL April 2022), Python 3.7+
- Frontend: Vue 2.6.14 (EOL December 2026), Vue CLI 4, Webpack 4
- Database: SQLite (default), PostgreSQL supported

**Target Stack:**
- Backend: Django 4.2 LTS (supported until April 2026)
- Frontend: Vue 3.5.x with Composition API, Vite
- Maintain existing database compatibility

---

## Critical Priority (Security - Immediate)

### CRIT-01: Fix ALLOWED_HOSTS Configuration
- **Status**: [x] COMPLETED
- **Files**: `pinry/settings/docker.py`, `pinry/settings/development.py`, `pinry/settings/local_settings.example.py`
- **Issue**: `ALLOWED_HOSTS = ['*']` allows Host Header Injection attacks
- **Fix**: Configure with actual domain names only
- **Risk**: CVE-level vulnerability

### CRIT-02: Secure SECRET_KEY Management
- **Status**: [x] COMPLETED
- **Files**: `pinry/settings/docker.py`, `pinry/settings/development.py`
- **Issue**: Placeholder secrets like `"PLEASE_REPLACE_ME"` and `"REPLACE-ME"`
- **Fix**: Require strong random keys from environment variables, fail if not set
- **Risk**: Session hijacking, CSRF token forgery, authentication bypass

### CRIT-03: Fix SSRF Vulnerability in Image Downloads
- **Status**: [x] COMPLETED
- **Files**: `core/models.py` (lines 37-54)
- **Issue**: `create_for_url()` accepts arbitrary URLs without validation
- **Fix**:
  - Add request timeout (10 seconds)
  - Add response size limit (10MB)
  - Block private IP ranges (10.x, 172.16.x, 192.168.x, 127.x, 169.254.x)
  - Validate URL scheme (http/https only)
- **Risk**: Server-Side Request Forgery, DoS, internal network access

### CRIT-04: Upgrade Vulnerable Dependencies
- **Status**: [x] COMPLETED
- **Files**: `pyproject.toml`, `pinry-spa/package.json`
- **Issue**: Known CVEs in current dependencies
- **Packages**:
  - [x] requests ^2.31.0 (includes urllib3 fix for CVE-2023-32681)
  - [x] Pillow >=10.0.0 (fixes multiple CVEs including buffer overflow)
  - [x] axios ^1.6.0 (multiple CVEs fixed, updated axios.all to Promise.all)
- **Risk**: RCE via crafted images, MITM attacks, request injection

### CRIT-05: Fix XSS Vulnerability via v-html
- **Status**: [x] COMPLETED (Added DOMPurify sanitization)
- **Files**: `pinry-spa/src/components/PinPreview.vue`, `pinry-spa/src/components/Pins.vue`, `pinry-spa/src/components/pin_edit/PinCreateModal.vue`
- **Issue**: User descriptions rendered via `v-html` with weak escaping
- **Fix**:
  - Add DOMPurify for HTML sanitization
  - Or replace v-html with text-only rendering
- **Risk**: Stored XSS, session theft, malware distribution

---

## High Priority (Security & Compatibility)

### HIGH-01: Add HTTP Security Headers
- **Status**: [x] COMPLETED
- **Files**: `pinry/settings/base.py`
- **Issue**: Missing security headers
- **Fix**: Add configuration:
  ```python
  SECURE_HSTS_SECONDS = 31536000
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_SSL_REDIRECT = True  # production only
  X_FRAME_OPTIONS = 'DENY'
  SECURE_CONTENT_TYPE_NOSNIFF = True
  ```

### HIGH-02: Configure Secure Cookie Settings
- **Status**: [x] COMPLETED
- **Files**: `pinry/settings/base.py`
- **Issue**: Session cookies not secured
- **Fix**: Add configuration:
  ```python
  SESSION_COOKIE_SECURE = True  # production
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SAMESITE = 'Strict'
  CSRF_COOKIE_SECURE = True  # production
  CSRF_COOKIE_HTTPONLY = True
  ```

### HIGH-03: Strengthen Password Requirements
- **Status**: [x] COMPLETED (min_length=12, no max_length)
- **Files**: `users/serializers.py` (lines 42-48)
- **Issue**: Minimum password length of 6 characters, max 32
- **Fix**: Change to min_length=12, remove max_length restriction

### HIGH-04: Add Rate Limiting to Authentication
- **Status**: [x] COMPLETED
- **Files**: `users/views.py`, `pyproject.toml`, `pinry/settings/base.py`
- **Issue**: No rate limiting on login/logout endpoints
- **Fix**: Added django-ratelimit, login limited to 5 attempts per minute per IP

### HIGH-05: Replace Deprecated Django URL Patterns
- **Status**: [x] COMPLETED
- **Files**: `users/urls.py`, all URL configuration files
- **Issue**: Using deprecated `url()` with regex patterns (removed in Django 4.0)
- **Fix**: Replace with `path()` and `re_path()` from `django.urls`

### HIGH-06: Fix Deprecated Authentication Check
- **Status**: [x] COMPLETED
- **Files**: `core/permissions.py`
- **Issue**: `request.user.is_authenticated()` called as method (deprecated)
- **Fix**: Change to `request.user.is_authenticated` (property)

### HIGH-07: Replace Deprecated Form Fields
- **Status**: [x] COMPLETED
- **Files**: `users/forms.py`
- **Issue**: Using deprecated `RegexField`
- **Fix**: Use `CharField` with `validators` parameter

### HIGH-08: Update Translation Imports
- **Status**: [x] COMPLETED
- **Files**: `users/forms.py`
- **Issue**: `ugettext_lazy` deprecated since Django 3.0
- **Fix**: Replace with `gettext_lazy`

### HIGH-09: Replace babel-eslint (Deprecated)
- **Status**: [ ] Not Started
- **Files**: `pinry-spa/.eslintrc.js`, `pinry-spa/package.json`
- **Issue**: babel-eslint is deprecated and unmaintained
- **Fix**: Replace with `@babel/eslint-parser`

### HIGH-10: Fix Node.js OpenSSL Compatibility
- **Status**: [ ] Not Started
- **Files**: `pinry-spa/package.json`
- **Issue**: Build scripts use `NODE_OPTIONS=--openssl-legacy-provider` workaround
- **Fix**: Upgrade build tooling to be compatible with Node 18+ natively

---

## Medium Priority (Modernization)

### MED-01: Upgrade Django 2.2 → 4.2 LTS
- **Status**: [ ] Not Started
- **Files**: `pyproject.toml`, all Python files
- **Issue**: Django 2.2 EOL was April 2022
- **Breaking Changes**:
  - [ ] URL patterns: `url()` → `path()`/`re_path()`
  - [ ] `is_authenticated()` → `is_authenticated`
  - [ ] Model Meta: `index_together` → `indexes`
  - [ ] Forms: `RegexField` → `CharField` + validators
  - [ ] Translations: `ugettext_lazy` → `gettext_lazy`
- **Migration Path**: Django 2.2 → 3.2 → 4.2 (incremental)

### MED-02: Update Django REST Framework
- **Status**: [ ] Not Started
- **Files**: `pyproject.toml`, `pinry/settings/base.py`
- **Issue**: DRF 3.13.1 uses deprecated CoreAPI schemas
- **Fix**:
  - Upgrade to DRF 3.14+
  - Replace `coreapi.AutoSchema` with `openapi.AutoSchema`
  - Update `filter_fields` to `filterset_fields`

### MED-03: Update Model Meta Options
- **Status**: [x] COMPLETED
- **Files**: `core/models.py`
- **Issue**: `index_together` deprecated in Django 3.2
- **Fix**: Replace with `indexes` parameter using `Index` objects

### MED-04: Fix Model __unicode__ Methods
- **Status**: [x] COMPLETED
- **Files**: `core/models.py`
- **Issue**: `__unicode__` is Python 2 style
- **Fix**: Rename to `__str__`

### MED-05: Replace MD5 with SHA-256
- **Status**: [x] COMPLETED
- **Files**: `core/utils.py`, `django_images/models.py`
- **Issue**: MD5 used for image path hashing (cryptographically weak)
- **Fix**: Replaced with SHA-256. New uploads use 'by-sha256' prefix; existing files unaffected
- **Note**: Gravatar uses MD5 by their API spec - this is standard and unchanged

### MED-06: Plan Vue 2 → Vue 3 Migration
- **Status**: [ ] Not Started
- **Files**: All `pinry-spa/` files
- **Issue**: Vue 2.6 approaching EOL (December 2026)
- **Scope**:
  - [ ] Upgrade vue 2.6 → 3.5
  - [ ] Upgrade vue-router 3.5 → 4.x
  - [ ] Upgrade vue-i18n 8.x → 11.x
  - [ ] Migrate Options API → Composition API
  - [ ] Replace Event Bus with Pinia

### MED-07: Replace Event Bus Anti-pattern
- **Status**: [ ] Not Started
- **Files**: `pinry-spa/src/components/utils/bus.js`, components using it
- **Issue**: Event Bus is deprecated pattern, doesn't work in Vue 3
- **Fix**: Replace with Pinia state management

### MED-08: Migrate Vue CLI/Webpack → Vite
- **Status**: [ ] Not Started
- **Files**: `pinry-spa/` build configuration
- **Issue**: Vue CLI 4 with Webpack 4 is outdated and slow
- **Fix**: Migrate to Vite for faster builds and better DX

### MED-09: Replace Buefy UI Framework
- **Status**: [ ] Not Started
- **Files**: All Vue components using Buefy
- **Issue**: Buefy is unmaintained, not Vue 3 compatible
- **Options**:
  - [ ] PrimeVue (full-featured)
  - [ ] Headless UI + Tailwind (flexible)
  - [ ] Element Plus (similar to Buefy)

### MED-10: Add Route Lazy Loading
- **Status**: [ ] Not Started
- **Files**: `pinry-spa/src/router/index.js`
- **Issue**: All routes eagerly loaded, large initial bundle
- **Fix**: Use dynamic imports for route components

### MED-11: Update Dockerfile Base Image
- **Status**: [ ] Not Started (Still uses python:3.7-stretch)
- **Files**: `Dockerfile`
- **Issue**: Uses `python:3.7-stretch` (2017 base image)
- **Fix**: Update to `python:3.11-slim-bookworm` or similar
- **Note**: pyproject.toml updated to support Python >=3.9,<3.13

### MED-12: Add Query Optimization
- **Status**: [ ] Not Started
- **Files**: `core/views.py`, ViewSets
- **Issue**: Missing `prefetch_related`/`select_related` causing N+1 queries
- **Fix**: Add proper query optimization to ViewSets

---

## Low Priority (Cleanup & Enhancement)

### LOW-01: Pin All Wildcard Dependencies
- **Status**: [ ] Not Started
- **Files**: `pyproject.toml`
- **Issue**: Unpinned dependencies (markdown, flake8, mkdocs)
- **Fix**: Pin to specific versions for reproducible builds

### LOW-02: Update Black Formatter
- **Status**: [x] COMPLETED
- **Files**: `pyproject.toml`
- **Issue**: black 19.10b0 is from 2019
- **Fix**: Updated to ">=23.0.0"

### LOW-03: Upgrade ESLint
- **Status**: [ ] Not Started
- **Files**: `pinry-spa/package.json`, `pinry-spa/.eslintrc.js`
- **Issue**: ESLint 5.16.0 is severely outdated (current is 9.x)
- **Fix**: Upgrade to ESLint 9.x with flat config

### LOW-04: Replace Promise Chains with async/await
- **Status**: [ ] Not Started
- **Files**: `pinry-spa/src/components/api.js`, other JS files
- **Issue**: Nested `.then()` chains are verbose and hard to read
- **Fix**: Refactor to async/await pattern

### LOW-05: Add Error Handling for localStorage
- **Status**: [ ] Not Started
- **Files**: `pinry-spa/src/components/utils/storage.js`
- **Issue**: `JSON.parse()` without try-catch for corrupted data
- **Fix**: Wrap in try-catch block

### LOW-06: Remove Console Logging in Production
- **Status**: [ ] Not Started
- **Files**: Various frontend files (12 instances)
- **Issue**: `console.log()` statements may leak sensitive data
- **Fix**: Remove or replace with proper logging

### LOW-07: Update User-Agent String
- **Status**: [x] COMPLETED (Updated to Chrome 120)
- **Files**: `core/models.py` (lines 18-22)
- **Issue**: Hardcoded outdated Chrome User-Agent from 2016
- **Fix**: Use more generic or current User-Agent

### LOW-08: Enhance SECURITY.md
- **Status**: [ ] Not Started
- **Files**: `SECURITY.md`
- **Issue**: Minimal content, missing disclosure policy details
- **Fix**: Add PGP key, timeline, supported versions, full policy

### LOW-09: Add Email Verification
- **Status**: [ ] Not Started
- **Files**: `users/` app
- **Issue**: No email verification in registration flow
- **Fix**: Implement email verification step

### LOW-10: Consider TypeScript Migration
- **Status**: [ ] Not Started
- **Files**: All frontend `.js` and `.vue` files
- **Issue**: No type safety in frontend code
- **Fix**: Gradual migration to TypeScript

---

## Migration Strategy

### Phase 1: Critical Security (Week 1-2)
1. Fix ALLOWED_HOSTS configuration
2. Secure SECRET_KEY management
3. Fix SSRF vulnerability
4. Upgrade vulnerable dependencies (urllib3, Pillow, axios)
5. Add DOMPurify for XSS protection

### Phase 2: Security Hardening (Week 3-4)
1. Add HTTP security headers
2. Configure secure cookies
3. Strengthen password requirements
4. Add rate limiting
5. Replace deprecated authentication checks

### Phase 3: Django Upgrade (Week 5-8)
1. Fix all deprecated patterns (URLs, forms, translations)
2. Upgrade Django 2.2 → 3.2
3. Test thoroughly
4. Upgrade Django 3.2 → 4.2
5. Update DRF and related packages

### Phase 4: Frontend Modernization (Week 9-16)
1. Upgrade axios and other dependencies
2. Replace babel-eslint
3. Fix OpenSSL compatibility
4. Plan and execute Vue 2 → Vue 3 migration
5. Replace Buefy with Vue 3-compatible UI framework
6. Migrate to Vite build system

### Phase 5: Cleanup & Optimization (Ongoing)
1. Query optimization
2. Code cleanup
3. TypeScript migration (optional)
4. Documentation updates

---

## Dependency Upgrade Matrix

### Backend (Python)

| Package | Current | Target | Priority |
|---------|---------|--------|----------|
| Django | 2.2.28 | 4.2.x | CRITICAL |
| DRF | 3.13.1 | 3.14+ | MEDIUM |
| Pillow | 9.1.1 | 11.x | CRITICAL |
| urllib3 | 1.22 | 2.x | CRITICAL |
| requests | 2.27.1 | 2.32+ | HIGH |
| psycopg2-binary | 2.9.9 ✓ | 2.9+ | COMPLETED |
| django-filter | 2.4.0 | 24.x | MEDIUM |
| django-taggit | 1.3.0 | 6.x | MEDIUM |
| black | >=23.0.0 ✓ | 24.x | COMPLETED |

### Frontend (Node.js)

| Package | Current | Target | Priority |
|---------|---------|--------|----------|
| vue | 2.6.14 | 3.5.x | MEDIUM |
| vue-router | 3.5.3 | 4.6.x | MEDIUM |
| vue-i18n | 8.27.1 | 11.x | MEDIUM |
| axios | 0.21.4 | 1.13.x | CRITICAL |
| eslint | 5.16.0 | 9.x | HIGH |
| sass-loader | 8.0.2 | 14.x | MEDIUM |
| bulma | 0.7.5 | 1.0.x | LOW |
| buefy | 0.8.20 | Replace | MEDIUM |

---

## Notes

- All security fixes should be completed before any feature work
- Django upgrade should be incremental (2.2 → 3.2 → 4.2)
- Vue 3 migration is significant effort; consider parallel operation during transition
- Maintain backward compatibility with existing user data
- Test thoroughly at each migration step
