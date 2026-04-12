@echo off
title Haruki POS - Backup

set BACKUP_DIR=D:\Haruki_Backups
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo Backing up Haruki database...
copy "D:\Python\Ye Htut Win\django\Haruki\db.sqlite3" "%BACKUP_DIR%\haruki_%DATE%.db"

echo.
echo Backup saved to: %BACKUP_DIR%\haruki_%DATE%.db
echo.
pause