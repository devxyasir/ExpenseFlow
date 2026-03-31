# -*- mode: python ; coding: utf-8 -*-
# Single-file executable spec for Expense Flow

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('web', 'web'),
    ],
    hiddenimports=[
        'eel',
        'pymongo',
        'pymongo.mongo_client',
        'pymongo.server_api',
        'dotenv',
        'reportlab',
        'reportlab.lib',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'reportlab.lib.colors',
        'reportlab.lib.pagesizes',
        'reportlab.lib.units',
        'reportlab.lib.enums',
        'bson',
        'bson.objectid',
        'bson.codec_options',
        'dns.resolver',  # For mongodb srv support
        'eel_api',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'django',
        'flask',
        'jinja2',
        'sqlalchemy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ExpenseFlow',
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
    # Windows options
    icon='icon.ico',
    version=None,
    manifest=None,
    onefile=True,  # Single file executable
)
