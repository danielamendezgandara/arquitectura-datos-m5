@echo on
setlocal EnableExtensions EnableDelayedExpansion

REM === 0) Posicionarse en la carpeta del proyecto ===
cd /d "%~dp0"

REM === 1) Elegir Python del venv si existe; si no, usar python del sistema ===
set "VENVPY=amb_mod5\Scripts\python.exe"
if exist "%VENVPY%" (
  set "PY=%VENVPY%"
) else (
  set "PY=python"
)
echo Usando interprete: %PY%
"%PY%" -V

REM === 2) Instalar dependencias si hay archivo de requerimientos ===
set "REQFILE="
if exist "requerimientos_actualizado.txt" set "REQFILE=requerimientos_actualizado.txt"
if exist "requirements.txt" set "REQFILE=requirements.txt"
if exist "requerimientos.txt" set "REQFILE=requerimientos.txt"

if "%REQFILE%"=="" goto :SKIP_REQ
echo Instalando dependencias desde %REQFILE% (puede tardar...)
"%PY%" -m pip install -r "%REQFILE%"
if errorlevel 1 echo AVISO: No se pudo instalar dependencias desde %REQFILE%
:SKIP_REQ

REM === 3) Crear carpetas base si no existen ===
for %%D in ("datalake\datos_crudos" "datalake\datos_procesados" "datalake\datos_curados" "datamart" "reportes_datos_crudos" "reportes_datos_procesados" "viz") do (
  if not exist "%%~D" mkdir "%%~D"
)

echo.
echo === LISTADO RAPIDO ===
if exist datalake  dir /b datalake
if exist etl       dir /b etl
if exist scripts   dir /b scripts
if exist dw        dir /b dw
echo =======================
echo.

REM === 4) Ingesta
if exist "etl\ingesta.py" (
   echo [1/14] Ingesta (etl\ingesta.py)
  "%PY%" etl\ingesta.py || goto :ERROR
) else (
   echo [1/14] Omitido: Falta etl\ingesta.py >>"%LOG%"
)

REM === 5) Diagnostico previo (CRUDO) si existen scripts ===
if exist "etl\diagnostico_ventas.py" (
  echo [2/14] Diagnostico CRUDO ventas ^> reportes_datos_crudos
  "%PY%" etl\diagnostico_ventas.py datalake\datos_crudos\ventas.csv  1>>run_log.txt 2>>&1
)
if exist "etl\diagnostico_clientes.py" (
  echo [3/14] Diagnostico CRUDO clientes ^> reportes_datos_crudos
  "%PY%" etl\diagnostico_clientes.py datalake\datos_crudos\clientes.csv  1>>run_log.txt 2>>&1
)
if exist "etl\diagnostico_productos.py" (
  echo [4/14] Diagnostico CRUDO productos ^> reportes_datos_crudos
  "%PY%" etl\diagnostico_productos.py datalake\datos_crudos\productos.csv  1>>run_log.txt 2>>&1
)

REM === 6) Limpieza (CRUDO -> PROCESADO) ===
echo [5/14] Limpieza clientes ^> datalake\datos_procesados
if exist "etl\limpia_clientes.py" (
  "%PY%" etl\limpia_clientes.py || goto :ERROR
) else if exist "etl\clean_clientes.py" (
  "%PY%" etl\clean_clientes.py || goto :ERROR
) else (
  echo AVISO: No se encontro etl\limpia_clientes.py ni etl\clean_clientes.py
)

echo [6/14] Limpieza productos ^> datalake\datos_procesados
if exist "etl\limpia_productos.py" (
  "%PY%" etl\limpia_productos.py || goto :ERROR
) else if exist "etl\clean_productos.py" (
  "%PY%" etl\clean_productos.py || goto :ERROR
) else (
  echo AVISO: No se encontro etl\limpia_productos.py ni etl\clean_productos.py
)

echo [7/14] Limpieza ventas ^> datalake\datos_procesados
if exist "etl\limpia_ventas.py" (
  "%PY%" etl\limpia_ventas.py || goto :ERROR
) else if exist "etl\clean_ventas.py" (
  "%PY%" etl\clean_ventas.py || goto :ERROR
) else (
  echo AVISO: No se encontro etl\limpia_ventas.py ni etl\clean_ventas.py
)

REM === 7) Diagnostico posterior (PROCESADO) si existen scripts ===
if exist "etl\diagnostico_ventas.py" (
  echo [8/14] Diagnostico PROCESADO ventas ^> reportes_datos_procesados
  "%PY%" etl\diagnostico_ventas.py datalake\datos_procesados\ventas_limpio.csv  1>>run_log.txt 2>>&1
)
if exist "etl\diagnostico_clientes.py" (
  echo [9/14] Diagnostico PROCESADO clientes ^> reportes_datos_procesados
  "%PY%" etl\diagnostico_clientes.py datalake\datos_procesados\clientes_limpio.csv  1>>run_log.txt 2>>&1
)
if exist "etl\diagnostico_productos.py" (
  echo [10/14] Diagnostico PROCESADO productos ^> reportes_datos_procesados
  "%PY%" etl\diagnostico_productos.py datalake\datos_procesados\productos_limpio.csv  1>>run_log.txt 2>>&1
)

REM === 8) TRANSFORMACION (OBLIGATORIO) - crea dimensiones y hecho_ventas
if exist "etl\transformacion.py" (
  echo [11/14] Transformacion (etl\transformacion.py)
  "%PY%" etl\transformacion.py || goto :ERROR
) else (
  echo [11/14] Omitido: Falta etl\transformacion.py >>"%LOG%"
)


REM === 9) (Opcional) Carga al DW ===
if exist "dw\load_dw.py" (
  echo [12/14] Carga al Data Warehouse (dw\load_dw.py)
  "%PY%" dw\load_dw.py || goto :ERROR
) else (
  echo [12/14] Omitido: No se encontro script de carga DW.
)

REM === 10) DATAMART (OBLIGATORIO)
echo [13/14] Data Mart (OBLIGATORIO)
if exist "scripts\crear_datamart.py" (
  "%PY%" scripts\crear_datamart.py || goto :ERROR
) else (
  echo [13/14] Falta scripts\crear_datamart.py
)

REM === 11) VISUALIZACION (OBLIGATORIO)
echo [14/14] Visualizacion (OBLIGATORIO)
if exist "scripts\visualiza.py" (
  "%PY%" scripts\visualiza.py || goto :ERROR
) else (
  echo [14/14] Falta scripts\visualiza.py
)

echo.
echo ==== Flujo completado con exito ====
echo Revisa run_log.txt para mas detalle de diagnosticos.
pause
exit /b 0

:ERROR
echo ==== Ocurrio un error. Revisa el mensaje anterior y el archivo run_log.txt ====
type run_log.txt
pause
exit /b 1
