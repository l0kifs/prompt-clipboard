````markdown
# User Stories and Acceptance Tests

This document contains user stories, acceptance criteria, and examples of acceptance tests (MVP) for the "Prompt Clipboard" utility.

---

## 1. Introduction
The purpose of this document is to provide a compact set of user stories and associated acceptance tests used for planning and verifying the MVP implementation: a local cross-platform Python GUI utility for storing, searching, and inserting prompts for AI agents.

---

## 2. MVP Feature Summary
- CRUD for prompts (create/read/update/delete)
- Tags and categories
- Full-text search (FTS) on title and body
- Global hotkey + overlay for quick search and insertion
- JSON import/export
- Optional local encryption for sensitive prompts

---

## 3. User Stories

1) Title: Create and Save a Prompt
- As a user, I want to create a new prompt with a title, text, and tags so that I can save it for later use.
- Acceptance Criteria (AC):
  - UI provides a form for title, body, tags, category, and optional parameters.
  - After saving, the prompt appears in the general list and is available for search.
  - Metadata created_at/updated_at are correctly set.

2) Title: Edit a Prompt
- As a user, I want to edit an existing prompt so that I can improve or update it.
- AC:
  - UI allows opening an existing prompt for editing.
  - Saving updates body/title/tags and updated_at.
  - Version/history is saved (minimally: increment version).

3) Title: Delete a Prompt
- As a user, I want to delete prompts so that I can keep my collection organized.
- AC:
  - Deletion requires confirmation (undo is optional).
  - Deleted prompt disappears from the list and search results.

4) Title: Quick Search and Insert via Hotkey
- As a power-user, I want to press a global hotkey, type a search query, select a prompt, and insert it into the active application.
- AC:
  - Global hotkey opens an overlay window on top of the current application.
  - Incremental search displays relevant results in real time.
  - Selecting a result copies the text to clipboard and/or inserts into the active application (behavior is configurable).

5) Title: Templates with Variables
- As a user, I want to define placeholder variables in prompt text (e.g., {{topic}}) and fill them before copying.
- AC:
  - When selecting a prompt with variables, a form is shown to fill in the variables.
  - After filling in and confirming, placeholders are replaced and the result is copied.

6) Title: Search by Tags and Filtering
- As a user, I want to filter prompts by tags, categories, and date so that I can find relevant records faster.
- AC:
  - Interface allows combining filters (tags AND/OR, category, date range).
  - Filtering correctly limits search results.

7) Title: Import/Export Collection
- As a user, I want to export and import prompt collections to JSON for backup and sharing.
- AC:
  - Export creates a JSON file with all fields (id, title, body, tags, params, metadata, timestamps).
  - Import loads records and handles duplicates by id or title (prompt: skip/merge/duplicate).

8) Title: Local Encryption of Sensitive Prompts
- As a security-conscious user, I want to mark prompts as "sensitive" and store them encrypted to prevent data leakage.
- AC:
  - UI allows marking a prompt as sensitive.
  - For sensitive prompts, body is stored encrypted (when encryption mode is enabled) and requires password/OS keyring to decrypt.
  - After restarting the application, the user must enter a password/permission to access decrypted data.

---

## 4. Acceptance Tests (MVP): High-Level Tests and Checks

Each test is described with preconditions, steps, and expected results.

### Test A: Happy Path — Create → Search → Quick Insert
- Precondition: application is running, empty DB.
- Steps:
  1. Open the application.
  2. Click "New prompt" and create a prompt with title `Test Prompt`, body `Summarize the following: ...`, tags `test,summary`.
  3. Save.
  4. Press the global hotkey, type `Test` in the overlay.
  5. Select the found prompt and press Enter/Copy.
- Expected result:
  - Prompt is visible in the list and search results include `Test Prompt`.
  - Prompt text is copied to clipboard.

### Test B: Edge Case — Import JSON with Duplicates
- Precondition: local DB contains a prompt with id `uuid-1` and title `Hello`.
- Steps:
  1. Prepare JSON with two records: one with id `uuid-1` (title=Hello), another with new id `uuid-2`.
  2. In the application select Import → load JSON.
  3. When prompted for duplicate handling, select `skip`.
- Expected result:
  - Record with id `uuid-1` remains unchanged.
  - Record with id `uuid-2` is added.
  - Import completes without errors.

### Test C: Edge Case — Copying Sensitive Prompt Requires Confirmation
- Precondition: DB contains a prompt with is_sensitive=true and encrypted if encryption is enabled.
- Steps:
  1. Press the hotkey and find the sensitive prompt.
  2. Try to copy it.
- Expected result:
  - Application prompts for password/permission before copying.
  - After successful authentication, text is copied; without authentication, action is rejected.

### Test D: Performance — Search over 10k Prompts
- Precondition: database contains 10,000 prompts (different text).
- Steps:
  1. Open overlay and perform a search query characteristic of one prompt.
- Expected result:
  - Result is displayed < 300ms on a typical laptop; UI remains responsive.

---

## 5. Test Data Example (JSON)
```json
[
  {
    "id": "uuid-1",
    "title": "Summarize meeting notes",
    "body": "Summarize the following notes: {{notes}}",
    "tags": ["summarize","meeting"],
    "parameters": {"temperature":0.2},
    "is_sensitive": false
  }
]
```

---

## 6. Acceptance Criteria (Summary)
- CRUD works without errors.
- Search returns relevant results.
- Quick insert via hotkey functions.
- Import/Export work, including duplicate handling.
- Sensitive-prompt encryption works and requires authentication.

---

## 7. Next Steps
- Prepare detailed user stories for each scenario (break down to tasks).
- Create automated unit/integration tests for core logic (DB, search, import/export, encryption).
- Propose UI wireframes and flow for overlay.

This document was created automatically.

````
