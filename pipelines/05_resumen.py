# Databricks notebook source
# MAGIC %run ./00_common

# COMMAND ----------
rl = spark.read.format("delta").load(path("gold", "ops/run_log"))
# En el job, BATCH_ID es el de la corrida. A mano no coincide con ninguna capa, así que se usa la corrida más reciente.
lote = BATCH_ID if rl.filter(f"batch_id = '{BATCH_ID}'").count() > 0 else rl.orderBy(F.desc("ts")).first()["batch_id"]
OPS = lambda t: spark.read.format("delta").load(path("gold", f"ops/{t}")).filter(f"batch_id = '{lote}'")

por_capa = {r["capa"]: int(r["filas"]) for r in OPS("run_log").groupBy("capa").agg(F.sum("filas").alias("filas")).collect()}
segundos = OPS("run_log").agg(F.sum("segundos")).first()[0] or 0
rechazados = OPS("dq_silver").agg(F.sum("rechazados")).first()[0] or 0
pruebas_falladas = OPS("dq_gold").filter("resultado = 'FALLIDA'").count()

cuerpo = (f"Corrida {lote} completada.\n"
          f"Filas procesadas por capa: {por_capa}\n"
          f"Tiempo total de las tareas: {segundos / 60:.1f} min\n"
          f"Registros rechazados por calidad: {rechazados}\n"
          f"Pruebas de calidad falladas: {pruebas_falladas}")
send_mail("[OK] FinBank pipeline diario", cuerpo)
print(cuerpo)
