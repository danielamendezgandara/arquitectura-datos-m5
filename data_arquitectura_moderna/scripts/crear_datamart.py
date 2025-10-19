# scripts/crear_datamart.py
import pandas as pd
from pathlib import Path

curated = Path("datalake/datos_curados")
datamart = Path("datamart")
datamart.mkdir(exist_ok=True)

# Carga datos curados generados por etl/transformacion.py
hecho_ventas = pd.read_csv(curated / "hecho_ventas.csv")          # id_venta,id_cliente,id_producto,id_tiempo,cantidad,total
dim_producto = pd.read_csv(curated / "dim_producto.csv")          # id_producto,nombre_producto,categoria,proveedor
dim_tiempo = pd.read_csv(curated / "dim_tiempo.csv")              # id_tiempo,fecha,anio,mes,dia

# Join para análisis
df = (hecho_ventas
      .merge(dim_producto[["id_producto","categoria"]], on="id_producto", how="left")
      .merge(dim_tiempo[["id_tiempo","anio","mes"]], on="id_tiempo", how="left"))

# Data Mart 1: ventas mensuales por categoría
mart_mes_categoria = (df.groupby(["anio","mes","categoria"], as_index=False)
                        .agg(total_ventas=("total","sum"),
                             unidades=("cantidad","sum"))
                        .sort_values(["anio","mes","categoria"]))
mart_mes_categoria.to_csv(datamart / "mart_ventas_mes_categoria.csv", index=False)

# Data Mart 2: ventas anuales por categoría
mart_anio_categoria = (df.groupby(["anio","categoria"], as_index=False)
                         .agg(total_ventas=("total","sum"),
                              unidades=("cantidad","sum"))
                         .sort_values(["anio","total_ventas"], ascending=[True, False]))
mart_anio_categoria.to_csv(datamart / "mart_ventas_anio_categoria.csv", index=False)

print("✅ Data Marts generados en", datamart.resolve())
