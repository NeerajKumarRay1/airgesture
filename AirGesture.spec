# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\airgesture\\main.py'],
    pathex=['C:\\Users\\neera\\OneDrive\\Desktop\\airgesture\\src'],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=['mediapipe', 'cv2', 'numpy', 'PyQt5', 'screen_brightness_control', 'pynput', 'pycaw', 'comtypes'],
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
    name='AirGesture',
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
)
