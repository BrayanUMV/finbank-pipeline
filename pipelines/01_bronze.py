# Databricks notebook source
# MAGIC %run ./00_common

# COMMAND ----------
dbutils.widgets.text("simular_error", "no")
FULL = ["tb_productos_cat", "tb_sucursales_red", "tb_clientes_core"]          # dimensiones: copia completa
INCR = {"tb_mov_financieros": "id_mov", "tb_obligaciones": "id_oblig",         # hechos: incremental por llave
        "tb_comisiones_log": "id_comision"}
# TIME de PostgreSQL se lee como texto para evitar conversiones de zona horaria
SEL = {"tb_mov_financieros": "id_mov, id_cli, cod_prod, num_cuenta, fec_mov, hra_mov::text AS hra_mov, "
                             "vr_mov, tip_mov, cod_canal, cod_ciudad, cod_estado_mov, id_dispositivo"}

@retry()
def ingest(tabla, key=None):
    t0, dest = time.time(), path("bronze", tabla)
    if dbutils.widgets.get("simular_error") == "si" and tabla == "tb_comisiones_log":
        raise ValueError("Fallo simulado para probar las alertas")
    where = ""
    if key and DeltaTable.isDeltaTable(spark, dest):
        last = spark.read.format("delta").load(dest).agg(F.max(key)).first()[0]
        where = f" WHERE {key} > " + (f"'{last}'" if isinstance(last, str) else str(last))
    q = f"(SELECT {SEL.get(tabla, '*')} FROM {tabla}{where}) t"
    now = F.current_timestamp()
    df = (spark.read.format("jdbc").options(**PG, dbtable=q).load()
          .withColumn("_ingest_ts", now)
          .withColumn("_source_system", F.lit("postgres_finbank"))
          .withColumn("_batch_id", F.lit(BATCH_ID))
          .withColumn("ing_anio", F.year(now)).withColumn("ing_mes", F.month(now)).withColumn("ing_dia", F.dayofmonth(now)))
    w = df.write.format("delta").partitionBy("ing_anio", "ing_mes", "ing_dia")
    (w.mode("append") if key else w.mode("overwrite").option("overwriteSchema", "true")).save(dest)
    n = spark.read.format("delta").load(dest).filter(f"_batch_id = '{BATCH_ID}'").count()
    log_run("bronze", tabla, n, time.time() - t0, dest)
    return n

res = [guarded("bronze", t, lambda t=t: ingest(t)) for t in FULL]
res += [guarded("bronze", t, lambda t=t, k=k: ingest(t, k)) for t, k in INCR.items()]
fail_if_any(res, "bronze")
print(dict(zip(FULL + list(INCR), res)))