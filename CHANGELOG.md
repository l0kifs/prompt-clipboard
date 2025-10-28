# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- None yet

### Changed
- None yet

### Fixed
- None yet

## [0.1.0] - 2025-10-28

### Added
- Initial release
- **Core Features:**
  - Global hotkey for quick prompt access (default: `Ctrl+Alt+I`, configurable)
  - Add, edit, and delete prompts through dedicated dialogs
  - Multi-word intelligent search (all words must match, order independent)
  - Multi-select support with `Space` key or `Ctrl+Click`
  - Automatic prompt relations tracking when multiple prompts are copied together
  - Usage count tracking for each prompt
  - Quick prompt creation: type in search and press Enter to add new prompt
- **User Interface:**
  - Main overlay window with instant search
  - Prompt manager window for bulk operations
  - Add/Edit prompt dialogs
  - Settings window for hotkey configuration
  - Keyboard-first navigation:
    - `Space` - Toggle selection
    - `Enter` - Copy selected prompt(s)
    - `↑/↓` - Navigate between search field and list
    - `Esc` - Close overlay
  - Visual grouping of related prompts in search results
  - Usage count display for each prompt
- **Intelligent Features:**
  - Smart search with automatic grouping of related prompts
  - Related prompts suggestion based on co-usage patterns
  - Connection strength tracking between prompts
  - Results sorted by usage count and relevance
- **Technical:**
  - PySide6 GUI framework with Qt widgets
  - SQLModel ORM for database operations
  - SQLite database with `Prompt`, `PromptRelation`, and `Setting` tables
  - Loguru for structured logging
  - Pynput for cross-platform global hotkey handling
  - Pydantic Settings for configuration management
  - Cross-platform support (Linux, macOS, Windows)
- **Documentation:**
  - Comprehensive README with usage examples
  - Business Requirements Document (BRD)
  - Technical stack and architecture documentation
  - User stories and acceptance criteria
  - Development and Git commit rules
  - Configuration guide
  - Publishing guide
  - Contributing guidelines

### Technical Details
- **Database Schema:**
  - `Prompt` table: id, body, usage_count, created_at, updated_at
  - `PromptRelation` table: tracks connections between prompts with strength metric
  - `Setting` table: stores user preferences (hotkey configuration)
- **Search Algorithm:**
  - Unicode-aware case-insensitive search
  - All search words must be present in prompt body
  - Results grouped by relation connections
  - Sorted by usage count and connection strength
- **Hotkey System:**
  - Customizable key combinations (modifiers + key)
  - Supports: Ctrl, Alt, Shift, Meta/Cmd/Win
  - Requires application restart after change

### Known Issues
- Hotkey configuration requires application restart to take effect
- No import/export functionality yet
- No cloud synchronization
- No undo/redo for prompt deletion
- Search is limited to prompt body (no title or tags yet)
