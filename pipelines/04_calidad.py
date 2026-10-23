# Databricks notebook source
# MAGIC %run ./00_common

# COMMAND ----------
GD = lambda t: spark.read.format("delta").load(path("gold", t))
BUCKETS = ["Al día", "Rango 1 (1-30)", "Rango 2 (31-60)", "Rango 3 (61-90)", "Deteriorado (más de 90)"]
pruebas = []

def prueba(nombre, problemas, detalle):
    pruebas.append(dict(ts=now_utc(), batch_id=BATCH_ID, prueba=nombre,
                        resultado="APROBADA" if problemas == 0 else "FALLIDA",
                        filas_con_problema=int(problemas), detalle=detalle))

# 1. Llaves sin nulos
prueba("llaves_no_nulas",
       GD("dim_clientes").filter("id_cli IS NULL").count()
       + GD("fact_cartera").filter("id_oblig IS NULL").count()
       + GD("fact_transacciones").filter("id_mov IS NULL").count(),
       "dim_clientes.id_cli, fact_cartera.id_oblig, fact_transacciones.id_mov")

# 2. Unicidad de llaves (comprueba también que los duplicados se eliminaron)
prueba("unicidad_llaves",
       sum(GD(t).count() - GD(t).select(k).distinct().count()
           for t, k in [("dim_clientes", "id_cli"), ("dim_productos", "cod_prod"),
                        ("fact_transacciones", "id_mov"), ("fact_cartera", "id_oblig")]),
       "dim_clientes, dim_productos, fact_transacciones, fact_cartera")

# 3. Integridad referencial hecho -> dimensión
prueba("integridad_hecho_dimension",
       GD("fact_transacciones").join(GD("dim_clientes"), "id_cli", "left_anti").count()
       + GD("fact_cartera").join(GD("dim_productos"), "cod_prod", "left_anti").count()
       + GD("fact_cartera").join(GD("dim_clientes"), "id_cli", "left_anti").count(),
       "transacciones->clientes, cartera->productos, cartera->clientes")

# 4. Fechas dentro del periodo
prueba("fechas_en_periodo",
       GD("fact_transacciones").filter(f"NOT (fec_mov BETWEEN date'{PERIODO[0]}' AND date'{PERIODO[1]}')").count(),
       f"fec_mov entre {PERIODO[0]} y {PERIODO[1]}")

# 5. Valores válidos de bucket_mora y clasificación regulatoria
prueba("valores_validos_mora",
       GD("fact_cartera").filter(~F.col("bucket_mora").isin(BUCKETS)
                                 | ~F.col("clasificacion_regulatoria").isin(list("ABCDE"))).count(),
       "bucket_mora en 5 rangos y clasificacion_regulatoria en A-E")

# 6. Consistencia entre el rango de mora y los días de mora
prueba("consistencia_bucket_dias",
       GD("fact_cartera").filter(((F.col("bucket_mora") == "Al día") & (F.col("dias_mora_act") != 0))
                                 | ((F.col("bucket_mora") == "Deteriorado (más de 90)") & (F.col("dias_mora_act") <= 90))).count(),
       "Al día = 0 días; Deteriorado = más de 90 días")

append_ops("dq_gold", pruebas)
for p in pruebas:
    print(f"{p['prueba']:<30} {p['resultado']:<9} filas con problema: {p['filas_con_problema']}")
if any(p["resultado"] == "FALLIDA" for p in pruebas):
    raise Exception("Fallaron pruebas de calidad en Gold")
