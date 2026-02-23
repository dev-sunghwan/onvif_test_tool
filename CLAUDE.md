# ONVIF Command Tester — Project Guide

## Overview
Flask web app for testing ONVIF camera commands via SOAP/WSDL. Uses zeep for SOAP client, supports HTTP/HTTPS with self-signed certs.

## Project Structure
```
app.py                  — Flask entry point, routes, JSON serialization
config.py               — ONVIF_PRESETS (16 services), ENDPOINT_MAP, DEFAULT_PORT
onvif_client/
  command_executor.py   — SOAP call execution, XML capture, HTTPS support
  wsdl_loader.py        — WSDL parsing, binding/operation extraction
  type_introspector.py  — XSD type → form parameter conversion
  serializer.py         — zeep response → JSON serialization
templates/index.html    — Single-page UI (Bootstrap 5)
static/js/app.js        — Frontend logic (vanilla JS, IIFE)
static/js/params.js     — Dynamic parameter form builder
static/css/style.css    — Custom styles
```

## Commands
```bash
# Run dev server (from venv)
.venv\Scripts\python.exe app.py

# Build exe
.venv\Scripts\python.exe -m PyInstaller onvif_tester.spec --clean --noconfirm

# Install dependencies
pip install -r requirements.txt
```

## Git Configuration
- Remote: `https://github.com/dev-sunghwan/onvif_test_tool.git`
- Push with: `git push https://dev-sunghwan@github.com/dev-sunghwan/onvif_test_tool.git main`
- Commit email (repo-local): `dev.sunghwan@gmail.com`
- Commit style: imperative mood, concise (e.g., "Add HTTPS support", "Fix AnyAttribute bug")

## Key Conventions
- Python: type hints on public methods, docstrings on classes
- JS: vanilla JS only, no frameworks, IIFE pattern, Bootstrap 5
- All ONVIF service presets defined in `config.py` ONVIF_PRESETS dict
- Camera endpoint paths mapped in `config.py` ENDPOINT_MAP dict
- zeep quirks: guard `hasattr(obj, "type")` for AnyAttribute objects in type_introspector.py

## Known Issues
- zeep AnyAttribute: objects in `elements` and `attributes` iterations may lack `.type` — always guard with hasattr
- WSDL first-load is slow (~5-15s per service) due to remote XSD fetching; subsequent loads use zeep cache
- Cameras use self-signed certs — HTTPS requires `verify=False` on requests.Session

## PyInstaller Notes
- `sys._MEIPASS` used for template/static paths in frozen mode
- `console=True` in spec (needed for Flask server log + Ctrl+C shutdown)
- Hidden imports: zeep.plugins, zeep.wsse.username, zeep.transports, zeep.cache, lxml.etree, lxml._elementpath
- Build output: `dist/ONVIF_Command_Tester.exe` (~17MB)
