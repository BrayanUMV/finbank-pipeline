\# Changelog



&#x09;	## 2026-10-21 - BrayanUMV



\- Estructura inicial del repositorio.

\- Se agregó .gitignore para excluir credenciales, estado de Terraform y datos.

\- Se creó el README con las decisiones iniciales (sector y plataforma).



\- Entorno virtual de Python 3.12 y requirements.txt.

\- Sección de entorno de ejecución en el README.

\- Archivo config.yaml con semilla, volúmenes, rango de fechas, tasas de calidad y formatos de salida.



\- PostgreSQL 16 en Docker como base fuente, con credenciales en .env (excluido de Git) y plantilla .env.example.



\- Generador de datos sintéticos (tablas maestras): productos, sucursales y clientes, con semilla fija, nulos y anomalías controladas.



\- Generador de tablas transaccionales: obligaciones, movimientos y comisiones.

\- Anomalías documentadas (7 patrones) y picos atípicos para el motor de fraude.



\- Diagrama ER de la base fuente en docs/er\_diagram.md.

\- Instrucciones de reproducción de la Fase 1 en el README.



&#x09;	## 2026-10-22 - BrayanUMV



\- Fase 2: infraestructura en Azure con Terraform (grupo de recursos, ADLS Gen2 con bronze/silver/gold, Key Vault, PostgreSQL, Log Analytics, Action Group, Databricks, roles).

\- Región de PostgreSQL parametrizada (pg\_location) porque la región principal no ofrecía PostgreSQL 16.

\- Base fuente cargada en PostgreSQL de Azure.



\- Fase 3: notebook común con reintentos, alertas y registro de corridas.

\- Capa Bronze incremental con auditoría y partición por fecha de ingesta.



\- Capa Silver con limpieza, validación de llaves, tabla de errores, hash de PII y bandera de fraude.



\- Pruebas de calidad automáticas sobre Gold con reporte de aprobación o fallo.

\- Notebook de resumen diario por correo.

