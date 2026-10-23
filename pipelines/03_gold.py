# Databricks notebook source
# MAGIC %run ./00_common

# COMMAND ----------
SV = lambda t: spark.read.format("delta").load(path("silver", t))
GD = lambda t: spark.read.format("delta").load(path("gold", t))

def put(nombre, df, t0, part=None):
    w = df.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
    (w.partitionBy(part) if part else w).save(path("gold", nombre))
    n = GD(nombre).count()
    log_run("gold", nombre, n, time.time() - t0, path("gold", nombre))
    return n

# Catálogo de ciudades con código DANE (el mismo que usan los movimientos en cod_ciudad)
CIUDADES = [("11001", "Bogotá D.C.", "Bogotá D.C."), ("05001", "Medellín", "Antioquia"),
            ("76001", "Cali", "Valle del Cauca"), ("08001", "Barranquilla", "Atlántico"),
            ("13001", "Cartagena", "Bolívar"), ("68001", "Bucaramanga", "Santander"),
            ("66001", "Pereira", "Risaralda"), ("17001", "Manizales", "Caldas"),
            ("54001", "Cúcuta", "Norte de Santander"), ("47001", "Santa Marta", "Magdalena"),
            ("73001", "Ibagué", "Tolima"), ("50001", "Villavicencio", "Meta")]

# ---------------- Dimensiones ----------------
def dim_clientes():
    t0 = time.time()
    seg = F.create_map(*[F.lit(x) for kv in [("BAS", "Básico"), ("EST", "Estándar"),
                                              ("PRE", "Premium"), ("ELI", "Elite")] for x in kv])
    df = SV("tb_clientes_core").select(
        "id_cli",
        F.concat_ws(" ", "nomb_cli", "apell_cli").alias("nombre_completo"),       # ya viene enmascarado desde Silver
        "num_doc_hash",
        F.floor(F.months_between(F.lit(AS_OF).cast("date"), F.col("fec_nac")) / 12).alias("edad"),
        seg[F.col("cod_segmento")].alias("segmento"), "cod_segmento", "ciudad_res", "depto_res",
        "estado_cli", "canal_adquis", "score_buro", "fec_alta")
    return put("dim_clientes", df, t0)

def dim_productos():
    t0 = time.time()
    fam = (F.when(F.col("tip_prod").isin("LIBRE_INVERSION", "ROTATIVO", "TARJETA_DIGITAL"), "Crédito")
            .when(F.col("tip_prod") == "AHORRO", "Ahorro")
            .otherwise("Transaccional"))
    df = SV("tb_productos_cat").select(
        "cod_prod", F.col("desc_prod").alias("nombre_producto"), F.col("tip_prod").alias("tipo_producto"),
        "tasa_ea",
        (F.pow(F.lit(1.0) + F.col("tasa_ea").cast("double"), F.lit(1 / 12)) - 1).alias("tasa_mensual"),
        "plazo_max_meses", F.col("cuota_min").alias("cuota_minima"), "comision_admin",
        fam.alias("familia"), "estado_prod")
    return put("dim_productos", df, t0)

def dim_geografia():
    t0 = time.time()
    df = spark.createDataFrame(CIUDADES, "cod_ciudad string, ciudad string, depto string")
    return put("dim_geografia", df, t0)

def dim_canal():
    t0 = time.time()
    dig = spark.createDataFrame([("APP_MOVIL", "Digital"), ("PORTAL_WEB", "Digital"),
                                 ("CORRESPONSAL", "Punto de atención")], "cod_canal string, tipo_canal string")
    fis = (SV("tb_sucursales_red").select(F.col("tip_punto").alias("cod_canal")).distinct()
           .withColumn("tipo_canal", F.lit("Punto de atención")))
    return put("dim_canal", dig.unionByName(fis).dropDuplicates(["cod_canal"]), t0)

# ---------------- Hechos ----------------
def fact_transacciones():
    t0 = time.time()
    hora = F.substring("hra_mov", 1, 2).cast("int")
    df = (SV("tb_mov_financieros")
          .join(GD("dim_clientes").select("id_cli"), "id_cli", "left_semi")           # valida id_cli contra dim_clientes
          .withColumn("monto_usd", F.round(F.col("vr_mov") / F.lit(COP_USD), 2))
          .withColumn("horario", F.when(F.dayofweek("fec_mov").between(2, 6) & hora.between(8, 17), "HABIL")
                                  .otherwise("NO_HABIL"))
          .withColumnRenamed("prom_30d", "promedio_movil_30d")
          .withColumn("mes", F.date_format("fec_mov", "yyyy-MM")))
    return put("fact_transacciones", df, t0, "mes")

def fact_cartera():
    t0 = time.time()
    d = F.col("dias_mora_act")
    bucket = (F.when(d == 0, "Al día").when(d <= 30, "Rango 1 (1-30)").when(d <= 60, "Rango 2 (31-60)")
               .when(d <= 90, "Rango 3 (61-90)").otherwise("Deteriorado (más de 90)"))
    clasif = F.when(d == 0, "A").when(d <= 30, "B").when(d <= 60, "C").when(d <= 90, "D").otherwise("E")
    prov = F.create_map(*[x for k, v in PROVISION.items() for x in (F.lit(k), F.lit(v))])
    df = (SV("tb_obligaciones")
          .withColumn("bucket_mora", bucket)
          .withColumn("clasificacion_regulatoria", clasif)
          .withColumn("provision_estimada", F.round(F.col("sdo_capital") * prov[clasif], 0))
          .withColumn("fecha_corte", F.lit(AS_OF).cast("date")))
    return put("fact_cartera", df, t0)

def fact_rentabilidad_cliente():
    t0 = time.time()
    tasa = GD("dim_productos").select("cod_prod", "tasa_mensual")
    # Intereses mensuales estimados: monto desembolsado x tasa mensual, en cada mes de vigencia dentro del periodo
    inter = (SV("tb_obligaciones").join(tasa, "cod_prod")
             .withColumn("m_ini", F.greatest(F.trunc("fec_desembolso", "month"), F.lit(PERIODO[0]).cast("date")))
             .withColumn("m_fin", F.least(F.trunc("fec_venc", "month"), F.trunc(F.lit(AS_OF).cast("date"), "month")))
             .filter("m_ini <= m_fin")
             .withColumn("mes", F.explode(F.expr("sequence(m_ini, m_fin, interval 1 month)")))
             .groupBy("id_cli", "mes")
             .agg(F.sum(F.col("vr_desembolsado") * F.col("tasa_mensual")).alias("ingreso_intereses")))
    # Comisiones efectivamente cobradas
    com = (SV("tb_comisiones_log").filter("estado_cobro = 'COBRADA'")
           .withColumn("mes", F.trunc("fec_cobro", "month"))
           .groupBy("id_cli", "mes").agg(F.sum("vr_comision").alias("ingreso_comisiones")))
    r = (inter.join(com, ["id_cli", "mes"], "full")
              .na.fill(0, ["ingreso_intereses", "ingreso_comisiones"])
              .withColumn("ingreso_total", F.col("ingreso_intereses") + F.col("ingreso_comisiones"))
              .withColumn("m_idx", F.year("mes") * 12 + F.month("mes")))
    w = Window.partitionBy("id_cli").orderBy("m_idx").rangeBetween(-11, 0)     # los 12 meses calendario más recientes
    r = r.withColumn("cltv_12m", F.round(F.sum("ingreso_total").over(w), 2)).drop("m_idx")
    return put("fact_rentabilidad_cliente", r, t0)

# ---------------- Agregaciones y KPIs ----------------
def kpi_cartera_diaria():
    t0 = time.time()
    c = GD("fact_cartera").join(GD("dim_clientes").select("id_cli", "segmento", "ciudad_res"), "id_cli")
    mora = F.col("dias_mora_act") > 0
    df = (c.groupBy("fecha_corte", "cod_prod", "segmento", "ciudad_res").agg(
            F.sum(F.when(F.col("num_cuotas_pend") > 0, 1).otherwise(0)).alias("obligaciones_activas"),
            F.sum("sdo_capital").alias("monto_total_cartera"),
            F.sum(F.when(mora, F.col("sdo_capital")).otherwise(0)).alias("monto_en_mora"),
            F.countDistinct(F.when(mora, F.col("id_cli"))).alias("clientes_en_mora"))
          .withColumn("tasa_mora_pct",
                      F.when(F.col("monto_total_cartera") > 0,
                             F.round(100 * F.col("monto_en_mora") / F.col("monto_total_cartera"), 2))))
    return put("kpi_cartera_diaria", df, t0, "fecha_corte")

def agg_regulatorio_mensual():
    t0 = time.time()
    df = (GD("fact_transacciones").filter("cod_estado_mov = 'APROBADO'")
          .groupBy("mes", "cod_prod", "cod_canal", "cod_ciudad")
          .agg(F.countDistinct("num_cuenta").alias("cuentas_activas"),
               F.count("*").alias("total_transacciones"),
               F.sum("vr_mov").alias("volumen_cop")))
    return put("agg_regulatorio_mensual", df, t0, "mes")

def vista_cliente_360():
    t0 = time.time()
    tx = GD("fact_transacciones")
    uso = tx.groupBy("id_cli").agg(F.countDistinct("cod_prod").alias("productos_usados"),
                                   F.count("*").alias("transacciones"), F.sum("vr_mov").alias("volumen_cop"))
    pagos = (tx.filter("tip_mov = 'PAGO_CUOTA' AND cod_estado_mov = 'APROBADO'").groupBy("id_cli")
               .agg(F.count("*").alias("pagos_realizados"), F.max("fec_mov").alias("ultimo_pago")))
    riesgo = GD("fact_cartera").groupBy("id_cli").agg(F.max("dias_mora_act").alias("max_dias_mora"),
                                                      F.max("clasificacion_regulatoria").alias("peor_calificacion"),
                                                      F.sum("sdo_capital").alias("saldo_total"))
    df = (GD("dim_clientes").select("id_cli", "nombre_completo", "segmento", "ciudad_res")
          .join(uso, "id_cli", "left").join(pagos, "id_cli", "left").join(riesgo, "id_cli", "left"))
    return put("vista_cliente_360", df, t0)

# COMMAND ----------
# Las dimensiones van primero (los hechos las usan); cada tabla se aísla para no frenar a las demás
PASOS = [dim_clientes, dim_productos, dim_geografia, dim_canal, fact_transacciones, fact_cartera,
         fact_rentabilidad_cliente, kpi_cartera_diaria, agg_regulatorio_mensual, vista_cliente_360]
res = [guarded("gold", f.__name__, f) for f in PASOS]
fail_if_any(res, "gold")
print(dict(zip([f.__name__ for f in PASOS], res)))
