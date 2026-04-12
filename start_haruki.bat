@echo off
title Haruki POS System
color 0A

echo.
echo  ================================
echo   HARUKI POS - Starting Server
echo   春木 ポイント・オブ・セール
echo  ================================
echo.

cd /d "D:\Python\Ye Htut Win\django\Haruki"
call venv\Scripts\activate.bat

echo  Running system checks...
python manage.py migrate --run-syncdb

echo.
echo  Server starting on http://localhost:8000
echo  Press Ctrl+C to stop the server
echo.

start "" "http://localhost:8000/login/"
python manage.py runserver 0.0.0.0:8000

pause