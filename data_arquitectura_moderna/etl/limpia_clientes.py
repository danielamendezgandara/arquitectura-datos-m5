#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Limpieza de datos crudos: clientes.csv
--------------------------------------
Uso:
  python etl\clean_clientes.py [--in ruta_csv] [--out ruta_csv] [--sep ,] [--enc utf-8]

Lee un CSV crudo (por defecto: datalake/datos_crudos/clientes.csv), normaliza tipos y texto,
elimina duplicados por id_cliente y guarda en datalake/datos_procesados/clientes_limpio.csv
"""
import argparse
import pandas as pd
from pathlib import Path

def norm_str(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", default="datalake/datos_crudos/clientes.csv")
    parser.add_argument("--out", dest="out", default="datalake/datos_procesados/clientes_limpio.csv")
    parser.add_argument("--sep", default=",")
    parser.add_argument("--enc", default="utf-8")
    args = parser.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inp, sep=args.sep, encoding=args.enc)

    # Columnas esperadas: id_cliente,nombre,edad,ubicacion,categoria
    # Normalizar headers (tolerar mayúsculas/espacios)
    ren = {c: c.strip().lower() for c in df.columns}
    df = df.rename(columns=ren)

    # Renombres comunes
    df = df.rename(columns={
        "customer_id":"id_cliente",
        "cliente_id":"id_cliente",
        "customername":"nombre",
        "customer_name":"nombre"
    })

    # Asegurar columnas
    for col in ["id_cliente","nombre","edad","ubicacion","categoria"]:
        if col not in df.columns:
            df[col] = pd.NA

    # Tipos
    df["id_cliente"] = pd.to_numeric(df["id_cliente"], errors="coerce").astype("Int64")
    df["edad"] = pd.to_numeric(df["edad"], errors="coerce").astype("Int64")

    # Texto
    for c in ["nombre","ubicacion","categoria"]:
        df[c] = norm_str(df[c]).replace({"<NA>": pd.NA})

    # Reglas básicas
    # - Edad razonable 0..120
    mask_bad_age = df["edad"].notna() & ~df["edad"].between(0,120)
    df.loc[mask_bad_age, "edad"] = pd.NA

    # Deduplicar por id_cliente (mantener primera)
    before = len(df)
    df = df.drop_duplicates(subset=["id_cliente"], keep="first")
    after = len(df)

    print(f"Filas originales: {before} | tras deduplicar por id_cliente: {after}")
    print(f"Nulos en columnas clave -> id_cliente: {df['id_cliente'].isna().sum()}, nombre: {df['nombre'].isna().sum()}")

    df.to_csv(out, index=False)
    print('Guardado:', out.resolve())

if __name__ == "__main__":
    main()
