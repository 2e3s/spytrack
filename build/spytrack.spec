# -*- mode: python -*-

block_cipher = None

lib_path = '../venv/lib/python3.6/site-packages/'

a = Analysis(
    ['../spytrack/__main__.py'],
    pathex=[lib_path, '../projects/spytrack'],
    binaries=[],
    datas=[
        (lib_path + 'aw_core/schemas/bucket.json', 'aw_core/schemas'),
        (lib_path + 'aw_core/schemas/event.json', 'aw_core/schemas'),
        (lib_path + 'aw_core/schemas/export.json', 'aw_core/schemas'),
        ('../icon.png', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
# a.binaries = [x for x in a.binaries if not x[0].startswith("libicu")]
pyz = PYZ(
    a.pure, a.zipped_data,
    cipher=block_cipher
)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='spytrack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='spytrack'
)
