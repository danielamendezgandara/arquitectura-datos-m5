#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico de calidad: ventas.csv
----------------------------------
Uso:
  python etl/diagnostico_ventas.py [ruta_csv]

Entrega:
  - diagnostico_calidad_ventas.csv
  - diagnostico_calidad_ventas.md
"""
import sys
import pandas as pd ,re
from pathlib import Path

def pct(x): return f"{x:.0f}%"

def completitud(s): return s.notna().mean() * 100

def validez_no_vacio(s):
    return (s.astype(str).str.strip().ne("") & s.notna()).mean() * 100

def validez_numerico(s):
    return pd.to_numeric(s, errors="coerce").notna().mean() * 100

def validez_fecha(s):
    # 1) Si ya es datetime, no reparsear
    if pd.api.types.is_datetime64_any_dtype(s):
        return s.notna().mean() * 100
    # 2) Si la mayoría viene como 'YYYY-MM-DD', no reparsear (cuenta como válido)
    is_iso = s.astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    if is_iso.notna().any():
        return is_iso.fillna(False).mean() * 100
    # 3) Si es texto variado, intenta parsear
    v = pd.to_datetime(s.astype(str).str.strip(), errors="coerce", dayfirst=True)
    return v.notna().mean() * 100

def duplicados_por_valor(s):
    return int(s.duplicated().sum())

def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("datos_origen/ventas.csv")
    if not csv_path.exists():
        print(f"ERROR: No se encuentra {csv_path.resolve()}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # Mostramos las primeras 9 filas del DataFrame original para tener una vista inicial del contenido
    print ("Dataframe")
    print(df.head(9))

    # Columnas esperadas
    cols = {
        "id_venta":     ("numerico",),
        "id_producto":  ("numerico",),
        "id_sucursal":  ("numerico",),  # si fuera texto, cambiar a "no_vacio"
        "fecha":        ("fecha",),
        "cantidad":     ("numerico",),
        "monto":        ("numerico",)
    }

    filas = []
    for c, rules in cols.items():
        if c not in df.columns:
            continue
        comp = completitud(df[c])
        if "fecha" in rules:
            val = validez_fecha(df[c])
        elif "numerico" in rules:
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
    print("\nDiagnóstico ventas.csv")
    if not tabla.empty:
        print(tabla.to_string(index=False))
    else:
        print("No se encontraron columnas esperadas.")

    # Reglas de negocio simples
    problemas = {}
    if "cantidad" in df.columns:
        n = int((pd.to_numeric(df["cantidad"], errors="coerce") < 0).sum())
        if n: problemas["cantidad_negativa"] = n
    if "monto" in df.columns:
        n = int((pd.to_numeric(df["monto"], errors="coerce") < 0).sum())
        if n: problemas["monto_negativo"] = n

    if problemas:
        print("\nCheques de negocio:")
        for k, v in problemas.items():
            print(f" - {k}: {v} filas")

    filas_dup = int(df.duplicated().sum())
    print(f"\nDuplicados de filas completas: {filas_dup}")

    # Guardar CSV y MD
    base = "reportes_datos_crudos/diagnostico_calidad_ventas"
    df_csv = tabla.copy()
    if not df_csv.empty:
        for col in ["Completitud (%)","Validez (%)"]:
            df_csv[col] = df_csv[col].str.replace("%","", regex=False).astype(float)
        df_csv.to_csv(base + ".csv", index=False)
        try:
            with open(base + ".md","w",encoding="utf-8") as f:
                f.write("## Diagnóstico ventas.csv\n\n")
                f.write(tabla.to_markdown(index=False))
                f.write(f"\n\nDuplicados de filas completas: {filas_dup}\n")
                if problemas:
                    f.write("\n### Cheques de negocio\n")
                    for k, v in problemas.items():
                        f.write(f"- {k}: {v} filas\n")
        except Exception as e:
            print(f"(Aviso) No se pudo escribir Markdown: {e}")

    # Señal rápida de problemas
    if not tabla.empty:
        t = tabla.copy()
        t["Val_num"] = t["Validez (%)"].str.replace("%","", regex=False).astype(float)
        peor = t.sort_values("Val_num").iloc[0]["Campo"]
        if peor == "id_venta":
            dim = "Integridad/Unicidad de claves"
            imp = "Ventas duplicadas o inválidas distorsionan todas las métrricas."
        elif peor == "fecha":
            dim = "Consistencia temporal"
            imp = "Fechas inválidas rompen series de tiempo y agregaciones."
        elif peor in ("cantidad","monto"):
            dim = "Exactitud de medidas"
            imp = "Valores inválidos afectan KPIs (ingresos, unidades)."
        else:
            dim = "Completitud/Consistencia"
            imp = "Campos vacíos degradan la calidad del análisis."
        print(f"\nCampo con más problemas: {peor}")
        print(f"Dimensión afectada: {dim}")
        print(f"Impacto potencial: {imp}")

if __name__ == "__main__":
    main()
