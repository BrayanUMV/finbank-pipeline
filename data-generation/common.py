"""Utilidades compartidas del generador de datos sintéticos de FinBank."""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent


def load_config(path=None):
    """Lee config.yaml con todos los parámetros de generación."""
    path = Path(path) if path else BASE_DIR / "config.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def make_rng(seed):
    """Generador aleatorio con semilla fija: mismos datos en cada ejecución."""
    return np.random.default_rng(seed)


def inject_nulls(df, columns, rate, rng):
    """Introduce ~rate% de nulos en columnas no críticas."""
    for col in columns:
        mask = rng.random(len(df)) < rate
        if pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype("Int64")
        df.loc[mask, col] = pd.NA
    return df


def write_table(df, name, cfg):
    """Escribe la tabla en CSV o Parquet según lo definido en config.yaml."""
    out_dir = REPO_DIR / cfg["output"]["path"]
    out_dir.mkdir(parents=True, exist_ok=True)
    if name in cfg["output"]["csv_tables"]:
        path = out_dir / f"{name}.csv"
        df.to_csv(path, index=False, encoding="utf-8")
    elif name in cfg["output"]["parquet_tables"]:
        path = out_dir / f"{name}.parquet"
        df.to_parquet(path, index=False)
    else:
        raise ValueError(f"{name} no tiene formato definido en config.yaml")
    return path