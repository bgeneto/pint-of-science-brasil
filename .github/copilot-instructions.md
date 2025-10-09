# Pint of Science Certificate System - AI Coding Guide

## Architecture Overview

This is a **Streamlit-based certificate management system** for the Pint of Science Brasil event. The architecture follows strict separation of concerns with a multi-page Streamlit app:

- **`Home.py`**: Public-facing entry point (registration, certificate download, login form)
- **`pages/1_✅_Validação_de_Participantes.py`**: Coordinator area (validate participants)
- **`pages/2_⚙️_Administração.py`**: Superadmin area (full CRUD management)
- **`app/`**: Core business logic modules

### Key Architectural Decisions

1. **Encrypted PII**: `nome_completo` and `email` in `participantes` table are stored as BLOB using Fernet encryption
2. **Session-based Auth**: Authentication managed entirely through `st.session_state` with centralized keys in `SESSION_KEYS` dict
3. **Repository Pattern**: Database access abstracted through repositories in `app/db.py`
4. **Service Layer**: All business logic (encryption, PDF generation, email) centralized in `app/services.py`

## Critical Patterns

### 1. Session State Management

**ALWAYS** use the `SESSION_KEYS` dictionary from `app/auth.py` when accessing session state:

```python
from app.auth import SESSION_KEYS

# ✅ CORRECT - Using SESSION_KEYS
user_id = st.session_state.get(SESSION_KEYS["user_id"])

# ❌ WRONG - Hard-coding keys
user_id = st.session_state.get("user_id")
```

Session keys: `logged_in`, `user_id`, `user_email`, `user_name`, `is_superadmin`, `login_time`, `last_activity`, `allowed_cities`

### 2. Page Protection

Protected pages MUST start with access control using the helper functions:

```python
from app.auth import require_login, require_superadmin

# For coordinator pages
require_login()

# For superadmin pages
require_superadmin()
```

These functions call `st.stop()` internally if unauthorized - no need for manual `if/else` checks.

### 3. Database Session Management

**ALWAYS** use the context manager pattern for database operations:

```python
from app.db import db_manager

# ✅ CORRECT - Context manager with auto-commit/rollback
with db_manager.get_db_session() as session:
    coord_repo = get_coordenador_repository(session)
    coordenador = coord_repo.get_by_email(email)

# ❌ WRONG - Manual session management
session = db_manager.get_session()
# ... operations without proper cleanup
```

### 4. PII Encryption/Decryption

Access the encryption service as a singleton:

```python
from app.services import servico_criptografia

# Encrypt before storing
email_encrypted = servico_criptografia.criptografar_email(email)

# Decrypt when reading
email_plain = servico_criptografia.descriptografar(participante.email_encrypted)
```

### 5. Environment Configuration

All config loaded from `.env` via `app/core.py`. **NEVER** use `os.getenv()` directly:

```python
from app.core import settings

# ✅ CORRECT
if settings.is_email_configured:
    # send email

# ❌ WRONG
if os.getenv("BREVO_API_KEY"):
    # ...
```

Required env vars: `ENCRYPTION_KEY` (Fernet key), `DATABASE_URL`, `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`

## Development Workflows

### Running the Application

```bash
# Activate environment (using uv recommended)
source .venv/bin/activate  # or `source pint/bin/activate`

# Run Streamlit
streamlit run Home.py

# Access at http://localhost:8501
```

### Database Initialization

Database auto-initializes on first `db_manager` usage. To manually reset:

```bash
rm pint_of_science.db
python test_system.py  # Re-creates with test data
```

### Testing

```bash
# Run system validation tests
python test_system.py

# Expected output: Connection tests, encryption tests, database checks

# Run pytest unit/integration tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app
```

**Test Organization**:
- ALL unit and integration tests MUST go in the `tests/` folder
- `test_system.py` in root is for system validation/smoke tests only
- Follow pytest conventions: `test_*.py` or `*_test.py` filenames
- Mirror app structure in tests: `tests/test_auth.py`, `tests/test_services.py`, etc.

### Adding New Pages

1. Create in `pages/` with numeric prefix: `3_New_Feature.py`
2. Add page protection at top: `require_login()` or `require_superadmin()`
3. Import from `app/` modules - never duplicate business logic in pages
4. Use `st.session_state` via `SESSION_KEYS` for user context

## Common Pitfalls

1. **Don't decrypt in queries**: Can't filter by encrypted fields. Use separate lookup tables if needed.
2. **Check `is_email_configured`**: Email features fail gracefully if Brevo not configured.
3. **Import order matters**: `app/core.py` loads `.env` - import `settings` before other app modules.
4. **Streamlit reruns**: Every widget interaction reruns entire script. Use `@st.cache_data` for expensive operations.
5. **Portuguese UI**: All user-facing text in Brazilian Portuguese. Code/comments in English.

## Project-Specific Conventions

- **File encoding**: UTF-8 throughout
- **Date format**: ISO 8601 (`datetime.isoformat()`) in DB, `DD/MM/YYYY HH:MM` for display
- **Password hashing**: bcrypt via `app/auth.py:AuthManager.hash_password()`
- **Audit logging**: All coordinator actions logged to `auditoria` table via repositories
- **Certificate naming**: `Certificado-PintOfScience-{ANO}-{UUID_CURTO}.pdf`
- **Test location**: All unit/integration tests go in `tests/` folder (pytest structure)

## Key Files Reference

- **`app/models.py`**: SQLAlchemy ORM models + Pydantic validators (371 lines)
- **`app/services.py`**: Business logic (PDF, email, encryption) (927 lines)
- **`app/auth.py`**: Complete auth system with `AuthManager` class (497 lines)
- **`app/db.py`**: `DatabaseManager` and repository pattern (545 lines)
- **`CLAUDE.md`**: Original project brief with full requirements

## Integration Points

- **Brevo API**: Email sending via `app/services.py:ServicoEmail` (REST API)
- **ReportLab**: PDF generation in `app/services.py:ServicoCertificado`
- **SQLite**: Local file database (`pint_of_science.db`)

When modifying email/PDF features, always test with `settings.is_email_configured` checks for graceful degradation.

## Tooling for shell interactions (install if missing)

- Is it about finding FILES? use `fd`
- Is it about finding TEXT/strings? use `rg`
- Is it about finding CODE STRUCTURE? use `ast-grep`
- Is it about SELECTING from multiple results? pipe to `fzf`
- Is it about interacting with JSON? use `jq`
- Is it about interacting with YAML or XML? use `yq`
