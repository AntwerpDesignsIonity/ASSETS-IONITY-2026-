@echo off
REM ===========================================================================
REM  IONITY GLOBAL / AEDI :: terminal intro (Windows Terminal / ANSI console)
REM  (c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd | Policy 986 AED | TM2
REM ===========================================================================
setlocal
chcp 65001 >nul
cls
type "%~dp0..\banners\ionity-global-banner.ans"
echo.
type "%~dp0..\logos\ionity-global-logo-100col.ans"
echo.
echo   Building Tomorrow, Today.   Anything is Possible with God.
echo   www.ionity.today ^| Policy 986 AED ^| TM2
endlocal
