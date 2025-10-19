
# Informe Final - Arquitectura de Datos Moderna

## 1. Introducción
El objetivo de este proyecto fue implementar, de manera conceptual y simplificada, una arquitectura de datos moderna que permita transformar datos crudos en información valiosa para la toma de decisiones. 

Se diseñó un flujo completo desde la ingesta de datos hasta la visualización, siguiendo buenas prácticas y utilizando herramientas de libre acceso.

## 2. Flujo de Datos
1. **Origen de datos (crudos)**: Archivos CSV sintéticos (`datos_crudos/`).
2. **Ingesta**: Se copiaron al Data Lake en la zona *datos_crudos* mediante el script `etl/ingesta.py`.
3. **Limpieza**: Se eliminaron duplicados, se validaron tipos y formatos (especialmente fechas), normalización de texto. Con `etl/limpia_clientes.py`, `etl/limpia_productos.py` y `etl/limpia_ventas.py` se limpiaron los datos generando datos limpios en la zona *datos_procesados*.
3. **Transformación (ETL)**: Con `etl/transforma.py` se estructuraron los datos, generando dimensiones y hechos en la zona *datos_curados*.
4. **Data Warehouse (DW)**: Se implementó un modelo estrella en PostgreSQL (`dw/esquema.sql`) y se cargaron los datos con `dw/load_dw.py`.
5. **Data Mart**: Se crearon CSV derivados con métricas agregadas (`scripts/crear_datamart.py`).
6. **Visualización**: Gráficos de ventas por categoría y por año (`scripts/visualiza.py`).

## 3. Herramientas Utilizadas
- **Lenguaje**: Python 3.x
- **Base de datos**: PostgreSQL (modelo estrella)
- **Bibliotecas**: pandas, matplotlib, psycopg2 ,tabulate , numpy , SQLAlchemy , psycopg2-binary
- **Modelado**: draw.io
- **Almacenamiento**: Estructura de carpetas simulando Data Lake (datos_crudos,datos_procesados, datos_curados)

## 4. Justificación de Decisiones Técnicas
- **Python**: Flexibilidad para el ETL y amplia comunidad.
- **PostgreSQL**: Base de datos relacional robusta y gratuita, ideal para DW.
- **Modelo estrella**: Simplifica consultas y análisis multidimensional.
- **CSV para Data Mart**: Portabilidad y fácil consumo en herramientas de BI.

## 5. Resultados y Hallazgos
- **Consultas más fáciles**: ventas por categoría/mes, comparaciones año a año
- **Métricas clave**: crecimiento mensual, productos más vendidos, tendencias estacionales.
- **Visualización**: gráficos claros que muestran patrones de ventas por categoría y periodo.

## 6. Recomendaciones Finales
- Automatizar el flujo ETL con un orquestador (por ejemplo, Apache Airflow).
- Integrar herramientas BI como Metabase o Superset para dashboards interactivos.
- Escalar el Data Lake a almacenamiento en la nube (AWS S3, Azure Data Lake) en proyectos reales.

## 7. Conclusiones
El proyecto demuestra que con un diseño estructurado, incluso una implementación simplificada puede ofrecer una visión clara y útil para la toma de decisiones. La arquitectura propuesta es flexible, escalable y adaptable a diferentes escenarios.

---
**Autor**: Daniela Méndez  
**Fecha**: Agosto 2025
