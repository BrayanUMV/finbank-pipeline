"""Generador de datos sintéticos de FinBank. Uso: python data-generation/generate_data.py"""
import json

from faker import Faker

from common import REPO_DIR, load_config, make_rng, write_table
from master_tables import generate_clientes, generate_productos, generate_sucursales


def main():
    cfg = load_config()
    rng = make_rng(cfg["seed"])
    Faker.seed(cfg["seed"])
    fake = Faker("es_CO")
    anomalies = {}

    tables = {
        "TB_PRODUCTOS_CAT": generate_productos(cfg, rng),
        "TB_SUCURSALES_RED": generate_sucursales(cfg, rng),
        "TB_CLIENTES_CORE": generate_clientes(cfg, rng, fake, anomalies),
    }

    for name, df in tables.items():
        path = write_table(df, name, cfg)
        print(f"{name}: {len(df):,} filas -> {path}")

    log_path = REPO_DIR / cfg["output"]["path"] / "anomalies_log.json"
    log_path.write_text(json.dumps(anomalies, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Anomalías registradas en {log_path}")


if __name__ == "__main__":
    main()