# Prompt Clipboard

[![PyPI version](https://badge.fury.io/py/prompt-clipboard.svg)](https://badge.fury.io/py/prompt-clipboard)
[![Python Version](https://img.shields.io/pypi/pyversions/prompt-clipboard.svg)](https://pypi.org/project/prompt-clipboard/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A lightweight cross-platform clipboard manager designed specifically for AI prompts, templates, and frequently used text snippets.

## Highlights

🎯 **Smart & Intuitive**
- Multi-select prompts and copy them all at once
- Automatic relation tracking: prompts used together stay together
- Intelligent search with related prompts suggestions

⚡ **Fast & Efficient**
- Global hotkey access from anywhere
- Usage-based sorting keeps your favorites on top
- Keyboard-first interface for maximum productivity

🔒 **Private & Secure**
- 100% local storage, no cloud required
- No telemetry, no tracking
- Your data stays on your machine

## Features

- 🚀 **Fast Access** - Global hotkey to instantly search and insert prompts (default: `Ctrl+Alt+I`)
- 🔍 **Intelligent Search** - Multi-word search with automatic grouping of related prompts
- 🔗 **Smart Relations** - Automatically tracks which prompts are used together
- 📊 **Usage Analytics** - Tracks usage count to prioritize frequently used prompts
- ⌨️ **Keyboard-First** - Navigate entirely with keyboard shortcuts
  - `Space` - Toggle multi-selection
  - `Enter` - Copy selected prompt(s) to clipboard
  - `↑/↓` - Navigate between search and list
  - `Esc` - Close overlay
- 🎯 **Multi-Select** - Select and copy multiple prompts at once (separated by newlines)
- 💾 **Local Storage** - All data stored locally in SQLite database
- 🎨 **Modern UI** - Clean interface built with PySide6
- 🔐 **Privacy-Focused** - No cloud sync, no telemetry, your data stays local

## Quick Start

### Installation

#### From PyPI (Recommended)

```bash
pip install prompt-clipboard
```

Or using `uvx`:

```bash
uvx prompt-clipboard
```

#### From Source

```bash
git clone https://github.com/l0kifs/prompt-clipboard.git
cd prompt-clipboard
uv sync
uv run prompt-clipboard
```

### Usage

1. **Launch the application:**
   ```bash
   prompt-clipboard
   ```

2. **Add your first prompt:**
   - Click "Add Prompt" button or press the hotkey
   - Enter your prompt text
   - Click "Save"

3. **Use the global hotkey:**
   - Press `Ctrl+Alt+I` (default) anywhere
   - Start typing to search (all words must match)
   - Use arrow keys to navigate
   - Press `Space` to toggle selection (multi-select)
   - Press `Enter` to copy to clipboard
   - Press `Esc` to close

4. **Advanced features:**
   - **Multi-select**: Use `Space` or `Ctrl+Click` to select multiple prompts
   - **Related prompts**: Prompts used together are automatically grouped
   - **Smart search**: Search results show related prompts with connection strength
   - **Quick add**: Type in search and press Enter to create a new prompt

5. **Configure settings:**
   - Click the settings icon
   - Customize global hotkey
   - Restart application for hotkey changes to take effect

## Configuration

The application stores its data in:
- **Linux**: `~/.local/share/prompt-clipboard/`
- **macOS**: `~/Library/Application Support/prompt-clipboard/`
- **Windows**: `%APPDATA%\prompt-clipboard\`

**Files:**
- `prompt_clip.db` - SQLite database with prompts and relations
- `logs/prompt_clipboard.log` - Application logs

**Keyboard Shortcuts:**
- `Ctrl+Alt+I` - Open/close overlay (configurable)
- `Space` - Toggle prompt selection
- `Enter` - Copy selected prompt(s)
- `↑/↓` - Navigate list
- `Esc` - Close overlay

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for advanced configuration options.

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone repository
git clone https://github.com/l0kifs/prompt-clipboard.git
cd prompt-clipboard

# Install dependencies
uv sync

# Run application
uv run prompt-clipboard
```

### Project Structure

```
prompt-clipboard/
├── src/
│   └── prompt_clipboard/
│       ├── main.py                 # Application entry point
│       ├── database.py             # SQLite database operations
│       ├── hotkey.py               # Global hotkey handler
│       ├── prompt_manager_window.py # Main window
│       ├── add_prompt_dialog.py    # Add prompt dialog
│       ├── edit_prompt_dialog.py   # Edit prompt dialog
│       ├── settings_window.py      # Settings dialog
│       └── config/
│           ├── settings.py         # Application settings
│           └── logging.py          # Logging configuration
├── docs/                           # Documentation
├── pyproject.toml                  # Project configuration
└── README.md
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Import/Export functionality (JSON/CSV)
- [ ] Prompt templates with variable substitution
- [ ] Cloud synchronization (optional, encrypted)
- [ ] Prompt versioning and history
- [ ] Custom themes (dark/light mode)
- [ ] Multi-language UI support
- [ ] Prompt categories/folders
- [ ] Statistics and analytics dashboard

## Support

- **Issues**: [GitHub Issues](https://github.com/l0kifs/prompt-clipboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/l0kifs/prompt-clipboard/discussions)

## Acknowledgments

Built with:
- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with Python type hints
- [pynput](https://pynput.readthedocs.io/) - Global hotkey handling
- [loguru](https://loguru.readthedocs.io/) - Python logging made simple