# scripts/visualiza.py
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

dm = Path("datamart")
viz = Path("viz")
viz.mkdir(exist_ok=True)

# Gráfico 1: ventas mensuales por categoría (gráfico de línea por categoría)
df = pd.read_csv(dm / "mart_ventas_mes_categoria.csv")  # año, mes, categoria, total_ventas, unidades
df["yyyymm"] = df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2)
pivot = df.pivot_table(index="yyyymm", columns="categoria", values="total_ventas", aggfunc="sum").fillna(0)

plt.figure(figsize=(10,6))
for col in pivot.columns:
    plt.plot(pivot.index, pivot[col], label=col)
plt.title("Ventas por mes y categoría")
plt.xlabel("Mes")
plt.ylabel("Total ventas")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(viz / "ventas_mes_categoria.png", dpi=160)
plt.close()

# Gráfico 2: Gráfico de barra por año (total categoría)
annual = pd.read_csv(dm / "mart_ventas_anio_categoria.csv")
for y in sorted(annual["anio"].unique()):
    subset = annual[annual["anio"] == y].sort_values("total_ventas", ascending=False)
    plt.figure(figsize=(8,5))
    plt.bar(subset["categoria"], subset["total_ventas"])
    plt.title(f"Ventas por categoría - {y}")
    plt.xlabel("Categoría")
    plt.ylabel("Total ventas")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(viz / f"ventas_categoria_{y}.png", dpi=160)
    plt.close()

print("✅ Gráficos generados en", viz.resolve())
