# Reply Challenge - Team Schafe

**Schafe essen Wölfe**

## Setup

1. Create venv (`python3 -m venv venv`)
2. Activate said venv (`source venv/bin/activate`)
3. Install exempi
```bash
brew install exempi # macos
sudo apt-get install libexempi3
sudo apt-get install libexempi8 # on newer linux versions
```
4. Install the requirements (`pip install -r triangulation/requirements.txt`)
5. Run the notebook (`main.ipynb`)



## Troubleshooting:
In case exempi is not found, run
`sudo ln -s /opt/homebrew/lib/libexempi.dylib /usr/local/lib/libexempi.dylib`
