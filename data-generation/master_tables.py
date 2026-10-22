"""Generación de las tablas maestras: productos, sucursales y clientes."""
import numpy as np
import pandas as pd

from common import inject_nulls

# tip_prod, cantidad, nombre base, tasa EA (min,max), plazos posibles,
# cuota mínima (min,max), comisión administrativa en COP (min,max)
PRODUCT_SPECS = [
    ("LIBRE_INVERSION", 8, "Crédito libre inversión", (0.20, 0.30), (12, 24, 36, 48, 60, 72), (80_000, 150_000), (0, 15_000)),
    ("ROTATIVO", 6, "Crédito rotativo", (0.24, 0.32), (12, 24, 36), (50_000, 100_000), (0, 15_000)),
    ("TARJETA_DIGITAL", 6, "Tarjeta digital", (0.26, 0.34), (12, 24, 36), (30_000, 80_000), (0, 15_000)),
    ("AHORRO", 10, "Cuenta de ahorro digital", (0.02, 0.08), None, None, (0, 9_900)),
    ("PSE", 6, "Pagos PSE", (0.0, 0.0), None, None, (0, 3_500)),
    ("ACH", 8, "Transferencia ACH", (0.0, 0.0), None, None, (0, 3_500)),
    ("CORRESPONSALIA", 6, "Corresponsalía bancaria", (0.0, 0.0), None, None, (0, 3_500)),
]


def generate_productos(cfg, rng):
    rows, counter = [], 1
    for tip, qty, base, tasa, plazos, cuota, comision in PRODUCT_SPECS:
        for i in range(1, qty + 1):
            rows.append({
                "cod_prod": f"PRD{counter:03d}",
                "desc_prod": f"{base} - Plan {i}",
                "tip_prod": tip,
                "tasa_ea": round(float(rng.uniform(*tasa)), 4),
                "plazo_max_meses": int(rng.choice(plazos)) if plazos else None,
                "cuota_min": int(round(rng.uniform(*cuota), -3)) if cuota else None,
                "comision_admin": int(round(rng.uniform(*comision), -2)),
                # el primer producto de cada tipo siempre queda activo
                "estado_prod": "ACTIVO" if i == 1 else str(rng.choice(["ACTIVO", "INACTIVO"], p=[0.9, 0.1])),
            })
            counter += 1
    assert len(rows) == cfg["volumes"]["TB_PRODUCTOS_CAT"]
    df = pd.DataFrame(rows)
    df["plazo_max_meses"] = df["plazo_max_meses"].astype("Int64")
    df["cuota_min"] = df["cuota_min"].astype("Int64")
    return df


def generate_sucursales(cfg, rng):
    n = cfg["volumes"]["TB_SUCURSALES_RED"]
    cities = cfg["cities"]
    w = np.array([c["peso"] for c in cities])
    w = w / w.sum()

    city_idx = rng.choice(len(cities), size=n, p=w)
    city_idx[: len(cities)] = np.arange(len(cities))  # al menos 1 punto por ciudad
    tipo = rng.choice(["CORRESPONSAL", "PUNTO_ASISTIDO"], size=n, p=[0.85, 0.15])

    contador, rows = {}, []
    for i in range(n):
        c = cities[city_idx[i]]
        contador[c["cod"]] = contador.get(c["cod"], 0) + 1
        etiqueta = "Corresponsal" if tipo[i] == "CORRESPONSAL" else "Punto asistido"
        rows.append({
            "cod_suc": f"SUC{i + 1:04d}",
            "nom_suc": f"{etiqueta} {c['nombre']} {contador[c['cod']]:03d}",
            "tip_punto": tipo[i],
            "ciudad": c["nombre"],
            "depto": c["depto"],
            "latitud": round(c["lat"] + float(rng.normal(0, 0.03)), 6),
            "longitud": round(c["lon"] + float(rng.normal(0, 0.03)), 6),
            "activo": int(rng.choice([1, 0], p=[0.92, 0.08])),
        })
    df = pd.DataFrame(rows)
    return inject_nulls(df, ["latitud", "longitud"], cfg["quality"]["null_rate"], rng)


def generate_clientes(cfg, rng, fake, anomalies):
    n = cfg["volumes"]["TB_CLIENTES_CORE"]
    end = pd.Timestamp(cfg["date_range"]["end"])
    cities = cfg["cities"]
    w = np.array([c["peso"] for c in cities])
    w = w / w.sum()

    id_cli = np.arange(100_001, 100_001 + n)
    nombres = [fake.first_name() for _ in range(n)]
    apellidos = [f"{fake.last_name()} {fake.last_name()}" for _ in range(n)]
    tip_doc = rng.choice(["CC", "CE", "PAS"], size=n, p=[0.88, 0.08, 0.04])

    # Números de documento únicos
    candidatos = np.unique(rng.integers(10_000_000, 1_900_000_000, size=n * 2))
    num_doc = rng.permutation(candidatos)[:n]

    # Edad con distribución normal (media 38, desviación 11), mínimo 21
    edad = rng.normal(38, 11, n)
    jovenes = edad < 21
    edad[jovenes] = rng.uniform(21, 30, jovenes.sum())
    edad = np.clip(edad, 21, 85)
    fec_nac = (end - pd.to_timedelta(edad * 365.25, unit="D")).normalize()

    # Fecha de alta: más clientes recientes (banco fundado en 2015); nunca antes de los 18 años
    alta_ini, alta_fin = pd.Timestamp("2015-06-01"), pd.Timestamp("2026-06-30")
    span = (alta_fin - alta_ini).days
    u = rng.beta(2.0, 1.0, n)
    fec_alta = alta_ini + pd.to_timedelta((u * span).astype(int), unit="D")
    min_alta = fec_nac + pd.to_timedelta(18 * 365.25 + 1, unit="D")
    fec_alta = pd.DatetimeIndex(np.maximum(fec_alta.values, min_alta.values)).normalize()

    # Segmento y score de buró (a mayor segmento, mayor score promedio)
    seg = rng.choice(["BAS", "EST", "PRE", "ELI"], size=n, p=[0.45, 0.35, 0.17, 0.03])
    base = pd.Series(seg).map({"BAS": 600, "EST": 660, "PRE": 720, "ELI": 780}).to_numpy()
    score = np.clip(rng.normal(base, 70), 150, 950).round().astype(int)

    city_idx = rng.choice(len(cities), size=n, p=w)

    df = pd.DataFrame({
        "id_cli": id_cli,
        "nomb_cli": nombres,
        "apell_cli": apellidos,
        "tip_doc": tip_doc,
        "num_doc": num_doc.astype(str),
        "fec_nac": fec_nac,
        "fec_alta": fec_alta,
        "cod_segmento": seg,
        "score_buro": score,
        "ciudad_res": [cities[i]["nombre"] for i in city_idx],
        "depto_res": [cities[i]["depto"] for i in city_idx],
        "estado_cli": rng.choice(["ACTIVO", "INACTIVO", "BLOQUEADO"], size=n, p=[0.90, 0.07, 0.03]),
        "canal_adquis": rng.choice(["APP_MOVIL", "PORTAL_WEB", "CORRESPONSAL", "REFERIDO"],
                                   size=n, p=[0.55, 0.25, 0.15, 0.05]),
    })

    # ~5% de nulos en campos no críticos
    df = inject_nulls(df, ["score_buro", "canal_adquis"], cfg["quality"]["null_rate"], rng)

    # ANOMALÍA 1: fechas de nacimiento en el futuro (fuera de rango)
    k1 = max(1, int(n * cfg["quality"]["out_of_range_date_rate"]))
    idx1 = rng.choice(n, size=k1, replace=False)
    df.loc[idx1, "fec_nac"] = (end + pd.to_timedelta(rng.integers(30, 3000, k1), unit="D")).values

    # ANOMALÍA 2: estado_cli escrito de forma inconsistente
    k2 = max(1, int(n * cfg["quality"]["inconsistent_rate"]))
    idx2 = rng.choice(n, size=k2, replace=False)
    df.loc[idx2, "estado_cli"] = rng.choice(["activo", "Activo ", "A", "ACT"], size=k2)

    anomalies["TB_CLIENTES_CORE"] = {
        "fec_nac_futura": k1,
        "estado_cli_inconsistente": k2,
    }

    df["fec_nac"] = df["fec_nac"].dt.date
    df["fec_alta"] = df["fec_alta"].dt.date
    return df