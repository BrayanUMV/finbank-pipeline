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

## 4. Entorno de ejecución

- Python: 3.12
- Sistema operativo de desarrollo: Windows 11
- Instalación de dependencias:

```bash
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Nota:** se usa una versión estable de Python porque las versiones más recientes aún no tienen paquetes precompilados para algunas librerías (como pyyaml) y obligan a compilarlas. (Fue la primera dificultad que se presento)
