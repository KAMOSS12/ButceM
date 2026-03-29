# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ctk_datas = collect_data_files('customtkinter')

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.ico', '.')] + ctk_datas,
    hiddenimports=[
        'customtkinter',
        'google.generativeai',
        'selenium',
        'openpyxl',
        'plyer', 'plyer.platforms', 'plyer.platforms.win', 'plyer.platforms.win.notification',
        'requests',
        'bs4',
        'pandas',
        'matplotlib',
        'dotenv',
    ] + collect_submodules('customtkinter'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BütçeM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
