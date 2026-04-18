@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem ============================================================
rem Subir TODO a GitHub pidiendo antes el comentario del commit
rem ============================================================

cd /d "%~dp0"

echo.
echo ==========================================
echo  SUBIR TODO (git add -A + commit + push)
echo ==========================================
echo.

set "MENSAJE="
set /p MENSAJE=Escribe el comentario del commit: 

if "%MENSAJE%"=="" (
	echo.
	echo [CANCELADO] No escribiste comentario. No se hizo nada.
	echo.
	pause
	exit /b 1
)

echo.
echo [1/4] Estado actual:
git status
if errorlevel 1 (
	echo.
	echo [ERROR] git status fallo. Revisa que estas en un repositorio Git.
	echo.
	pause
	exit /b 1
)

echo.
echo [2/4] Agregando TODO (incluye borrados)...
git add -A
if errorlevel 1 (
	echo.
	echo [ERROR] git add -A fallo.
	echo.
	pause
	exit /b 1
)

echo.
echo [3/4] Creando commit...
git commit -m "%MENSAJE%"
if errorlevel 1 (
	echo.
	echo [AVISO] git commit fallo. Puede que no haya cambios para commitear.
	echo.
	pause
	exit /b 1
)

echo.
echo [4/4] Haciendo push...
git push
if errorlevel 1 (
	echo.
	echo [ERROR] git push fallo. Revisa autenticacion / upstream / red.
	echo.
	pause
	exit /b 1
)

echo.
echo [OK] Subido correctamente.
echo.
pause
exit /b 0
