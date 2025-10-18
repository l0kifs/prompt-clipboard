```markdown
# Technical Stack and Architecture — Prompt Clipboard

This document contains detailed recommendations for technology stack selection, architectural decisions, and a prototype plan for implementing the "Prompt Clipboard" utility (a cross-platform Python GUI utility for storing and inserting prompts).

---

## 1. Brief Summary of Recommendations
- Language: Python 3.11+
- GUI: PySide6 (Qt6) — primary candidate for desktop-native application. Alternatives: PyQt6 (licensing), Flet (web-first), DearPyGui (suitable for rapid prototypes).
- Local storage: SQLite + FTS5 for full-text search.
- ORM / DB layer: SQLAlchemy Core + Alembic (migration) or dataset for simplicity.
- Encryption: cryptography (Fernet / AES-GCM) + OS keyring to store master-key; alternatively libsodium.
- Packaging: PyInstaller (single-file executables) or Briefcase (native installers). CI: GitHub Actions for cross-compilation (windows/mac/linux).
- Hotkey / global shortcut: pynput (cross-platform), keyboard (Windows), pyobjc/Quartz (macOS) — use abstract layer and per-OS adapters.
- Clipboard operations: pyperclip or platform-specific calls; for insertion into active window — use OS-specific paste simulation (keyboard events) with caution.

---

## 2. Why PySide6
- Mature and full-featured Qt binding with native look on all platforms.
- PySide6 is licensed under LGPL (more convenient in some cases compared to PyQt commercial license).
- Large community, stable support, powerful widget system, model/view architecture for large lists (QAbstractItemModel).
- Well-suited for implementing overlay (hints) and global hotkey approach.

Alternative: Flet
- Fast UI development, but based on web view; may be simpler for cross-platform deployments, but less "desktop-native".

Alternative: DearPyGui
- Very fast rendering, but limited standard widgets and fewer ready-made components.

---

## 3. High-Level Architectural Schema
- Presentation Layer (GUI): PySide6 windows, overlay, dialogs
- Application Layer: UI controllers, Commands (create/edit/delete/search/import/export), Hotkey manager
- Domain Layer: Prompt model, Tag model, Folder model, Versioning, Encryption service
- Persistence Layer: SQLite DB with FTS5, migrations via Alembic
- Integration Layer: OS clipboard, global hotkeys, keyring, optional cloud sync

(loosely coupled modules, single event loop — Qt mainloop)

---

## 4. Database Schema (Example SQL)
- prompts
  - id TEXT PRIMARY KEY
  - title TEXT NOT NULL
  - body TEXT
  - body_encrypted BLOB NULL
  - is_sensitive BOOLEAN DEFAULT 0
  - tags TEXT (comma-separated) or normalized tags table
  - category_id TEXT NULL
  - parameters JSON
  - metadata JSON
  - version INTEGER DEFAULT 1
  - created_at DATETIME
  - updated_at DATETIME

- tags
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - name TEXT UNIQUE

- prompt_tags
  - prompt_id TEXT
  - tag_id INTEGER

- folders
  - id TEXT PRIMARY KEY
  - name TEXT
  - parent_id TEXT NULL

- history
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - prompt_id TEXT
  - action TEXT
  - diff JSON
  - actor TEXT
  - timestamp DATETIME

FTS virtual table for search (FTS5): prompts_fts(title, body, content='prompts', content_rowid='rowid')

Notes:
- Store non-sensitive body in `body`, and if `is_sensitive` then store encrypted payload in `body_encrypted` and set body=NULL or placeholder.
- Use JSON column type where supported (SQLite stores as TEXT but can be parsed).

---

## 5. Encryption Design
Requirements:
- Simple enable/disable encryption
- Master key stored in OS keyring or derived from user password
- `body_encrypted` field stores recorded ciphertext along with metadata (salt, nonce)

Design options:
- Option A (recommended): cryptography.Fernet (symmetric authenticated encryption). Pros: easy to use; Cons: key management manual.
- Option B: Use libsodium / pynacl (recommended for production-grade) with libsodium secretbox or AEAD.

Key storage:
- Use `keyring` library to store master-key in OS keyring (Keychain/Windows Credential Manager/SecretService).
- On first run, generate master key and save, or ask user for password derivation (PBKDF2/Argon2id) — latter is preferable for user-controlled key.

Workflow:
- If user enables encryption with password -> derive key via Argon2id -> store only a key-wrapping blob in keyring (encrypted by OS keyring); or store nothing and require password on startup.
- For convenience, allow opt-in "unlock on login" via OS keyring.

---

## 6. Search Implementation Details
- Use SQLite FTS5 virtual table for fulltext search with tokenizer set to unicode61.
- For ranking use bm25 extension if available, else use FTS built-in rank function.
- Index title and body; consider generating additional n-grams for fuzzy search.
- For tags and filters use normal SQL WHERE clauses; combine with FTS via `JOIN` on rowid.

Performance tips:
- Background index updates for large imports.
- Pagination and virtualized UI list (QListView with QAbstractItemModel) to handle large result sets.

---

## 7. Hotkey and Overlay Design
- Global hotkey manager abstracts per-OS implementation.
- On hotkey press:
  - If app not running, start in background (optional), show overlay.
  - Overlay is small frameless window (always on top) with an input field and result list.
  - Typing triggers asynchronous search against DB (debounce 50-150ms).
  - Selecting a result shows actions: Copy, Copy with params, Insert to active window.

Security note: Simulating paste into another application's input can be sensitive; provide clear UX and user consent.

---

## 8. CLI and API
- Provide a small CLI module (entrypoint `prompt-clip`) with commands:
  - add, list, search, export, import, copy
- Provide optional local REST API (Flask/FastAPI) listening on localhost if user enables (auth token). This allows IDE plugins/automation to talk to the app.

---

## 9. Packaging and Distribution
- Use `pyproject.toml` with `setuptools`/`flit`/`poetry` for package management.
- For desktop builds:
  - PyInstaller for single-file executables (fast start)
  - Briefcase for native installers (more polished)
- CI: GitHub Actions to produce artifacts for Windows, macOS, Linux.

---

## 10. Project Structure (Suggestion)
- src/
  - prompt_clip/
    - __init__.py
    - main.py (Qt entrypoint)
    - ui/ (Qt Designer .ui or programmatic widgets)
    - models/ (Prompt, Tag, Folder)
    - db/ (schema, migrations)
    - services/ (encryption_service.py, hotkey_manager.py, clipboard.py, search_service.py)
    - cli.py
    - api.py (optional)
- tests/
- docs/
- pyproject.toml

---

## 11. Minimal Prototype Plan (PoC)
Goal: working overlay + local DB + copy-to-clipboard
Steps (estimated 1–2 weeks):
1. Initialize project, pyproject, basic CLI bootstrap.
2. Implement SQLite schema and a small DB layer (no ORM required for PoC).
3. Create simple PySide6 window with an input box and a list view bound to DB results.
4. Implement global hotkey for one platform (Linux) using pynput and show overlay.
5. Implement copy-to-clipboard using Qt clipboard or pyperclip.
6. Wire up create + search + quick copy. Add basic tests for DB and search.

Acceptance for PoC: overlay opens via hotkey, search queries DB, selection copies content.

---

## 12. Implementation Tasks (Microtasks)
- [ ] Create repository and CI skeleton
- [ ] Implement DB schema and migrations
- [ ] Implement core domain models and basic CRUD
- [ ] Implement FTS search and ranking
- [ ] Implement PoC overlay (PySide6) and local hotkey (Linux)
- [ ] Implement CLI commands
- [ ] Implement optional encryption and keyring integration
- [ ] Write unit/integration tests and set up test CI
- [ ] Prepare cross-platform packaging pipeline

---

## 13. Risks and Recommendations
- Global hotkeys and paste simulation differ across OS — test separately on each platform.
- Packaging with Qt can increase binary size — use slim builds and document trade-offs.
- Key management must be careful: offer user-controlled password + OS keyring.

---

## 14. Resources and Links (Brief)
- SQLite FTS5 docs
- PySide6 documentation
- cryptography.io — Fernet and recipes
- keyring python library


---

This document was created automatically. If needed — I can generate an example `pyproject.toml`, minimal `main.py` PoC (overlay + DB) and tests.
```