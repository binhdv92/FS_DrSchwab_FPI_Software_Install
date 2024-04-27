REM python -m pip install -r requirements.txt
SET var=%cd%
ECHO %var%
cd %var%
python -m venv venv
@CALL venv\scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt