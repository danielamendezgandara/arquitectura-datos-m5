import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
raw = BASE / "datalake" / "datos_crudos"
processed = BASE / "datalake" / "datos_procesados"
curated = BASE / "datalake" / "datos_curados"

processed.mkdir(parents=True, exist_ok=True)
curated.mkdir(parents=True, exist_ok=True)

clientes = pd.read_csv(processed / "clientes_limpio.csv")
productos  = pd.read_csv(processed / "productos_limpio.csv")
ventas   = pd.read_csv(processed / "ventas_limpio.csv", parse_dates=["fecha"])

clientes["nombre_cliente"] = clientes["nombre"].str.strip()
productos["nombre_producto"] = productos["nombre_producto"].str.strip()
# Renombrar columnas
clientes.rename(columns={'nombre': 'nombre_cliente'}, inplace=False)
ventas.rename(columns={'id_sucursal': 'id_cliente'}, inplace=True)
ventas.rename(columns={'monto': 'total'}, inplace=True)

quality_report = pd.DataFrame({
    "rows": [len(ventas)],
    "null_cliente": [int(ventas["id_cliente"].isna().sum())],
    "null_producto":  [int(ventas["id_producto"].isna().sum())],
    "total_mismatch":[int(ventas["total"].sum())]
})
processed.mkdir(parents=True, exist_ok=True)
quality_report.to_csv(processed / "quality_report.csv", index=False)

# Dimensiones
dim_cliente= clientes[["id_cliente","nombre_cliente","edad","ubicacion","categoria"]].drop_duplicates()
dim_producto = productos[["id_producto","nombre_producto","categoria","proveedor"]].drop_duplicates()

dim_tiempo = ventas[["fecha"]].drop_duplicates()
dim_tiempo["anio"]  = dim_tiempo["fecha"].dt.year
dim_tiempo["mes"] = dim_tiempo["fecha"].dt.month
dim_tiempo["dia"]   = dim_tiempo["fecha"].dt.day
dim_tiempo = dim_tiempo.sort_values("fecha").reset_index(drop=True)
dim_tiempo["id_tiempo"] = (dim_tiempo["fecha"].dt.strftime("%Y%m%d")).astype(int)
dim_tiempo = dim_tiempo[["id_tiempo","fecha","anio","mes","dia"]]

ventas["id_tiempo"] = ventas["fecha"].dt.strftime("%Y%m%d").astype(int)
# Hechos ventas
hecho_ventas = ventas[[
    "id_venta","id_cliente","id_producto","id_tiempo","cantidad","total"
]].copy()

dim_cliente.to_csv(curated / "dim_cliente.csv", index=False)
dim_producto.to_csv(curated / "dim_producto.csv", index=False)
dim_tiempo.to_csv(curated / "dim_tiempo.csv", index=False)
hecho_ventas.to_csv(curated / "hecho_ventas.csv", index=False)

print("Transformaciones listas ✅")
print(f"Curated: {curated}")
