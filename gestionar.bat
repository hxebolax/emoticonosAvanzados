@echo off
chcp 65001 >nul
title Gestionar EmoticonosAvanzados para NVDA
echo.
echo ============================================================
echo  Gestor de EmoticonosAvanzados para NVDA
echo ============================================================
echo.
echo  1. Crear entorno virtual e instalar dependencias
echo  2. Compilar complemento (.nvda-addon)
echo  3. Crear entorno + Compilar (todo en uno)
echo  4. Limpiar archivos generados
echo  5. Generar archivo .pot para traducciones
echo  6. Salir
echo.
echo ============================================================
echo.
set /p opcion="Seleccione una opcion (1-6): "

if "%opcion%"=="1" goto crear_entorno
if "%opcion%"=="2" goto compilar
if "%opcion%"=="3" goto todo
if "%opcion%"=="4" goto limpiar
if "%opcion%"=="5" goto pot
if "%opcion%"=="6" goto salir
echo Opcion no valida.
pause
goto :eof

:crear_entorno
echo.
echo [INFO] Creando entorno virtual...
if exist ".venv" (
	echo [INFO] El entorno virtual ya existe. Eliminando...
	rmdir /s /q ".venv"
)
python -m venv .venv
if errorlevel 1 (
	echo [ERROR] No se pudo crear el entorno virtual.
	echo [ERROR] Asegurese de tener Python 3.11+ instalado y en el PATH.
	pause
	goto :eof
)
echo [OK] Entorno virtual creado.
echo.
echo [INFO] Instalando dependencias...
call ".venv\Scripts\activate.bat"
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
	echo [ERROR] No se pudieron instalar las dependencias.
	pause
	goto :eof
)
pip install scons markdown
if errorlevel 1 (
	echo [ERROR] No se pudieron instalar las herramientas de compilacion.
	pause
	goto :eof
)
echo.
echo [OK] Dependencias instaladas correctamente.
echo.
echo [INFO] Librerias instaladas:
pip list --format=columns 2>nul | findstr /i "emoji emot scons markdown"
echo.
pause
goto :eof

:compilar
echo.
echo [INFO] Compilando complemento...
if not exist ".venv" (
	echo [ERROR] No existe entorno virtual. Ejecute primero la opcion 1 o 3.
	pause
	goto :eof
)
call ".venv\Scripts\activate.bat"
echo [INFO] Copiando librerias al complemento...
scons
if errorlevel 1 (
	echo [ERROR] Error durante la compilacion.
	pause
	goto :eof
)
echo.
echo [OK] Complemento compilado correctamente.
echo [OK] El archivo .nvda-addon se encuentra en el directorio actual.
echo.
dir /b *.nvda-addon 2>nul
echo.
pause
goto :eof

:todo
echo.
echo [INFO] Ejecutando proceso completo...
echo.
echo === Paso 1: Crear entorno virtual ===
if exist ".venv" (
	echo [INFO] Eliminando entorno virtual anterior...
	rmdir /s /q ".venv"
)
python -m venv .venv
if errorlevel 1 (
	echo [ERROR] No se pudo crear el entorno virtual.
	pause
	goto :eof
)
echo [OK] Entorno virtual creado.
echo.
echo === Paso 2: Instalar dependencias ===
call ".venv\Scripts\activate.bat"
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
	echo [ERROR] Error instalando dependencias.
	pause
	goto :eof
)
pip install scons markdown
if errorlevel 1 (
	echo [ERROR] Error instalando herramientas de compilacion.
	pause
	goto :eof
)
echo [OK] Dependencias instaladas.
echo.
echo === Paso 3: Compilar complemento ===
scons
if errorlevel 1 (
	echo [ERROR] Error durante la compilacion.
	pause
	goto :eof
)
echo.
echo ============================================================
echo [OK] Proceso completo finalizado correctamente.
echo [OK] Archivo generado:
dir /b *.nvda-addon 2>nul
echo ============================================================
echo.
pause
goto :eof

:limpiar
echo.
echo [INFO] Limpiando archivos generados...
if exist ".venv" (
	call ".venv\Scripts\activate.bat"
	scons -c 2>nul
)
if exist "addon\libs" rmdir /s /q "addon\libs"
if exist "addon\doc\es" rmdir /s /q "addon\doc\es"
if exist "addon\manifest.ini" del /q "addon\manifest.ini"
if exist ".sconsign.dblite" del /q ".sconsign.dblite"
del /q *.nvda-addon 2>nul
del /q *.pot 2>nul
echo [OK] Limpieza completada.
echo.
pause
goto :eof

:pot
echo.
echo [INFO] Generando archivo .pot para traducciones...
if not exist ".venv" (
	echo [ERROR] No existe entorno virtual. Ejecute primero la opcion 1.
	pause
	goto :eof
)
call ".venv\Scripts\activate.bat"
scons pot
if errorlevel 1 (
	echo [ERROR] Error generando el archivo .pot.
	pause
	goto :eof
)
echo.
echo [OK] Archivo .pot generado correctamente.
dir /b *.pot 2>nul
echo.
pause
goto :eof

:salir
echo.
echo Hasta luego.
exit /b 0
