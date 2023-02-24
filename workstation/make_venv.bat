:: Create venv ::
python -m venv ..\RobotVision\.venv

:: Activate venv ::
cmd /k "..\RobotVision\.venv\Scripts\activate.bat"

:: Upgrade pip ::
python -m pip install --upgrade pip

pip install -r requirements.txt