## Setup

1. Create venv (`python3 -m venv venv`)
2. Activate said venv (`source venv/bin/activate`)
3. Install exempi (`brew install exempi`)
4. Install the requiremnets (`pip install -r requirements.txt`)
5. Run the script (`python3 main.py`)

Troubleshooting:
In case exempi is not found, run
`sudo ln -s /opt/homebrew/lib/libexempi.dylib /usr/local/lib/libexempi.dylib`