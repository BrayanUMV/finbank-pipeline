"""Carga los datos sintéticos en PostgreSQL (fuente origen del pipeline).
Uso: python data-generation/load_to_postgres.py"""
import os
import io
import time
from datetime import datetime

import pandas as pd
import psycopg2
from dotenv import dotenv_values

from common import BASE_DIR, REPO_DIR, load_config

# El orden respeta las llaves foráneas: primero las tablas padre
LOAD_ORDER = ["TB_PRODUCTOS_CAT", "TB_SUCURSALES_RED", "TB_CLIENTES_CORE",
              "TB_OBLIGACIONES", "TB_COMISIONES_LOG", "TB_MOV_FINANCIEROS"]


def connect():
    env = dotenv_values(BASE_DIR / os.environ.get("ENV_FILE", ".env"))
    return psycopg2.connect(host=env.get("POSTGRES_HOST", "localhost"), port=5432,
                            user=env["POSTGRES_USER"], password=env["POSTGRES_PASSWORD"],
                            dbname=env["POSTGRES_DB"], sslmode=env.get("POSTGRES_SSLMODE", "prefer"))

def create_schema(conn):
    sql = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def read_table(name, cfg):
    raw = REPO_DIR / cfg["output"]["path"]
    if name in cfg["output"]["csv_tables"]:
        # Todo como texto para no alterar valores; las celdas vacías se cargan como NULL
        return pd.read_csv(raw / f"{name}.csv", dtype=str, keep_default_na=False)
    return pd.read_parquet(raw / f"{name}.parquet")


def load_table(conn, name, cfg):
    df = read_table(name, cfg)
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False)
    buf.seek(0)
    cols = ", ".join(df.columns)
    with conn.cursor() as cur:
        cur.copy_expert(f"COPY {name} ({cols}) FROM STDIN WITH (FORMAT csv, NULL '')", buf)
    conn.commit()
    return len(df)


def main():
    cfg = load_config()
    conn = connect()
    create_schema(conn)

    for name in LOAD_ORDER:
        t = time.time()
        n = load_table(conn, name, cfg)
        print(f"{name}: {n:,} filas cargadas en {time.time() - t:.1f} s")

    lines = [f"Evidencia de carga - {datetime.now():%Y-%m-%d %H:%M}", ""]
    with conn.cursor() as cur:
        for name in LOAD_ORDER:
            cur.execute(f"SELECT COUNT(*) FROM {name}")
            lines.append(f"SELECT COUNT(*) FROM {name}; -> {cur.fetchone()[0]:,}")
    conn.close()

    docs = REPO_DIR / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "evidencia_fase1_conteos.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()