# Agent Build Instructions

## Project Overview

Pinry is a Pinterest-like image bookmarking application with:
- **Backend**: Python/Django
- **Frontend**: Vue.js SPA (pinry-spa)

## Requirements

- Python 3.9-3.12 (tested on 3.12)
- NodeJS 18
- Poetry or venv (Python package manager)
- pnpm (Node package manager)

## Project Setup

### Option 1: Poetry (Recommended)

```bash
cd pinry

# If you get keyring errors, set this env var:
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

poetry install
```

### Option 2: venv (Alternative)

```bash
cd pinry

# Create and set up venv
python3 -m venv .venv
.venv/bin/pip install --upgrade pip

# Install dependencies
.venv/bin/pip install 'requests>=2.27.1' 'django>2.2.17,<3' 'pillow>=8.1.1' markdown \
  'django-filter==2.4.0' 'coreapi>=2.3.3' 'psycopg2-binary==2.9.9' 'django-taggit==1.3.0' \
  'django-braces>=1.15.0' 'django-compressor>=4.0' 'mock>=4.0.3' 'gunicorn>=20.1.0' \
  'djangorestframework>=3.13.1' setuptools 'django-extensions<4'
```

### Frontend Dependencies
```bash
cd pinry-spa
pnpm install
```

**Python 3.12 Compatibility Notes**:
- Django 2.2.x requires `setuptools` for `distutils` module (removed in Python 3.12)
- `django-extensions` must be <4.0 to maintain Django 2.2 compatibility
- `coreapi` shows pkg_resources deprecation warning (harmless)
- Chinese mirror (tuna) removed from pyproject.toml - was causing Poetry lock failures

## Development Server

You need to run both the backend and frontend servers:

### Backend (Terminal 1)

With Poetry:
```bash
poetry run python manage.py migrate
poetry run python manage.py runserver
```

With venv:
```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

### Frontend (Terminal 2)
```bash
cd pinry-spa
pnpm serve
```

## Running Tests
```bash
# With Poetry
poetry run python manage.py test

# With venv
.venv/bin/python manage.py test
```

## Build Commands

### Frontend Production Build
```bash
cd pinry-spa
pnpm build
```

### Lint Frontend
```bash
cd pinry-spa
pnpm lint
```

## Configuration

- Custom settings: Add `local_settings.py` in `pinry/settings/` to customize settings
- Enable signups: Set `ALLOW_NEW_REGISTRATIONS = True` in local_settings.py

## Key Learnings
- Backend and frontend run as separate services during development
- Poetry or venv can manage Python dependencies; pnpm manages Node dependencies
- Frontend dev server proxies API requests to backend on port 8000
- Django 2.2.x requires setuptools for distutils on Python 3.12
- Poetry may need `PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring` to avoid keyring errors

## Feature Development Quality Standards

**CRITICAL**: All new features MUST meet the following mandatory requirements before being considered complete.

### Testing Requirements

- **Minimum Coverage**: 85% code coverage ratio required for all new code
- **Test Pass Rate**: 100% - all tests must pass, no exceptions
- **Test Types Required**:
  - Unit tests for all business logic and services
  - Integration tests for API endpoints or main functionality
  - End-to-end tests for critical user workflows
- **Coverage Validation**: Run coverage reports before marking features complete:
  ```bash
  # Examples by language/framework
  npm run test:coverage
  pytest --cov=src tests/ --cov-report=term-missing
  cargo tarpaulin --out Html
  ```
- **Test Quality**: Tests must validate behavior, not just achieve coverage metrics
- **Test Documentation**: Complex test scenarios must include comments explaining the test strategy

### Git Workflow Requirements

Before moving to the next feature, ALL changes must be:

1. **Committed with Clear Messages**:
   ```bash
   git add .
   git commit -m "feat(module): descriptive message following conventional commits"
   ```
   - Use conventional commit format: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, etc.
   - Include scope when applicable: `feat(api):`, `fix(ui):`, `test(auth):`
   - Write descriptive messages that explain WHAT changed and WHY

2. **Pushed to Remote Repository**:
   ```bash
   git push origin <branch-name>
   ```
   - Never leave completed features uncommitted
   - Push regularly to maintain backup and enable collaboration
   - Ensure CI/CD pipelines pass before considering feature complete

3. **Branch Hygiene**:
   - Work on feature branches, never directly on `main`
   - Branch naming convention: `feature/<feature-name>`, `fix/<issue-name>`, `docs/<doc-update>`
   - Create pull requests for all significant changes

4. **Ralph Integration**:
   - Update .ralph/@fix_plan.md with new tasks before starting work
   - Mark items complete in .ralph/@fix_plan.md upon completion
   - Update .ralph/PROMPT.md if development patterns change
   - Test features work within Ralph's autonomous loop

### Documentation Requirements

**ALL implementation documentation MUST remain synchronized with the codebase**:

1. **Code Documentation**:
   - Language-appropriate documentation (JSDoc, docstrings, etc.)
   - Update inline comments when implementation changes
   - Remove outdated comments immediately

2. **Implementation Documentation**:
   - Update relevant sections in this AGENT.md file
   - Keep build and test commands current
   - Update configuration examples when defaults change
   - Document breaking changes prominently

3. **README Updates**:
   - Keep feature lists current
   - Update setup instructions when dependencies change
   - Maintain accurate command examples
   - Update version compatibility information

4. **AGENT.md Maintenance**:
   - Add new build patterns to relevant sections
   - Update "Key Learnings" with new insights
   - Keep command examples accurate and tested
   - Document new testing patterns or quality gates

### Feature Completion Checklist

Before marking ANY feature as complete, verify:

- [ ] All tests pass with appropriate framework command
- [ ] Code coverage meets 85% minimum threshold
- [ ] Coverage report reviewed for meaningful test quality
- [ ] Code formatted according to project standards
- [ ] Type checking passes (if applicable)
- [ ] All changes committed with conventional commit messages
- [ ] All commits pushed to remote repository
- [ ] .ralph/@fix_plan.md task marked as complete
- [ ] Implementation documentation updated
- [ ] Inline code comments updated or added
- [ ] .ralph/@AGENT.md updated (if new patterns introduced)
- [ ] Breaking changes documented
- [ ] Features tested within Ralph loop (if applicable)
- [ ] CI/CD pipeline passes

### Rationale

These standards ensure:
- **Quality**: High test coverage and pass rates prevent regressions
- **Traceability**: Git commits and .ralph/@fix_plan.md provide clear history of changes
- **Maintainability**: Current documentation reduces onboarding time and prevents knowledge loss
- **Collaboration**: Pushed changes enable team visibility and code review
- **Reliability**: Consistent quality gates maintain production stability
- **Automation**: Ralph integration ensures continuous development practices

**Enforcement**: AI agents should automatically apply these standards to all feature development tasks without requiring explicit instruction for each task.
