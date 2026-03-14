# Contributing to ONVIF Command Tester

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/dev-sunghwan/onvif_test_tool.git
cd onvif_test_tool

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Project Structure

```
app.py                  — Flask entry point, routes, VERSION constant
config.py               — ONVIF_PRESETS, ENDPOINT_MAP, DEFAULT_PORT
onvif_client/
  command_executor.py   — SOAP call execution, HTTPS support
  wsdl_loader.py        — WSDL parsing, binding/operation extraction
  type_introspector.py  — XSD type → form parameter schema
  serializer.py         — zeep response → JSON serialization
  profile_checker.py    — ONVIF profile detection via GetServices
templates/index.html    — Single-page UI (Bootstrap 5)
static/js/app.js        — Frontend logic (vanilla JS, IIFE)
static/js/param-builder.js — Dynamic parameter form builder
static/css/style.css    — Custom styles
```

## Coding Conventions

**Python**
- Type hints on public methods
- Docstrings on classes
- Guard `hasattr(obj, "type")` before accessing `.type` on zeep objects (AnyAttribute quirk)

**JavaScript**
- Vanilla JS only — no frameworks
- IIFE pattern in `app.js`
- Bootstrap 5 components and utilities

**Config**
- All ONVIF service presets defined in `config.py` `ONVIF_PRESETS`
- Camera endpoint paths mapped in `config.py` `ENDPOINT_MAP`
- Version is the single source of truth in `app.py` `VERSION`

## Commit Style

Imperative mood, concise:
```
Add HTTPS support
Fix AnyAttribute bug in type_introspector
Update README with new features
```

## Building the exe

```bash
.venv\Scripts\python.exe -m PyInstaller onvif_tester.spec --clean --noconfirm
# Output: dist/ONVIF_Command_Tester_v{version}.exe
```

## Submitting a Pull Request

1. Fork the repository and create a branch from `main`
2. Make your changes
3. Test against a real ONVIF camera if possible
4. Submit a pull request with a clear description of what changed and why

## Reporting Issues

Use the issue templates:
- **Bug report**: unexpected errors or wrong behavior
- **Feature request**: new functionality or improvements
