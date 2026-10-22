\# Changelog



\## 2026-10-21 - BrayanUMV

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

