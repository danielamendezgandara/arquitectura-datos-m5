#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Limpieza de datos crudos: productos.csv
---------------------------------------
Uso:
  python etl\limpia_productos.py [--in ruta_csv] [--out ruta_csv] [--sep ,] [--enc utf-8]

Lee un CSV crudo (por defecto: datalake/datos_crudos/productos.csv), normaliza tipos y texto,
elimina duplicados por id_producto y guarda en datalake/datos_procesados/productos_limpio.csv
"""
import argparse
import pandas as pd
from pathlib import Path

def norm_str(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", default="datalake/datos_crudos/productos.csv")
    parser.add_argument("--out", dest="out", default="datalake/datos_procesados/productos_limpio.csv")
    parser.add_argument("--sep", default=",")
    parser.add_argument("--enc", default="utf-8")
    args = parser.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inp, sep=args.sep, encoding=args.enc)

    # Columnas esperadas: id_producto,nombre_producto,categoria,proveedor
    ren = {c: c.strip().lower() for c in df.columns}
    df = df.rename(columns=ren)
    df = df.rename(columns={
        "product_id":"id_producto",
        "id":"id_producto",
        "nombre":"nombre_producto",
        "product_name":"nombre_producto",
        "supplier":"proveedor"
    })

    for col in ["id_producto","nombre_producto","categoria","proveedor"]:
        if col not in df.columns:
            df[col] = pd.NA

    df["id_producto"] = pd.to_numeric(df["id_producto"], errors="coerce").astype("Int64")

    for c in ["nombre_producto","categoria","proveedor"]:
        df[c] = norm_str(df[c]).replace({"<NA>": pd.NA})

    # Deduplicar por id_producto
    before = len(df)
    df = df.drop_duplicates(subset=["id_producto"], keep="first")
    after = len(df)

    print(f"Filas originales: {before} | tras deduplicar por id_producto: {after}")
    print(f"Nulos clave -> id_producto: {df['id_producto'].isna().sum()}, nombre_producto: {df['nombre_producto'].isna().sum()}")

    df.to_csv(out, index=False)
    print('Guardado:', out.resolve())

if __name__ == "__main__":
    main()
