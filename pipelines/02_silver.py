# Databricks notebook source
# MAGIC %run ./00_common

# COMMAND ----------
AUD = ["_ingest_ts", "_source_system", "_batch_id", "ing_anio", "ing_mes", "ing_dia"]
B = lambda t: spark.read.format("delta").load(path("bronze", t)).drop(*AUD)
SV = lambda t: spark.read.format("delta").load(path("silver", t))
SALT = S("pii-salt")
hash_ = lambda c: F.sha2(F.concat(F.lit(SALT), F.col(c).cast("string")), 256)   # hash con sal: irreversible
mask = lambda c: F.concat(F.substring(F.col(c), 1, 2), F.lit("***"))             # Ju***

def check(df, tabla, reglas):
    """reglas = [(motivo, condición SQL que indica error)]. Devuelve (limpios, rechazados con motivo)."""
    r = F.lit(None).cast("string")
    for motivo, cond in reversed(reglas):          # la primera regla de la lista tiene prioridad
        r = F.when(F.expr(cond), F.lit(motivo)).otherwise(r)
    d = df.withColumn("_motivo", r)
    ok = d.filter("_motivo IS NULL").drop("_motivo")
    rej = (d.filter("_motivo IS NOT NULL")
            .select(F.lit(tabla).alias("source_table"), F.lit(BATCH_ID).alias("batch_id"),
                    F.col("_motivo").alias("motivo"),
                    F.to_json(F.struct(*[F.col(c) for c in df.columns])).alias("registro")))
    return ok, rej

def ids(tabla, key, flag):
    """Llaves existentes en una tabla de Silver, con una marca para detectar huérfanos tras un left join."""
    return SV(tabla).select(key).distinct().withColumn(flag, F.lit(1))

def finish(nombre, t0, n_in, dedup, ok, rej):
    dest = path("silver", nombre)
    ok.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(dest)
    (rej.write.format("delta").mode("overwrite")
        .option("replaceWhere", f"source_table = '{nombre}'").save(path("silver", "_errores")))
    out = SV(nombre)
    n_ok = out.count()
    n_rej = SV("_errores").filter(f"source_table = '{nombre}'").count()
    nulos = out.select([F.round(100 * F.avg(F.col(c).isNull().cast("int")), 2).alias(c)
                        for c in out.columns]).first().asDict()
    append_ops("dq_silver", [dict(ts=now_utc(), batch_id=BATCH_ID, tabla=nombre,
                                  filas_bronze=int(n_in), duplicados_eliminados=int(n_in - dedup.count()),
                                  rechazados=int(n_rej), conformes_pct=round(100 * n_ok / max(n_in, 1), 2),
                                  nulos_pct=json.dumps(nulos))])
    log_run("silver", nombre, n_ok, time.time() - t0, dest)
    return n_ok

# COMMAND ----------
def run_productos():
    t0, raw = time.time(), B("tb_productos_cat")
    df = raw.dropDuplicates().withColumn("desc_prod", F.trim("desc_prod"))
    ok, rej = check(df, "tb_productos_cat", [
        ("campo_obligatorio_nulo", "cod_prod IS NULL OR tip_prod IS NULL"),
        ("tasa_ea_invalida", "tasa_ea IS NULL OR NOT (tasa_ea BETWEEN 0 AND 1)")])
    return finish("tb_productos_cat", t0, raw.count(), df, ok, rej)

def run_sucursales():
    t0, raw = time.time(), B("tb_sucursales_red")
    df = (raw.dropDuplicates()
             .withColumn("coordenadas_nulas", F.col("latitud").isNull() | F.col("longitud").isNull()))
    ok, rej = check(df, "tb_sucursales_red", [("campo_obligatorio_nulo", "cod_suc IS NULL OR ciudad IS NULL")])
    return finish("tb_sucursales_red", t0, raw.count(), df, ok, rej)

def run_clientes():
    t0, raw = time.time(), B("tb_clientes_core")
    df = raw.dropDuplicates()
    med = df.groupBy("cod_segmento").agg(F.expr("percentile_approx(score_buro, 0.5)").alias("score_med"))
    df = (df.join(med, "cod_segmento", "left")
            .withColumn("score_buro_imputado", F.col("score_buro").isNull())    # nulo: mediana del segmento + indicador
            .withColumn("score_buro", F.coalesce("score_buro", "score_med")).drop("score_med")
            .withColumn("canal_adquis", F.coalesce("canal_adquis", F.lit("NO_INFORMADO")))
            .withColumn("estado_cli", F.when(F.upper(F.trim("estado_cli")).isin("A", "ACT", "ACTIVO"), "ACTIVO")
                                       .otherwise(F.upper(F.trim("estado_cli")))))
    ok, rej = check(df, "tb_clientes_core", [
        ("campo_obligatorio_nulo", "id_cli IS NULL OR num_doc IS NULL OR fec_alta IS NULL"),
        ("fec_nac_fuera_de_rango", f"fec_nac IS NULL OR NOT (fec_nac BETWEEN date'1900-01-01' AND date'{AS_OF}')")])
    ok = (ok.withColumn("num_doc_hash", hash_("num_doc")).drop("num_doc")        # PII: hash del documento
            .withColumn("nomb_cli", mask("nomb_cli")).withColumn("apell_cli", mask("apell_cli")))
    return finish("tb_clientes_core", t0, raw.count(), df, ok, rej)

def run_obligaciones():
    t0, raw = time.time(), B("tb_obligaciones")
    d = F.col("dias_mora_act")
    calif = F.when(d <= 0, "A").when(d <= 30, "B").when(d <= 60, "C").when(d <= 90, "D").otherwise("E")
    df = (raw.dropDuplicates().join(ids("tb_clientes_core", "id_cli", "_fk_cli"), "id_cli", "left")
             .withColumn("calif_riesgo", F.coalesce("calif_riesgo", calif)))
    ok, rej = check(df, "tb_obligaciones", [
        ("campo_obligatorio_nulo", "id_oblig IS NULL OR id_cli IS NULL OR cod_prod IS NULL"),
        ("id_cli_inexistente", "_fk_cli IS NULL"),
        ("mora_negativa", "dias_mora_act < 0"),
        ("saldo_mayor_que_desembolsado", "sdo_capital > vr_desembolsado")])
    return finish("tb_obligaciones", t0, raw.count(), df, ok.drop("_fk_cli"), rej)

def run_movimientos():
    t0, raw = time.time(), B("tb_mov_financieros")
    df = raw.dropDuplicates().join(ids("tb_clientes_core", "id_cli", "_fk_cli"), "id_cli", "left")   # quita duplicados exactos
    ok, rej = check(df, "tb_mov_financieros", [
        ("campo_obligatorio_nulo", "id_mov IS NULL OR id_cli IS NULL OR fec_mov IS NULL OR vr_mov IS NULL"),
        ("id_cli_inexistente", "_fk_cli IS NULL"),
        ("fecha_fuera_de_rango", f"NOT (fec_mov BETWEEN date'{PERIODO[0]}' AND date'{PERIODO[1]}')"),
        ("monto_no_positivo", "vr_mov <= 0")])
    ok = (ok.drop("_fk_cli").withColumn("cod_ciudad", F.coalesce("cod_ciudad", F.lit("SIN_CIUDAD")))
            .withColumn("dispositivo_nulo", F.col("id_dispositivo").isNull()))
    # ind_sospechoso: monto mayor al promedio + 3 desviaciones estándar de los 30 días previos del mismo cliente
    dia = F.datediff(F.col("fec_mov"), F.lit("1970-01-01").cast("date"))
    w = Window.partitionBy("id_cli").orderBy(dia).rangeBetween(-30, -1)
    ok = (ok.withColumn("prom_30d", F.avg("vr_mov").over(w))
            .withColumn("desv_30d", F.stddev("vr_mov").over(w))
            .withColumn("n_30d", F.count("vr_mov").over(w))
            .withColumn("ind_sospechoso",
                        F.when((F.col("n_30d") >= 5) & (F.col("vr_mov") > F.col("prom_30d") + 3 * F.col("desv_30d")), 1)
                         .otherwise(0)))
    return finish("tb_mov_financieros", t0, raw.count(), df, ok, rej)

def run_comisiones():
    t0, raw = time.time(), B("tb_comisiones_log")
    df = (raw.dropDuplicates().join(ids("tb_clientes_core", "id_cli", "_fk_cli"), "id_cli", "left")
             .join(ids("tb_productos_cat", "cod_prod", "_fk_prod"), "cod_prod", "left")
             .withColumn("tip_comision", F.coalesce("tip_comision", F.lit("SIN_CLASIFICAR"))))
    ok, rej = check(df, "tb_comisiones_log", [
        ("campo_obligatorio_nulo", "id_comision IS NULL OR id_cli IS NULL OR cod_prod IS NULL"),
        ("id_cli_inexistente", "_fk_cli IS NULL"),
        ("cod_prod_inexistente", "_fk_prod IS NULL"),
        ("monto_no_positivo", "vr_comision <= 0")])
    return finish("tb_comisiones_log", t0, raw.count(), df, ok.drop("_fk_cli", "_fk_prod"), rej)

# COMMAND ----------
# El orden importa: las tablas que dependen de clientes y productos van después
ORDEN = [("tb_productos_cat", run_productos), ("tb_sucursales_red", run_sucursales),
         ("tb_clientes_core", run_clientes), ("tb_obligaciones", run_obligaciones),
         ("tb_mov_financieros", run_movimientos), ("tb_comisiones_log", run_comisiones)]
res = [guarded("silver", n, f) for n, f in ORDEN]
fail_if_any(res, "silver")
print(dict(zip([n for n, _ in ORDEN], res)))
