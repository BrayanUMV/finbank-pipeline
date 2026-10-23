# Databricks notebook source
# MAGIC %run ./00_common

# COMMAND ----------
print("1. Cuenta de almacenamiento:", ACCT)
print("2. Contenido de bronze:", dbutils.fs.ls(path("bronze", "")))

# COMMAND ----------
df = spark.read.format("jdbc").options(**PG, dbtable="(SELECT COUNT(*) AS n FROM tb_clientes_core) t").load()
print("3. Clientes en PostgreSQL:", df.first()["n"])

# COMMAND ----------
send_mail("[PRUEBA] FinBank", "Si lees esto, el correo de alertas funciona.")
print("4. Correo enviado")

for t in ["tb_productos_cat", "tb_sucursales_red", "tb_clientes_core",
          "tb_mov_financieros", "tb_obligaciones", "tb_comisiones_log"]:
    d = spark.read.format("delta").load(path("bronze", t))
    print(t, d.count(), "filas | lotes:", d.select("_batch_id").distinct().count())

m = spark.read.format("delta").load(path("bronze", "tb_mov_financieros"))
print("Duplicados que conserva Bronze:", m.count() - m.select("id_mov").distinct().count())   # esperado: 5000
m.printSchema()
display(spark.read.format("delta").load(path("gold", "ops/run_log")))
print(dbutils.fs.ls(path("bronze", "tb_mov_financieros")))