#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diagnóstico de calidad de datos con Pandas
------------------------------------------
Uso:
    python etl/diagnostico_clientes.py [ruta_csv]

- Auto-detecta columnas típicas: id_cliente/cliente_id/id, nombre/name
- Calcula: Completitud, Validez (por tipo) y Duplicados
- Imprime una tabla estilo consola y guarda:
    - diagnostico_calidad_clientes.csv
    - diagnostico_calidad_clientes.md
"""

import sys
import re
import pandas as pd
from pathlib import Path

# ---------- Utilidades ----------
def detectar_columna(df, posibles):
    """
    Devuelve el primer nombre de columna existente en df que coincida con alguno en 'posibles' (case-insensitive).
    Si no encuentra, retorna None.
    """
    lower_map = {c.lower(): c for c in df.columns}
    for p in posibles:
        if p.lower() in lower_map:
            return lower_map[p.lower()]
    return None

# Calculamos el porcentaje de valores no nulos por columna (completitud)
# Esto permite detectar campos incompletos en el dataset
def calcular_completitud(serie: pd.Series) -> float:
    return serie.notnull().mean() * 100

def calcular_validez(serie: pd.Series, tipo: str) -> float:
    tipo = (tipo or "no_vacio").lower()
    if tipo in ("no_vacio", "nonempty"):
        validos = serie.astype(str).str.strip().ne("") & serie.notna()
    elif tipo in ("numerico", "numeric", "int", "float"):
        # válido si es convertible a número
        validos = pd.to_numeric(serie, errors="coerce").notna()
    else:
        # Por defecto: no vacío
        validos = serie.astype(str).str.strip().ne("") & serie.notna()
    return validos.mean() * 100

def contar_duplicados(serie: pd.Series) -> int:
    # filas duplicadas por valor (cuenta cuántas filas están marcadas como duplicadas, excluyendo la primera de cada grupo)
    # Es una forma de evaluar la unicidad del dataset
    return int(serie.duplicated().sum())

def formatea_porcentaje(x: float) -> str:
    return f"{x:.0f}%"

def imprimir_tabla(df_table: pd.DataFrame, titulo="Resumen de calidad de datos:"):
    print("\n" + titulo)
    # Usa to_string para imitar la tabla del enunciado
    print(df_table.to_string(index=False))

def guardar_salidas(df_table: pd.DataFrame, base="reportes_datos_crudos/diagnostico_calidad_clientes"):
    # Guardar como CSV y Markdown
    # Convertimos columnas de porcentaje a float para el CSV "numérico"
    df_csv = df_table.copy()
    for col in df_csv.columns:
        if isinstance(df_csv[col].iloc[0], str) and df_csv[col].iloc[0].endswith("%"):
            df_csv[col] = df_csv[col].str.replace("%", "", regex=False).astype(float)
    df_csv.to_csv(f"{base}.csv", index=False)

    try:
        with open(f"{base}.md", "w", encoding="utf-8") as f:
            f.write("## Resumen de calidad de datos\n\n")
            f.write(df_table.to_markdown(index=False))
            f.write("\n")
    except Exception as e:
        print(f"(Aviso) No se pudo escribir Markdown: {e}")

def diagnostico(df: pd.DataFrame, reglas: dict) -> pd.DataFrame:
    filas = []
    for col, tipo in reglas.items():
        if col not in df.columns:
            continue
        comp = calcular_completitud(df[col])
        val  = calcular_validez(df[col], tipo)
        dups = contar_duplicados(df[col])
        filas.append({
            "Campo": col,
            "Completitud (%)": formatea_porcentaje(comp),
            "Validez (%)": formatea_porcentaje(val),
            "Duplicados": dups
        })
    return pd.DataFrame(filas, columns=["Campo", "Completitud (%)", "Validez (%)", "Duplicados"])

def main():
    # 1) CSV de entrada
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("datos_origen/clientes.csv")
    if not csv_path.exists():
        print(f"ERROR: No se encuentra el archivo CSV: {csv_path.resolve()}")
        print("Pásalo como argumento o renómbralo a 'clientes.csv'.")
        sys.exit(1)

    # 2) Leer datos
    df = pd.read_csv(csv_path)

    # Mostramos las primeras 9 filas del DataFrame original para tener una vista inicial del contenido
    print ("Dataframe")
    print(df.head(9))

    # 3) Auto-detección de columnas
    col_id      = detectar_columna(df, ["id_cliente", "cliente_id", "id", "idCliente"])
    col_nombre  = detectar_columna(df, ["nombre", "name", "full_name"])

    # Construir las reglas según lo que encontremos
    reglas = {}
    if col_nombre: reglas[col_nombre] = "no_vacio"
    if col_id:     reglas[col_id]     = "no_vacio"  # la unicidad la aproximamos con "duplicados"

    # Si no detectamos nada, toma todas las columnas como "no_vacio"
    if not reglas:
        reglas = {c: "no_vacio" for c in df.columns}

    # 4) Diagnóstico
    tabla = diagnostico(df, reglas)

    # 5) Impresión y guardado
    imprimir_tabla(tabla)

    # Campo con menor validez
    if not tabla.empty:
        tmp = tabla.copy()
        tmp["Validez_num"] = tmp["Validez (%)"].str.replace("%", "", regex=False).astype(float)
        campo_mas_problemas = tmp.sort_values("Validez_num").iloc[0]["Campo"]
        # Sugerencia de dimensión
        if campo_mas_problemas == col_id:
            dimension = "Unicidad/Integridad"
            impacto = "Confusión de clientes, duplicidad en reportes y errores de facturación."
        elif campo_mas_problemas == col_nombre:
            dimension = "Completitud/Consistencia"
            impacto = "Dificultad para personalizar comunicaciones y segmentar correctamente."
        else:
            dimension = "Calidad del Dato"
            impacto = "Impacto general en reportes y toma de decisiones."

        print(f"\nCampo con más problemas: {campo_mas_problemas}")
        print(f"Dimensión de calidad más comprometida: {dimension}")
        print(f"Posibles consecuencias: {impacto}")

    guardar_salidas(tabla)

if __name__ == "__main__":
    main()
