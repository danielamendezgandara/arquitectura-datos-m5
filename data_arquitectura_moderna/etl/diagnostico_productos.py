#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico de calidad: productos.csv
-------------------------------------
Uso:
  python etl/diagnostico_productos.py [ruta_csv]

Entrega:
  - diagnostico_calidad_productos.csv
  - diagnostico_calidad_productos.md
"""
import sys
import pandas as pd
from pathlib import Path

def pct(x): return f"{x:.0f}%"

def completitud(s): return s.notnull().mean() * 100

def validez_no_vacio(s):
    return (s.astype(str).str.strip().ne("") & s.notnull()).mean() * 100

def validez_numerico(s):
    return pd.to_numeric(s, errors="coerce").notnull().mean() * 100

def duplicados_por_valor(s):
    return int(s.duplicated().sum())

def main():
    csv = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("datos_origen/productos.csv")
    if not csv.exists():
        print(f"ERROR: No se encuentra {csv.resolve()}")
        sys.exit(1)

    df = pd.read_csv(csv)

    # Columnas esperadas
    cols = {
        "id_producto": ("numerico",),
        "nombre_producto": ("no_vacio",),
        "categoria": ("no_vacio",),
        "proveedor": ("no_vacio",)
    }

    filas = []
    for c, rules in cols.items():
        if c not in df.columns: 
            continue
        comp = completitud(df[c])
        if "numerico" in rules:
            val = validez_numerico(df[c])
        else:
            val = validez_no_vacio(df[c])
        dups = duplicados_por_valor(df[c])
        filas.append({
            "Campo": c,
            "Completitud (%)": pct(comp),
            "Validez (%)": pct(val),
            "Duplicados": dups
        })

    tabla = pd.DataFrame(filas, columns=["Campo","Completitud (%)","Validez (%)","Duplicados"])
    print("\nDiagnóstico productos.csv")
    if not tabla.empty:
        print(tabla.to_string(index=False))
    else:
        print("No se encontraron columnas esperadas.")

    # Extras
    filas_dup = int(df.duplicated().sum())
    print(f"\nDuplicados de filas completas: {filas_dup}")

    # Guardar CSV (numérico) y Markdown
    base = "reportes_datos_crudos/diagnostico_calidad_productos"
    df_csv = tabla.copy()
    if not df_csv.empty:
        for col in ["Completitud (%)","Validez (%)"]:
            df_csv[col] = df_csv[col].str.replace("%","", regex=False).astype(float)
        df_csv.to_csv(base + ".csv", index=False)
        try:
            with open(base + ".md","w",encoding="utf-8") as f:
                f.write("## Diagnóstico productos.csv\n\n")
                f.write(tabla.to_markdown(index=False))
                f.write(f"\n\nDuplicados de filas completas: {filas_dup}\n")
        except Exception as e:
            print(f"(Aviso) No se pudo escribir Markdown: {e}")

    # Señal rápida de problemas
    if not tabla.empty:
        t = tabla.copy()
        t["Val_num"] = t["Validez (%)"].str.replace("%","", regex=False).astype(float)
        peor = t.sort_values("Val_num").iloc[0]["Campo"]
        if peor == "id_producto":
            dim = "Integridad/Unicidad de claves"
            imp = "IDs inválidos o duplicados afectan joins y el DW."
        elif peor == "categoria":
            dim = "Consistencia semántica"
            imp = "Categorías mal definidas dañan segmentaciones y reportes."
        else:
            dim = "Completitud/Consistencia"
            imp = "Campos vacíos degradan la calidad de análisis."
        print(f"\nCampo con más problemas: {peor}")
        print(f"Dimensión afectada: {dim}")
        print(f"Impacto potencial: {imp}")

if __name__ == "__main__":
    main()
