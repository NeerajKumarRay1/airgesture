from setuptools import setup, find_packages

setup(
    name="airgesture",
    version="0.1",
    author="Neeraj",
    author_email="your.email@example.com",
    description="Control your computer with intuitive hand gestures",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://your-website.com/airnav",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.9.0",
        "mediapipe>=0.10.13",
        "PyQt5>=5.15.0",
        "numpy>=1.26.4",
        "pyautogui>=0.9.0",
        "screen-brightness-control>=0.9.0",
        "pynput>=1.7.0",
        "pycaw>=20181226"
    ],
    entry_points={
        "console_scripts": [
            "airgesture=airgesture.main:main",
        ],
    },
) 