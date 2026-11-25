@echo off
echo ===================================================
echo Launching Chrome with Remote Debugging for Antigravity
echo ===================================================
echo.
echo 1. Closing background Chrome processes...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 1 /nobreak >nul

echo 2. Launching Chrome on port 9222...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=* "https://www.linkedin.com/feed/foryou/"

echo.
echo Chrome is now open and listening on port 9222!
echo Return to Antigravity and run: /browser https://www.linkedin.com/feed/foryou/
echo ===================================================

