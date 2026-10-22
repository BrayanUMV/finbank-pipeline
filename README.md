\# FinBank Data Pipeline



	1\. Decisiones iniciales



\- Sector elegido: Escenario A, Banca y Servicios Financieros (FinBank S.A.).

\- Plataforma cloud: Microsoft Azure.

\- Justificación del sector: el escenario tiene el volumen de datos más manejable (alrededor de 620 mil registros en total), reglas de negocio bien definidas (mora, CLTV, transacciones sospechosas) y sirve para demostrar enmascaramiento de datos sensibles, que es un tema central en banca.

\- Justificación de la plataforma: integración con el ecosistema Microsoft, ADLS Gen2 para el data lake, Databricks para el procesamiento, y alineación con el stack que usa DATAKNOW.



	2\. Arquitectura







	3\. Estructura del repositorio



\- `/infra`: código de infraestructura como código (Terraform).

\- `/data-generation`: scripts para generar datos sintéticos.

\- `/pipelines`: transformaciones de las capas Bronze, Silver y Gold.

\- `/orchestration`: definición del flujo orquestado.

\- `/docs`: diagramas, catálogo de datos y diagrama ER.

	4\. Entorno de ejecución

- Python: 3.12
- Sistema operativo de desarrollo: Windows 11
- Instalación de dependencias:

```bash
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Nota:** se usa una versión estable de Python porque las versiones más recientes aún no tienen paquetes precompilados para algunas librerías (como pyyaml) y obligan a compilarlas. (Fue la primera dificultad que se presento)

	5\. Supuestos

- Los datos de FinBank se modelan para Colombia (COP, Superintendencia Financiera, PSE, ACH), con 12 ciudades principales.
- `comision_admin` está en COP: mensual para créditos y ahorro, por transacción para productos transaccionales.

- Las obligaciones se desembolsan desde octubre 2024 para que exista cartera con historial; los movimientos y comisiones cubren octubre 2025 a septiembre 2026.
- Se generan 7 patrones de anomalías, registrados en `data/raw/anomalies_log.json`: fechas de nacimiento futuras, estados inconsistentes, fechas de movimiento fuera de rango, montos negativos, transacciones duplicadas, saldos mayores al desembolso y días de mora negativos.
- Los nulos en `id_dispositivo` incluyen un nulo estructural: las operaciones por corresponsal no tienen dispositivo.

	6\. Fase 1: generación de datos y carga

```bash
# 1. Levantar PostgreSQL (copiar data-generation/.env.example a .env y poner una contraseña)
cd data-generation
docker compose up -d
cd ..

# 2. Generar los datos sintéticos (semilla fija: resultado reproducible)
python data-generation/generate_data.py

# 3. Crear el esquema y cargar la base fuente
python data-generation/load_to_postgres.py
```

- Parámetros de generación: `data-generation/config.yaml`.
- Diagrama ER: `docs/er_diagram.md`.
- Evidencia de carga: `docs/evidencia_fase1_conteos.txt`.
