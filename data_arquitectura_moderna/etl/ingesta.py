import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
seed = BASE / "datos_origen"
raw = BASE / "datalake" / "datos_crudos"
raw.mkdir(parents=True, exist_ok=True)

for name in ["clientes.csv", "productos.csv", "ventas.csv"]:
    src = seed / name
    dst = raw / name
    if not src.exists():
        raise FileNotFoundError(f"No existe {src}")
    shutil.copy2(src, dst)
    print(f"Ingestado: {src.name} -> {dst}")
print("Ingesta completada ✅")
