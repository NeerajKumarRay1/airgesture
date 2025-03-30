import PyInstaller.__main__
import os
import sys
import mediapipe as mp
from pathlib import Path
import time

def main():
    # Get MediaPipe path for model files
    mp_path = os.path.join(Path(mp.__file__).parent, "modules")
    
    # Essential arguments only
    args = [
        'src/airgesture/main.py',
        '--name=AirNav',
        '--onefile',
        '--windowed',
        '--clean',
        '--version-file=version_info.txt',
        '--icon=assets/icon.ico',
        # Add MediaPipe model files
        f'--add-data={os.path.join(mp_path, "hand_landmark")}:mediapipe/modules/hand_landmark',
        f'--add-data={os.path.join(mp_path, "palm_detection")}:mediapipe/modules/palm_detection',
        # Essential imports only
        '--hidden-import=mediapipe',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=PyQt5',
        # Speed optimizations
        '--noupx',
        '--noconfirm',
    ]
    
    # Run PyInstaller
    print("Starting build process...")
    start_time = time.time()
    
    PyInstaller.__main__.run(args)
    
    build_time = time.time() - start_time
    print(f"\nBuild completed in {build_time:.2f} seconds!")
    print("Executable created: dist/AirNav.exe")

if __name__ == '__main__':
    main() 