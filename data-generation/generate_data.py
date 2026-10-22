"""Generador de datos sintéticos de FinBank. Uso: python data-generation/generate_data.py"""
import json

from faker import Faker

from common import REPO_DIR, load_config, make_rng, write_table
from master_tables import generate_clientes, generate_productos, generate_sucursales
from transactional_tables import generate_comisiones, generate_movimientos, generate_obligaciones


def main():
    cfg = load_config()
    rng = make_rng(cfg["seed"])
    Faker.seed(cfg["seed"])
    fake = Faker("es_CO")
    anomalies = {}

    # El orden importa: las tablas transaccionales dependen de las maestras
    productos = generate_productos(cfg, rng)
    sucursales = generate_sucursales(cfg, rng)
    clientes = generate_clientes(cfg, rng, fake, anomalies)
    obligaciones = generate_obligaciones(cfg, rng, clientes, productos, anomalies)
    movimientos = generate_movimientos(cfg, rng, clientes, productos, anomalies)
    comisiones = generate_comisiones(cfg, rng, obligaciones, movimientos, productos)

    tables = {
        "TB_CLIENTES_CORE": clientes,
        "TB_PRODUCTOS_CAT": productos,
        "TB_MOV_FINANCIEROS": movimientos,
        "TB_OBLIGACIONES": obligaciones,
        "TB_SUCURSALES_RED": sucursales,
        "TB_COMISIONES_LOG": comisiones,
    }

    for name, df in tables.items():
        path = write_table(df, name, cfg)
        print(f"{name}: {len(df):,} filas -> {path}")

    log_path = REPO_DIR / cfg["output"]["path"] / "anomalies_log.json"
    log_path.write_text(json.dumps(anomalies, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Anomalías registradas en {log_path}")


if __name__ == "__main__":
    main()