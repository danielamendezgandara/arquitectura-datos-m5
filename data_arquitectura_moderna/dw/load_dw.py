import os
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
curated = BASE / "datalake" / "datos_curados"
dw_sql = (BASE / "dw" / "esquema.sql").read_text(encoding="utf-8")

PGHOST = os.getenv("PGHOST","localhost")
PGPORT = os.getenv("PGPORT","5432")
PGUSER = os.getenv("PGUSER","postgres")
PGPASSWORD = os.getenv("PGPASSWORD","admin")
PGDATABASE = os.getenv("PGDATABASE","ventas_olap")

url = f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
engine = create_engine(url, future=True)

with engine.begin() as conn:
    conn.execute(text(dw_sql))

dfs = {
    "dim_cliente": pd.read_csv(curated / "dim_cliente.csv"),
    "dim_producto":  pd.read_csv(curated / "dim_producto.csv"),
    "dim_tiempo":     pd.read_csv(curated / "dim_tiempo.csv", parse_dates=["fecha"]),
    "hecho_ventas":   pd.read_csv(curated / "hecho_ventas.csv")
}
for table, df in dfs.items():
    df.to_sql(table, engine, if_exists="append", index=False)
    print(f"Cargado: {table} ({len(df)} filas)")

print("Carga al DW completada ✅")
