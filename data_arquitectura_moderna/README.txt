
Proyecto: Arquitectura de Datos Moderna
=======================================

Descripción
--------------
Este proyecto implementa una arquitectura de datos moderna que procesa información desde archivos CSV de clientes, productos y ventas, aplicando un flujo ETL completo para su almacenamiento en un Data Warehouse (PostgreSQL), creación de un Data Mart y generación de visualizaciones automáticas.

Estructura del Proyecto
--------------------------
data_arquitectura_moderna/
│
├── datalake/
│   ├── datos_crudos/
│   ├── datos_curados/
│   └── datos_procesados/
│
├── datamart/
│   ├── mart_ventas_mes_categoria.csv
│   └── mart_ventas_anio_categoria.csv
│
├── datos_origen/
│   ├── clientes.csv
│   ├── productos.csv
│   └── ventas.csv
│
├── dw/
│   ├── esquema.sql
│   └── load_dw.py
│ 
├── etl/
│   ├── diagnostico_*.py
│   ├── transformacion.py
│   └── limpia_*.py
│   └── ingesta.py 
│
├── scripts/
│   ├── crear_datamart.py
│   └── visualiza.py
│
├── run_proyecto.bat
└── README.md

Flujo del Proceso ETL
------------------------
1. **Ingesta de Datos**
   - Se cargan archivos CSV de clientes, productos y ventas en el Data Lake (zona de datos crudos).
   
2. **Diagnóstico**
   - Ejecución de scripts `diagnostico_*.py` para análisis de calidad y perfilado de datos.
   
3. **Limpieza**
   - Scripts `limpia_*.py` para validar y normalizar la información.

4. **Transformación**
   - Uso de `transformacion.py` para generar tablas dimensionales y de hechos.

5. **Carga a Data Warehouse**
   - Uso de `load_dw.py` para almacenar datos en PostgreSQL.

6. **Creación de Data Mart**
   - `crear_datamart.py` genera CSV agregados:
     - `mart_ventas_mes_categoria.csv`
     - `mart_ventas_anio_categoria.csv`

7. **Visualización**
   - `visualiza.py` produce gráficos `.png` a partir del Data Mart.

Ejecución
------------
Para correr todo el pipeline de forma automática desde carpeta raíz mediante cmd:
    run_proyecto.bat

Diagrama de Arquitectura
----------------------------
El esquema visual de la arquitectura se encuentra en:
    /docs/arquitectura_datos_Daniela_Mendez.pdf

Tecnologías Utilizadas
--------------------------
- Python 3.x
- PostgreSQL
- Pandas
- Matplotlib / Seaborn
- Tabulate
- Batch Scripting (.bat)
- Draw.io
