# Air Gesture Control

A Python application that enables computer control through hand gestures using computer vision technology.

## Features

- Control mouse cursor with hand movements
- Perform clicks using gestures
- Adjust system volume with hand movements
- Control screen brightness
- System navigation shortcuts

## Requirements

- Python 3.8+
- OpenCV
- MediaPipe
- PyQt5
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/airgesture.git
cd airgesture
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

Run the application:
```bash
python -m airgesture.main
```

### Gesture Guide

Right Hand Controls:
- Two fingers up (with fingers together): Move cursor
- Spread fingers apart, then pinch: Left click
- Spread fingers apart, then middle-thumb tap: Right click
- Pinky finger up/down: Adjust screen brightness

Left Hand Controls:
- Index and middle fingers together up: Scroll up
- All fingers down: Scroll down
- Open palm: Task view (Win+Tab)
- Index finger up/down: Adjust volume

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/) 