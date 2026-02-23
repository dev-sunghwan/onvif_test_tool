# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for ONVIF Command Tester."""

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
    name="ONVIF_Command_Tester",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)
