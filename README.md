# 🧩 Proyecto: Arquitectura de Datos Moderna

## 📘 Descripción
Este proyecto implementa una **arquitectura de datos moderna** que procesa información desde archivos CSV de clientes, productos y ventas, aplicando un **flujo ETL completo** para su almacenamiento en un **Data Warehouse (PostgreSQL)**, creación de un **Data Mart** y generación de **visualizaciones automáticas**.

---

## 🗂️ Estructura del Proyecto

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


---

## ⚙️ Flujo del Proceso ETL

1. **Ingesta de Datos**  
   Se cargan los archivos CSV de clientes, productos y ventas en el *Data Lake* (zona de datos crudos).

2. **Diagnóstico**  
   Se ejecutan los scripts `diagnostico_*.py` para realizar análisis de calidad y perfilado de datos.

3. **Limpieza**  
   Los scripts `limpia_*.py` validan y normalizan la información.

4. **Transformación**  
   El script `transformacion.py` genera tablas dimensionales y de hechos.

5. **Carga a Data Warehouse**  
   `load_dw.py` almacena los datos en PostgreSQL con la estructura definida en `esquema.sql`.

6. **Creación de Data Mart**  
   `crear_datamart.py` genera archivos agregados:
   - `mart_ventas_mes_categoria.csv`
   - `mart_ventas_anio_categoria.csv`

7. **Visualización**  
   `visualiza.py` produce gráficos `.png` a partir del Data Mart para análisis final.

---

## ▶️ Ejecución
Para ejecutar todo el pipeline de forma automática desde la carpeta raíz mediante **cmd**:

```bash
run_proyecto.bat

