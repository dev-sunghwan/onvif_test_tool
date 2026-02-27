# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for ONVIF Command Tester."""

import re
with open("app.py", encoding="utf-8") as _f:
    _version = re.search(r'VERSION\s*=\s*"(.+?)"', _f.read()).group(1)
_exe_name = f"ONVIF_Command_Tester_v{_version}"

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("templates", "templates"),
        ("static", "static"),
    ],
    hiddenimports=[
        "zeep.plugins",
        "zeep.wsse.username",
        "zeep.transports",
        "zeep.cache",
        "zeep.xsd",
        "zeep.xsd.types",
        "zeep.xsd.types.complex",
        "zeep.xsd.types.simple",
        "lxml.etree",
        "lxml._elementpath",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=_exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)
