# Databricks notebook source
import time, uuid, json, smtplib, functools
from email.message import EmailMessage
from datetime import datetime, timezone
from pyspark.sql import functions as F, Window
from delta.tables import DeltaTable

# Identificador de la corrida. En el job diario lo entrega Databricks; a mano se genera uno nuevo cada vez.
dbutils.widgets.text("batch_id", "manual")
BATCH_ID = dbutils.widgets.get("batch_id")
if BATCH_ID == "manual":
    BATCH_ID = uuid.uuid4().hex[:12]

S = lambda k: dbutils.secrets.get("finbank", k)      # todos los secretos vienen del secret scope
now_utc = lambda: datetime.now(timezone.utc).isoformat()

ACCT = S("storage-account")
spark.conf.set(f"fs.azure.account.key.{ACCT}.dfs.core.windows.net", S("storage-key"))
def path(capa, nombre): return f"abfss://{capa}@{ACCT}.dfs.core.windows.net/{nombre}"

PG = dict(url=f"jdbc:postgresql://{S('pg-host')}:5432/finbank_source?sslmode=require",
          user=S("pg-user"), password=S("pg-password"), driver="org.postgresql.Driver")

PERIODO = ("2025-10-01", "2026-09-30")   # ventana de datos válida
AS_OF = PERIODO[1]                        # fecha de corte de la cartera
COP_USD = 4000.0                          # supuesto: TRM fija (documentar en el README)
PROVISION = {"A": 0.01, "B": 0.032, "C": 0.20, "D": 0.50, "E": 1.00}   # % del saldo (supuesto simplificado)
UMBRAL_VOLUMEN = 0.30

def retry(tries=3, base=30):
    """Reintentos con espera exponencial: 30 s, 60 s, 120 s."""
    def deco(fn):
        @functools.wraps(fn)
        def wrap(*a, **k):
            for i in range(tries):
                try:
                    return fn(*a, **k)
                except Exception:
                    if i == tries - 1:
                        raise
                    time.sleep(base * 2 ** i)
        return wrap
    return deco

def send_mail(asunto, cuerpo):
    """Envía un correo. Si el envío falla, lo avisa por pantalla pero no detiene el pipeline."""
    try:
        m = EmailMessage()
        m["Subject"], m["From"], m["To"] = asunto, S("smtp-user"), S("alert-email")
        m.set_content(cuerpo)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(S("smtp-user"), S("smtp-pass"))
            s.send_message(m)
    except Exception as e:
        print("No se pudo enviar el correo:", e)

def append_ops(nombre, filas):
    """Tablas operativas (logs, errores, calidad) en gold/ops."""
    spark.createDataFrame(filas).write.format("delta").mode("append").save(path("gold", f"ops/{nombre}"))

def log_run(capa, tabla, filas, segundos, dest):
    tam = spark.sql(f"DESCRIBE DETAIL delta.`{dest}`").first()["sizeInBytes"]
    append_ops("run_log", [dict(ts=now_utc(), batch_id=BATCH_ID, capa=capa, tabla=tabla,
                                filas=int(filas), size_bytes=int(tam), segundos=round(segundos, 1))])
    # Alerta de anomalía de volumen: más de 30% de diferencia contra el promedio de las últimas 7 corridas
    try:
        h = (spark.read.format("delta").load(path("gold", "ops/run_log"))
             .filter(f"capa = '{capa}' AND tabla = '{tabla}' AND batch_id != '{BATCH_ID}'")
             .orderBy(F.desc("ts")).limit(7))
        if h.count() >= 3:
            prom = h.agg(F.avg("filas")).first()[0]
            if prom and abs(filas - prom) / prom > UMBRAL_VOLUMEN:
                send_mail(f"[ALERTA VOLUMEN] {capa}.{tabla}", f"Filas: {filas}. Promedio de las últimas 7 corridas: {prom:.0f}.")
    except Exception as e:
        print("Sin historial suficiente para la alerta de volumen:", e)

def guarded(capa, tabla, fn):
    """Captura el error, lo registra, avisa por correo y deja seguir a las tareas independientes."""
    try:
        return fn()
    except Exception as e:
        append_ops("errores_pipeline", [dict(ts=now_utc(), batch_id=BATCH_ID,
                                             capa=capa, tabla=tabla, error=str(e)[:2000])])
        send_mail(f"[FALLO] FinBank {capa}.{tabla}",
                  f"Capa: {capa}\nTabla: {tabla}\nHora UTC: {now_utc()}\nError: {e}")
        return e

def fail_if_any(resultados, capa):
    fallos = [r for r in resultados if isinstance(r, Exception)]
    if fallos:
        raise Exception(f"{len(fallos)} tarea(s) fallaron en {capa}: {fallos[0]}")