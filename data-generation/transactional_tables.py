"""Generación de las tablas transaccionales: obligaciones, movimientos y comisiones."""
import numpy as np
import pandas as pd

from common import inject_nulls

CREDIT_TYPES = ["LIBRE_INVERSION", "ROTATIVO", "TARJETA_DIGITAL"]

# Monto típico de crédito aprobado (COP) y factor de gasto transaccional por segmento
SEGMENT_MEDIAN_CREDIT = {"BAS": 3_000_000, "EST": 8_000_000, "PRE": 20_000_000, "ELI": 50_000_000}
SEGMENT_TX_FACTOR = {"BAS": 0.6, "EST": 1.0, "PRE": 2.0, "ELI": 5.0}

# tip_mov: (probabilidad, tipos de producto asociados, monto mediano COP, dispersión)
MOV_SPECS = {
    "PAGO_PSE": (0.22, ["PSE"], 120_000, 0.9),
    "TRANSFERENCIA_ACH": (0.25, ["ACH"], 400_000, 1.0),
    "RECARGA": (0.12, ["AHORRO"], 30_000, 0.7),
    "DEPOSITO_CORRESPONSAL": (0.08, ["CORRESPONSALIA"], 200_000, 0.8),
    "RETIRO_CORRESPONSAL": (0.05, ["CORRESPONSALIA"], 150_000, 0.7),
    "AVANCE": (0.06, ["TARJETA_DIGITAL", "ROTATIVO"], 500_000, 0.8),
    "PAGO_CUOTA": (0.22, CREDIT_TYPES, 180_000, 0.5),
}

# Peso de cada hora del día (0 a 23): picos al mediodía y en la tarde-noche
HOUR_WEIGHTS = [0.3, 0.2, 0.15, 0.15, 0.2, 0.4, 1.0, 2.0, 3.5, 4.5, 5.0, 5.5,
                6.0, 5.5, 5.0, 4.5, 4.5, 5.0, 6.0, 6.0, 5.0, 3.5, 2.0, 1.0]


def _sample_dates(n, start, end, rng):
    """Fechas con estacionalidad: quincenas, inicio de mes y diciembre pesan más."""
    days = pd.date_range(start, end, freq="D")
    dow = days.dayofweek.to_numpy()
    dom = days.day.to_numpy()
    month = days.month.to_numpy()
    w = np.ones(len(days))
    w[dow >= 5] *= 0.75
    w[(dom >= 14) & (dom <= 16)] *= 1.5
    w[dom >= 29] *= 1.5
    w[dom <= 2] *= 1.2
    w[month == 12] *= 1.4
    w = w / w.sum()
    return days[rng.choice(len(days), size=n, p=w)]


def generate_obligaciones(cfg, rng, clientes, productos, anomalies):
    n = cfg["volumes"]["TB_OBLIGACIONES"]
    end = pd.Timestamp(cfg["date_range"]["end"])
    start_hist = pd.Timestamp("2024-10-01")

    credit = productos[productos["tip_prod"].isin(CREDIT_TYPES)
                       & (productos["estado_prod"] == "ACTIVO")].reset_index(drop=True)
    cli = clientes.reset_index(drop=True)
    c = cli.iloc[rng.integers(0, len(cli), n)].reset_index(drop=True)
    p = credit.iloc[rng.integers(0, len(credit), n)].reset_index(drop=True)

    # Montos: lognormal según el segmento del cliente
    median = c["cod_segmento"].map(SEGMENT_MEDIAN_CREDIT).to_numpy(dtype=float)
    aprobado = np.maximum(np.round(rng.lognormal(np.log(median), 0.5), -5), 500_000)
    factor = np.where(p["tip_prod"].to_numpy() == "LIBRE_INVERSION", 1.0, rng.uniform(0.6, 1.0, n))
    desembolsado = np.round(aprobado * factor, -3)

    plazo = p["plazo_max_meses"].astype(int).to_numpy()
    tasa = p["tasa_ea"].to_numpy(dtype=float)

    # Fecha de desembolso: nunca antes del alta del cliente
    span = (end - start_hist).days
    des = start_hist + pd.to_timedelta(rng.integers(0, span + 1, n), unit="D")
    alta = pd.to_datetime(c["fec_alta"]) + pd.Timedelta(days=1)
    des = pd.DatetimeIndex(np.maximum(des.values, alta.values))
    venc = des + pd.to_timedelta(plazo * 30, unit="D")

    # Amortización francesa: cuota fija y saldo de capital
    elapsed = np.asarray((end - des).days) // 30
    pagadas = np.minimum(plazo, elapsed)
    pend = plazo - pagadas
    r = (1 + tasa) ** (1 / 12) - 1
    cuota = desembolsado * r / (1 - (1 + r) ** (-plazo))
    saldo = desembolsado * (1 + r) ** pagadas - cuota * ((1 + r) ** pagadas - 1) / r
    saldo = np.where(pend == 0, 0, np.clip(saldo, 0, None))

    # Mora: más probable con score de buró bajo (score nulo = 650)
    score = np.nan_to_num(c["score_buro"].astype("float64").to_numpy(), nan=650.0)
    p_mora = np.clip((850 - score) / 2500, 0.04, 0.35)
    en_mora = (rng.random(n) < p_mora) & (pend > 0)
    rango = rng.choice(4, size=n, p=[0.50, 0.22, 0.13, 0.15])
    lo = np.array([1, 31, 61, 91])[rango]
    hi = np.array([30, 60, 90, 180])[rango]
    dias = np.where(en_mora, rng.integers(lo, hi + 1), 0)
    calif = np.select([dias == 0, dias <= 30, dias <= 60, dias <= 90], ["A", "B", "C", "D"], default="E")

    df = pd.DataFrame({
        "id_oblig": [f"OBL{i:06d}" for i in range(1, n + 1)],
        "id_cli": c["id_cli"].to_numpy(),
        "cod_prod": p["cod_prod"].to_numpy(),
        "vr_aprobado": aprobado.astype("int64"),
        "vr_desembolsado": desembolsado.astype("int64"),
        "sdo_capital": np.round(saldo).astype("int64"),
        "vr_cuota": np.round(cuota, -2).astype("int64"),
        "fec_desembolso": pd.Series(des).dt.date,
        "fec_venc": pd.Series(venc).dt.date,
        "dias_mora_act": dias.astype("int64"),
        "num_cuotas_pend": pend.astype("int64"),
        "calif_riesgo": calif,
    })
    df = inject_nulls(df, ["calif_riesgo"], cfg["quality"]["null_rate"], rng)

    # ANOMALÍAS: saldo mayor al desembolsado y días de mora negativos
    k = max(1, int(n * cfg["quality"]["inconsistent_rate"]))
    idx1 = rng.choice(n, size=k, replace=False)
    df.loc[idx1, "sdo_capital"] = (df.loc[idx1, "vr_desembolsado"] * rng.uniform(1.2, 2.0, k)).astype("int64")
    idx2 = rng.choice(n, size=k, replace=False)
    df.loc[idx2, "dias_mora_act"] = -rng.integers(1, 30, k)
    anomalies["TB_OBLIGACIONES"] = {"saldo_mayor_que_desembolsado": k, "dias_mora_negativos": k}
    return df


def generate_movimientos(cfg, rng, clientes, productos, anomalies):
    n = cfg["volumes"]["TB_MOV_FINANCIEROS"]
    start = pd.Timestamp(cfg["date_range"]["start"])
    end = pd.Timestamp(cfg["date_range"]["end"])
    cities = cfg["cities"]

    cli = clientes.reset_index(drop=True)
    # Unos clientes transaccionan mucho más que otros (distribución gamma)
    activity = rng.gamma(shape=1.2, scale=1.0, size=len(cli))
    c = cli.iloc[rng.choice(len(cli), size=n, p=activity / activity.sum())].reset_index(drop=True)

    tipos = list(MOV_SPECS)
    probs = np.array([MOV_SPECS[t][0] for t in tipos])
    tip_mov = rng.choice(tipos, size=n, p=probs / probs.sum())

    cod_prod = np.empty(n, dtype=object)
    vr = np.empty(n, dtype=float)
    for t in tipos:
        m = tip_mov == t
        cand = productos.loc[productos["tip_prod"].isin(MOV_SPECS[t][1])
                             & (productos["estado_prod"] == "ACTIVO"), "cod_prod"].to_numpy()
        cod_prod[m] = rng.choice(cand, size=int(m.sum()))
        vr[m] = rng.lognormal(np.log(MOV_SPECS[t][2]), MOV_SPECS[t][3], size=int(m.sum()))

    vr = vr * c["cod_segmento"].map(SEGMENT_TX_FACTOR).to_numpy(dtype=float)
    # Picos atípicos (0.3%): montos 8 a 15 veces mayores y de madrugada, para el motor de fraude
    pico = rng.random(n) < 0.003
    vr[pico] *= rng.uniform(8, 15, int(pico.sum()))
    vr = np.maximum(np.round(vr, -2), 1000).astype("int64")

    es_corr = np.isin(tip_mov, ["DEPOSITO_CORRESPONSAL", "RETIRO_CORRESPONSAL"])
    canal = np.where(es_corr, "CORRESPONSAL", rng.choice(["APP_MOVIL", "PORTAL_WEB"], size=n, p=[0.65, 0.35]))

    fec = _sample_dates(n, start, end, rng)
    alta = pd.to_datetime(c["fec_alta"])
    fec = pd.DatetimeIndex(np.maximum(fec.values, alta.values))  # no hay movimientos antes del alta

    hw = np.array(HOUR_WEIGHTS)
    hora = rng.choice(24, size=n, p=hw / hw.sum())
    hora = np.where(pico, rng.integers(0, 5, n), hora)
    secs = hora * 3600 + rng.integers(0, 3600, n)
    hra = pd.Series(secs).map(lambda s: f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}")

    num_cuenta = "AH" + pd.Series(c["id_cli"].to_numpy(dtype="int64") * 7919 % 10**10).astype(str).str.zfill(10)

    city_map = {x["nombre"]: x["cod"] for x in cities}
    base_city = c["ciudad_res"].map(city_map).to_numpy(dtype=object)
    other_city = rng.choice([x["cod"] for x in cities], size=n)
    cod_ciudad = np.where(rng.random(n) < 0.10, other_city, base_city)

    estado = rng.choice(["APROBADO", "RECHAZADO", "REVERSADO"], size=n, p=[0.94, 0.04, 0.02])
    k_dev = pd.Series(rng.integers(1, 3, n)).astype(str)
    disp = ("DV" + c["id_cli"].astype(str) + "-" + k_dev).to_numpy(dtype=object)
    disp = np.where(canal == "CORRESPONSAL", None, disp)

    df = pd.DataFrame({
        "id_cli": c["id_cli"].to_numpy(),
        "cod_prod": cod_prod,
        "num_cuenta": num_cuenta.to_numpy(),
        "fec_mov": fec,
        "hra_mov": hra.to_numpy(),
        "vr_mov": vr,
        "tip_mov": tip_mov,
        "cod_canal": canal,
        "cod_ciudad": cod_ciudad,
        "cod_estado_mov": estado,
        "id_dispositivo": disp,
    })
    df = df.sort_values(["fec_mov", "hra_mov"], kind="stable").reset_index(drop=True)
    df.insert(0, "id_mov", np.arange(1, n + 1))
    df = inject_nulls(df, ["cod_ciudad", "id_dispositivo"], cfg["quality"]["null_rate"], rng)

    # ANOMALÍA 1: fechas de movimiento fuera de rango (posteriores al periodo)
    k_f = max(1, int(n * cfg["quality"]["out_of_range_date_rate"]))
    idx_f = rng.choice(n, size=k_f, replace=False)
    df.loc[idx_f, "fec_mov"] = (end + pd.to_timedelta(rng.integers(60, 900, k_f), unit="D")).values

    # ANOMALÍA 2: montos negativos (campo inconsistente)
    k_v = max(1, int(n * cfg["quality"]["inconsistent_rate"]))
    idx_v = rng.choice(n, size=k_v, replace=False)
    df.loc[idx_v, "vr_mov"] = -df.loc[idx_v, "vr_mov"]

    df["fec_mov"] = df["fec_mov"].dt.date

    # ANOMALÍA 3: transacciones duplicadas (filas idénticas, mismo id_mov)
    k_d = max(1, int(n * cfg["quality"]["duplicate_rate"]))
    dup = df.sample(n=k_d, random_state=int(rng.integers(0, 2**31 - 1)))
    df = pd.concat([df, dup], ignore_index=True)

    anomalies["TB_MOV_FINANCIEROS"] = {
        "fec_mov_fuera_de_rango": k_f,
        "vr_mov_negativo": k_v,
        "transacciones_duplicadas": k_d,
        "picos_atipicos_intencionales": int(pico.sum()),
    }
    return df


def generate_comisiones(cfg, rng, obligaciones, movimientos, productos):
    n = cfg["volumes"]["TB_COMISIONES_LOG"]
    start = pd.Timestamp(cfg["date_range"]["start"])
    end = pd.Timestamp(cfg["date_range"]["end"])
    com_admin = productos.set_index("cod_prod")["comision_admin"]

    def valor(cods, fallback):
        base = com_admin.reindex(cods).to_numpy(dtype=float)
        return np.where(base > 0, base, rng.choice(fallback, size=len(base))).astype("int64")

    # 60% por transacciones aprobadas y válidas
    mov = movimientos.drop_duplicates("id_mov")
    mov = mov[(mov["cod_estado_mov"] == "APROBADO") & (mov["vr_mov"] > 0)
              & (mov["fec_mov"] >= start.date()) & (mov["fec_mov"] <= end.date())]
    n_tx = int(n * 0.6)
    s = mov.iloc[rng.choice(len(mov), size=n_tx, replace=False)]
    tx = pd.DataFrame({
        "id_cli": s["id_cli"].to_numpy(),
        "cod_prod": s["cod_prod"].to_numpy(),
        "fec_cobro": s["fec_mov"].to_numpy(),
        "vr_comision": valor(s["cod_prod"].to_numpy(), [1500, 2500, 3500]),
        "tip_comision": "TRANSACCIONAL",
    })

    # 40% por administración de créditos (cobro dentro del periodo, posterior al desembolso)
    n_cr = n - n_tx
    o = obligaciones.iloc[rng.integers(0, len(obligaciones), n_cr)]
    des = pd.to_datetime(o["fec_desembolso"])
    si = np.maximum(des.values, start.to_datetime64())
    dias = ((end.to_datetime64() - si) / np.timedelta64(1, "D")).astype(int) + 1
    fec = pd.DatetimeIndex(si) + pd.to_timedelta((rng.random(n_cr) * dias).astype(int), unit="D")
    cr = pd.DataFrame({
        "id_cli": o["id_cli"].to_numpy(),
        "cod_prod": o["cod_prod"].to_numpy(),
        "fec_cobro": pd.Series(fec).dt.date.to_numpy(),
        "vr_comision": valor(o["cod_prod"].to_numpy(), [4900, 9900, 14900]),
        "tip_comision": "ADMINISTRACION_CREDITO",
    })

    df = pd.concat([tx, cr], ignore_index=True)
    df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    df.insert(0, "id_comision", [f"COM{i:07d}" for i in range(1, len(df) + 1)])
    df["estado_cobro"] = rng.choice(["COBRADA", "PENDIENTE", "REVERSADA"], size=len(df), p=[0.93, 0.04, 0.03])
    return inject_nulls(df, ["tip_comision"], cfg["quality"]["null_rate"], rng)