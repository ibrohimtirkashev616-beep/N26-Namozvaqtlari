@echo off
chcp 65001 > nul
echo ========================================================
echo   🚀 Local Telegram Bot API Serverini Ishga Tushirish
echo   Limit: 2000 MB (2 GB) fayllar uchun
echo ========================================================

docker compose up -d

echo.
echo ✅ Server http://localhost:8081 manzilida ishga tushdi!
echo.
pause
