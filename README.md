# Reply Challenge - Team Schafe

“Schafe essen Wölfe”

## Overview

This project detects objects from drone images and triangulates their positions to generate KML/KMZ outputs for visualization and flight planning.

### Main components:
- Object detection using a trained YOLOv11 model.
- Triangulation based on detected objects from multiple viewpoints.
- Export to Google Earth (.kmz) and flight planning formats.

## Setup

### 1. Environment Setup
```
python3 -m venv venv
source venv/bin/activate
```
### 2. Install Dependencies

Make sure exempi is installed:
- macOS
```
brew install exempi
```
- Linux
```
sudo apt-get install libexempi3
sudo apt-get install libexempi8  # on newer Linux versions
```


If exempi is not found:
```
sudo ln -s /opt/homebrew/lib/libexempi.dylib /usr/local/lib/libexempi.dylib
```

Then install Python requirements:

```
pip install -r triangulation/requirements.txt
````

### 3. Download or Place the Model

Ensure `model/best.pt` exists. This is your trained YOLO model.

## Running the Project
- Main processing is inside `main.ipynb`.
- You can also use `triangulation/main.py` and `object_detection.py` for script-based usage.
- Outputs will be saved as `.kmz` files (for example, `output.kmz`).

### Folder Structure
```
.
├── main.ipynb
├── object_detection.py
├── model/
│   └── best.pt
├── templates/
│   ├── template.kml
│   └── waylines.wpml
├── triangulation/
│   ├── bbox.py
│   ├── export.py
│   ├── flight_planning.py
│   ├── metadata.py
│   ├── triangulate.py
│   ├── trigonometry.py
│   ├── visualize.py
│   ├── ...
├── output.kmz
└── README.md
```
## Notes

- Images must contain metadata (GPS coordinates, altitude, etc.) for triangulation to work.
- The flight planning exports are based on pre-defined templates.
