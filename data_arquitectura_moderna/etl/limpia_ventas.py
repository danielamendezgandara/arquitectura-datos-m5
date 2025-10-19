#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Limpieza de datos crudos: ventas.csv
------------------------------------
Uso:
  python etl\clean_ventas.py [--in ruta_csv] [--out ruta_csv] [--sep ,] [--enc utf-8]

Lee un CSV crudo (por defecto: datalake/datos_crudos/ventas.csv), normaliza tipos y fecha,
valida reglas básicas y guarda en datalake/datos_procesados/ventas_limpio.csv
"""
import argparse
import pandas as pd
from pathlib import Path

def parse_fecha_flexible(s: str):
    # Probar varios formatos comunes; cae a inferencia con dayfirst
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(s, format=fmt, errors="raise")
        except Exception:
            pass
    return pd.to_datetime(s, errors="coerce", dayfirst=True)

def limpiar_fecha(fecha):
    import pandas as pd
    if pd.isna(fecha):
        return pd.NaT
    s = str(fecha).strip()

    # Vacíos y marcadores comunes
    if s in ("", "NA", "N/A", "--", "None", "null"):
        return pd.NaT

    # Normalizar separadores a "/"
    s = s.replace("\\", "/").replace(".", "/").replace("-", "/")

    # Intentos con formatos más comunes
    formatos = ("%Y/%m/%d", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y")
    for fmt in formatos:
        try:
            return pd.to_datetime(s, format=fmt, errors="raise")
        except Exception:
            pass
    return pd.to_datetime(s, errors="coerce", dayfirst=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", default="datalake/datos_crudos/ventas.csv")
    parser.add_argument("--out", dest="out", default="datalake/datos_procesados/ventas_limpio.csv")
    parser.add_argument("--sep", default=",")
    parser.add_argument("--enc", default="utf-8")
    args = parser.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inp, sep=args.sep, encoding=args.enc)

    # Columnas esperadas: id_venta,id_producto,id_sucursal,fecha,cantidad,monto
    ren = {c: c.strip().lower() for c in df.columns}
    df = df.rename(columns=ren)

    # Tipos numericos
    for c in ["id_venta","id_producto","id_sucursal","cantidad"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    if "monto" in df.columns:
        # Quitar simbolos de moneda y miles
        df["monto"] = df["monto"].astype(str).str.replace(r"[\$\.,](?=\d{3}(\D|$))", "", regex=True)\
                                      .str.replace(",", ".", regex=False)
        df["monto"] = pd.to_numeric(df["monto"], errors="coerce")

    # Fecha
    if "fecha" in df.columns:
    # 1) Aplicar limpieza robusta
        df["fecha"] = df["fecha"].apply(limpiar_fecha)

    # 2) Enforzar rango razonable
        lim_inf = pd.Timestamp("2000-01-01")
        lim_sup = pd.Timestamp.today().normalize() + pd.Timedelta(days=1)
        mask = df["fecha"].between(lim_inf, lim_sup)
        df.loc[~mask, "fecha"] = pd.NaT

    # 3) (opcional) diagnóstico rápido en consola
        validez = (df["fecha"].notna().mean() * 100)
        print(f"Validez fecha tras limpieza: {validez:.1f}%")
        malos = df.loc[df["fecha"].isna(), "fecha"].shape[0]
        if malos:
           top = (df.loc[df["fecha"].isna()].index.size)
           print(f"Fechas no parseables (NaT): {malos}")


    # Reglas de negocio: no negativos
    if "cantidad" in df.columns:
        df.loc[df["cantidad"] < 0, "cantidad"] = pd.NA
    if "monto" in df.columns:
        df.loc[df["monto"] < 0, "monto"] = pd.NA

    # Unicidad id_venta
    before = len(df)
    if "id_venta" in df.columns:
        df = df.drop_duplicates(subset=["id_venta"], keep="first")
    after = len(df)

    print(f"Filas originales: {before} | tras deduplicar por id_venta: {after}")
    if "fecha" in df.columns:
        print(f"Validez fecha (no nulos): {(df['fecha'].notna().mean()*100):.0f}%")

    df.to_csv(out, index=False, date_format="%Y-%m-%d")
    print('Guardado:', out.resolve())

if __name__ == "__main__":
    main()
