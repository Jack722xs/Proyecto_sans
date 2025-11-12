# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main1.py'],
    pathex=[],
    binaries=[],
    datas=[('just-sans-talking (mp3cut.net).wav', '.'), ('gasters-theme_PgFvFMX.mp3', '.'), ('video\\deltarune Battle Meme Layout - Ordayne (720p, h264).mp4', 'video'), ('fonts', 'fonts'), ('determination.ttf', '.'), ('PixelOperator-Bold.ttf', '.'), ('PixelOperator8.ttf', '.')],
    hiddenimports=[],
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
    name='main1',
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
    icon=['images\\sans.ico'],
)
