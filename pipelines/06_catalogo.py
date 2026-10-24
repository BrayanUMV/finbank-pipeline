# Databricks notebook source
# MAGIC %run ./00_common

# COMMAND ----------
SILVER = ["tb_productos_cat", "tb_sucursales_red", "tb_clientes_core", "tb_obligaciones", "tb_mov_financieros", "tb_comisiones_log"]
GOLD = ["dim_clientes", "dim_productos", "dim_geografia", "dim_canal", "fact_transacciones", "fact_cartera",
        "fact_rentabilidad_cliente", "kpi_cartera_diaria", "agg_regulatorio_mensual", "vista_cliente_360"]

# Tabla de Silver de la que sale cada tabla de Gold (para completar la columna "Origen")
FUENTE = {"dim_clientes": "silver.tb_clientes_core", "dim_productos": "silver.tb_productos_cat",
          "dim_geografia": "catálogo fijo en 03_gold", "dim_canal": "silver.tb_sucursales_red + canales digitales",
          "fact_transacciones": "silver.tb_mov_financieros", "fact_cartera": "silver.tb_obligaciones",
          "fact_rentabilidad_cliente": "silver.tb_obligaciones + silver.tb_comisiones_log",
          "kpi_cartera_diaria": "gold.fact_cartera + gold.dim_clientes",
          "agg_regulatorio_mensual": "gold.fact_transacciones",
          "vista_cliente_360": "gold.dim_clientes + gold.fact_transacciones + gold.fact_cartera"}

# Campos calculados o transformados: su origen es una fórmula, no una columna
CALC = {
    "num_doc_hash": "hash SHA-256 con sal de num_doc", "score_buro_imputado": "score_buro nulo antes de imputar",
    "coordenadas_nulas": "latitud o longitud nulas", "dispositivo_nulo": "id_dispositivo nulo",
    "prom_30d": "promedio de vr_mov de los 30 días previos del cliente", "desv_30d": "desviación estándar de vr_mov de los 30 días previos",
    "n_30d": "cantidad de movimientos en los 30 días previos", "ind_sospechoso": "1 si vr_mov > prom_30d + 3 x desv_30d (con 5 o más movimientos previos)",
    "nombre_completo": "nomb_cli + apell_cli (ya enmascarados)", "edad": "años entre fec_nac y la fecha de corte",
    "segmento": "etiqueta legible de cod_segmento", "nombre_producto": "desc_prod", "tipo_producto": "tip_prod",
    "tasa_mensual": "(1 + tasa_ea) ^ (1/12) - 1", "cuota_minima": "cuota_min",
    "familia": "Crédito, Ahorro o Transaccional según tip_prod", "monto_usd": "vr_mov / TRM fija de 4,000",
    "horario": "HABIL si es lunes a viernes entre 8:00 y 17:59", "promedio_movil_30d": "prom_30d de Silver",
    "mes": "año-mes derivado de la fecha", "bucket_mora": "rango según dias_mora_act", "clasificacion_regulatoria": "A a E según dias_mora_act",
    "provision_estimada": "sdo_capital x porcentaje por clasificación", "fecha_corte": "fecha de corte de la cartera",
    "ingreso_intereses": "vr_desembolsado x tasa_mensual por cada mes de vigencia", "ingreso_comisiones": "suma de comisiones COBRADAS del mes",
    "ingreso_total": "ingreso_intereses + ingreso_comisiones", "cltv_12m": "suma de ingreso_total de los 12 meses calendario más recientes",
    "obligaciones_activas": "obligaciones con cuotas pendientes", "monto_total_cartera": "suma de sdo_capital",
    "monto_en_mora": "suma de sdo_capital con dias_mora_act > 0", "clientes_en_mora": "clientes distintos con mora",
    "tasa_mora_pct": "100 x monto_en_mora / monto_total_cartera", "cuentas_activas": "cuentas distintas con movimientos aprobados",
    "total_transacciones": "cantidad de movimientos aprobados", "volumen_cop": "suma de vr_mov",
    "productos_usados": "productos distintos usados por el cliente", "transacciones": "cantidad de movimientos del cliente",
    "pagos_realizados": "pagos de cuota aprobados", "ultimo_pago": "fecha del último pago de cuota",
    "max_dias_mora": "mayor dias_mora_act del cliente", "peor_calificacion": "peor clasificación regulatoria del cliente",
    "saldo_total": "suma de sdo_capital del cliente",
}

DESC = {
    "id_cli": "Identificador del cliente", "nomb_cli": "Nombre del cliente (solo 2 letras visibles)", "apell_cli": "Apellidos del cliente (solo 2 letras visibles)",
    "tip_doc": "Tipo de documento", "num_doc_hash": "Documento de identidad convertido en hash irreversible", "fec_nac": "Fecha de nacimiento",
    "fec_alta": "Fecha de alta del cliente", "cod_segmento": "Código de segmento (BAS, EST, PRE, ELI)", "score_buro": "Puntaje de buró de crédito (nulos imputados)",
    "score_buro_imputado": "Indica si el score se imputó con la mediana del segmento", "ciudad_res": "Ciudad de residencia", "depto_res": "Departamento de residencia",
    "estado_cli": "Estado del cliente normalizado", "canal_adquis": "Canal por el que se adquirió el cliente",
    "cod_prod": "Código del producto", "desc_prod": "Descripción del producto", "tip_prod": "Tipo de producto", "tasa_ea": "Tasa efectiva anual",
    "plazo_max_meses": "Plazo máximo en meses", "cuota_min": "Cuota mínima en COP", "comision_admin": "Comisión administrativa en COP", "estado_prod": "Estado del producto",
    "cod_suc": "Código de la sucursal o punto de atención", "nom_suc": "Nombre del punto", "tip_punto": "Tipo de punto de atención", "ciudad": "Ciudad", "depto": "Departamento",
    "latitud": "Latitud", "longitud": "Longitud", "activo": "Indica si el punto está activo", "coordenadas_nulas": "Indica si faltan coordenadas",
    "id_oblig": "Identificador de la obligación", "vr_aprobado": "Valor aprobado en COP", "vr_desembolsado": "Valor desembolsado en COP", "sdo_capital": "Saldo de capital en COP",
    "vr_cuota": "Valor de la cuota en COP", "fec_desembolso": "Fecha de desembolso", "fec_venc": "Fecha de vencimiento", "dias_mora_act": "Días de mora actuales",
    "num_cuotas_pend": "Cuotas pendientes", "calif_riesgo": "Calificación de riesgo (A a E)",
    "id_mov": "Identificador del movimiento", "num_cuenta": "Número de cuenta", "fec_mov": "Fecha del movimiento", "hra_mov": "Hora del movimiento (texto HH:MM:SS)",
    "vr_mov": "Valor del movimiento en COP", "tip_mov": "Tipo de movimiento", "cod_canal": "Canal del movimiento", "cod_ciudad": "Código DANE de la ciudad",
    "cod_estado_mov": "Estado del movimiento", "id_dispositivo": "Dispositivo desde el que se hizo", "dispositivo_nulo": "Indica si falta el dispositivo",
    "prom_30d": "Promedio de los 30 días previos", "desv_30d": "Desviación de los 30 días previos", "n_30d": "Movimientos en los 30 días previos", "ind_sospechoso": "Marca de transacción sospechosa (1 o 0)",
    "id_comision": "Identificador de la comisión", "fec_cobro": "Fecha de cobro", "vr_comision": "Valor de la comisión en COP", "tip_comision": "Tipo de comisión", "estado_cobro": "Estado del cobro",
    "nombre_completo": "Nombre completo enmascarado", "edad": "Edad en años", "segmento": "Segmento del cliente", "nombre_producto": "Nombre del producto",
    "tipo_producto": "Tipo de producto", "tasa_mensual": "Tasa mensual equivalente", "cuota_minima": "Cuota mínima en COP", "familia": "Familia del producto",
    "tipo_canal": "Tipo de canal (digital o punto de atención)", "monto_usd": "Monto en USD", "horario": "HABIL o NO_HABIL", "promedio_movil_30d": "Promedio móvil de 30 días",
    "mes": "Mes del registro", "bucket_mora": "Rango de mora", "clasificacion_regulatoria": "Clasificación regulatoria A a E", "provision_estimada": "Provisión estimada en COP",
    "fecha_corte": "Fecha de corte de la cartera", "ingreso_intereses": "Ingreso estimado por intereses", "ingreso_comisiones": "Ingreso por comisiones cobradas",
    "ingreso_total": "Ingreso total del mes", "cltv_12m": "Valor de vida del cliente a 12 meses", "obligaciones_activas": "Obligaciones activas", "monto_total_cartera": "Monto total de cartera",
    "monto_en_mora": "Monto en mora", "clientes_en_mora": "Clientes con alguna obligación en mora", "tasa_mora_pct": "Tasa de mora en porcentaje", "cuentas_activas": "Cuentas activas",
    "total_transacciones": "Total de transacciones", "volumen_cop": "Volumen en COP", "productos_usados": "Productos usados", "transacciones": "Transacciones del cliente",
    "pagos_realizados": "Pagos realizados", "ultimo_pago": "Fecha del último pago", "max_dias_mora": "Máximo de días de mora", "peor_calificacion": "Peor calificación regulatoria",
    "saldo_total": "Saldo total en COP",
}

PROTEGIDO = {"num_doc_hash": "Sí (hash irreversible)", "nomb_cli": "Sí (enmascarado)", "apell_cli": "Sí (enmascarado)", "nombre_completo": "Sí (enmascarado)"}
PERSONAL = {"fec_nac", "edad", "num_cuenta", "id_dispositivo", "score_buro"}
FINANCIERO = {"vr_aprobado", "vr_desembolsado", "sdo_capital", "vr_cuota", "vr_mov", "monto_usd", "vr_comision", "ingreso_intereses",
              "ingreso_comisiones", "ingreso_total", "cltv_12m", "saldo_total", "provision_estimada"}

def sensible(col):
    if col in PROTEGIDO: return PROTEGIDO[col]
    if col in PERSONAL: return "Sí (personal)"
    if col in FINANCIERO: return "Sí (financiero)"
    return "No"

def origen(capa, tabla, col):
    if col in CALC: return CALC[col]
    return f"bronze.{tabla}.{col}" if capa == "silver" else f"{FUENTE.get(tabla, 'silver')}.{col}"

def render(tablas):
    """tablas = [(capa, nombre, [(columna, tipo), ...]), ...] -> texto Markdown."""
    out = ["# Catálogo de datos", "",
           "Generado desde los esquemas reales de las capas Silver y Gold. "
           "Sensible = contiene datos personales o financieros por cliente.", ""]
    for capa, tabla, cols in tablas:
        out += [f"## {capa}.{tabla}", "", "| Campo | Tipo | Origen | Sensible | Descripción |", "|---|---|---|---|---|"]
        for col, tipo in cols:
            out.append(f"| {col} | {tipo} | {origen(capa, tabla, col)} | {sensible(col)} | {DESC.get(col, 'Pendiente de describir')} |")
        out.append("")
    return "\n".join(out)

# COMMAND ----------
tablas = []
for capa, lista in (("silver", SILVER), ("gold", GOLD)):
    for t in lista:
        sch = spark.read.format("delta").load(path(capa, t)).schema
        tablas.append((capa, t, [(f.name, f.dataType.simpleString()) for f in sch.fields]))

md = render(tablas)
yo = spark.sql("SELECT current_user()").first()[0]
destino = f"/Workspace/Users/{yo}/finbank/catalogo_datos.md"
with open(destino, "w", encoding="utf-8") as f:
    f.write(md)

sin_desc = sorted({c for _, _, cols in tablas for c, _ in cols if c not in DESC})
print("Archivo escrito en:", destino, "|", len(md), "caracteres,", sum(len(c) for _, _, c in tablas), "campos")
print("Campos sin descripción:", sin_desc if sin_desc else "ninguno")
