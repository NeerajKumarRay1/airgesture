# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\airgesture\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\neera\\OneDrive\\Desktop\\airgesture\\venv\\Lib\\site-packages\\mediapipe\\modules\\hand_landmark', 'mediapipe/modules/hand_landmark'), ('C:\\Users\\neera\\OneDrive\\Desktop\\airgesture\\venv\\Lib\\site-packages\\mediapipe\\modules\\palm_detection', 'mediapipe/modules/palm_detection')],
    hiddenimports=['mediapipe', 'cv2', 'numpy', 'PyQt5'],
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
    name='AirNav',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=['assets\\icon.ico'],
)
