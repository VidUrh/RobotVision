:: Create venv ::
python -m venv .venv

:: Activate venv ::
CALL .\.venv\Scripts\activate.bat

:: Upgrade pip ::
python -m pip install --upgrade pip

pip install -r requirements.txt