# Catálogo de datos

Generado desde los esquemas reales de las capas Silver y Gold. Sensible = contiene datos personales o financieros por cliente.

## silver.tb\_productos\_cat

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|cod\_prod|string|bronze.tb\_productos\_cat.cod\_prod|No|Código del producto|
|desc\_prod|string|bronze.tb\_productos\_cat.desc\_prod|No|Descripción del producto|
|tip\_prod|string|bronze.tb\_productos\_cat.tip\_prod|No|Tipo de producto|
|tasa\_ea|decimal(6,4)|bronze.tb\_productos\_cat.tasa\_ea|No|Tasa efectiva anual|
|plazo\_max\_meses|int|bronze.tb\_productos\_cat.plazo\_max\_meses|No|Plazo máximo en meses|
|cuota\_min|bigint|bronze.tb\_productos\_cat.cuota\_min|No|Cuota mínima en COP|
|comision\_admin|bigint|bronze.tb\_productos\_cat.comision\_admin|No|Comisión administrativa en COP|
|estado\_prod|string|bronze.tb\_productos\_cat.estado\_prod|No|Estado del producto|

## silver.tb\_sucursales\_red

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|cod\_suc|string|bronze.tb\_sucursales\_red.cod\_suc|No|Código de la sucursal o punto de atención|
|nom\_suc|string|bronze.tb\_sucursales\_red.nom\_suc|No|Nombre del punto|
|tip\_punto|string|bronze.tb\_sucursales\_red.tip\_punto|No|Tipo de punto de atención|
|ciudad|string|bronze.tb\_sucursales\_red.ciudad|No|Ciudad|
|depto|string|bronze.tb\_sucursales\_red.depto|No|Departamento|
|latitud|decimal(9,6)|bronze.tb\_sucursales\_red.latitud|No|Latitud|
|longitud|decimal(9,6)|bronze.tb\_sucursales\_red.longitud|No|Longitud|
|activo|smallint|bronze.tb\_sucursales\_red.activo|No|Indica si el punto está activo|
|coordenadas\_nulas|boolean|latitud o longitud nulas|No|Indica si faltan coordenadas|

## silver.tb\_clientes\_core

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|cod\_segmento|string|bronze.tb\_clientes\_core.cod\_segmento|No|Código de segmento (BAS, EST, PRE, ELI)|
|id\_cli|bigint|bronze.tb\_clientes\_core.id\_cli|No|Identificador del cliente|
|nomb\_cli|string|bronze.tb\_clientes\_core.nomb\_cli|Sí (enmascarado)|Nombre del cliente (solo 2 letras visibles)|
|apell\_cli|string|bronze.tb\_clientes\_core.apell\_cli|Sí (enmascarado)|Apellidos del cliente (solo 2 letras visibles)|
|tip\_doc|string|bronze.tb\_clientes\_core.tip\_doc|No|Tipo de documento|
|fec\_nac|date|bronze.tb\_clientes\_core.fec\_nac|Sí (personal)|Fecha de nacimiento|
|fec\_alta|date|bronze.tb\_clientes\_core.fec\_alta|No|Fecha de alta del cliente|
|score\_buro|int|bronze.tb\_clientes\_core.score\_buro|Sí (personal)|Puntaje de buró de crédito (nulos imputados)|
|ciudad\_res|string|bronze.tb\_clientes\_core.ciudad\_res|No|Ciudad de residencia|
|depto\_res|string|bronze.tb\_clientes\_core.depto\_res|No|Departamento de residencia|
|estado\_cli|string|bronze.tb\_clientes\_core.estado\_cli|No|Estado del cliente normalizado|
|canal\_adquis|string|bronze.tb\_clientes\_core.canal\_adquis|No|Canal por el que se adquirió el cliente|
|score\_buro\_imputado|boolean|score\_buro nulo antes de imputar|No|Indica si el score se imputó con la mediana del segmento|
|num\_doc\_hash|string|hash SHA-256 con sal de num\_doc|Sí (hash irreversible)|Documento de identidad convertido en hash irreversible|

## silver.tb\_obligaciones

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|id\_cli|bigint|bronze.tb\_obligaciones.id\_cli|No|Identificador del cliente|
|id\_oblig|string|bronze.tb\_obligaciones.id\_oblig|No|Identificador de la obligación|
|cod\_prod|string|bronze.tb\_obligaciones.cod\_prod|No|Código del producto|
|vr\_aprobado|bigint|bronze.tb\_obligaciones.vr\_aprobado|Sí (financiero)|Valor aprobado en COP|
|vr\_desembolsado|bigint|bronze.tb\_obligaciones.vr\_desembolsado|Sí (financiero)|Valor desembolsado en COP|
|sdo\_capital|bigint|bronze.tb\_obligaciones.sdo\_capital|Sí (financiero)|Saldo de capital en COP|
|vr\_cuota|bigint|bronze.tb\_obligaciones.vr\_cuota|Sí (financiero)|Valor de la cuota en COP|
|fec\_desembolso|date|bronze.tb\_obligaciones.fec\_desembolso|No|Fecha de desembolso|
|fec\_venc|date|bronze.tb\_obligaciones.fec\_venc|No|Fecha de vencimiento|
|dias\_mora\_act|int|bronze.tb\_obligaciones.dias\_mora\_act|No|Días de mora actuales|
|num\_cuotas\_pend|int|bronze.tb\_obligaciones.num\_cuotas\_pend|No|Cuotas pendientes|
|calif\_riesgo|string|bronze.tb\_obligaciones.calif\_riesgo|No|Calificación de riesgo (A a E)|

## silver.tb\_mov\_financieros

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|id\_cli|bigint|bronze.tb\_mov\_financieros.id\_cli|No|Identificador del cliente|
|id\_mov|bigint|bronze.tb\_mov\_financieros.id\_mov|No|Identificador del movimiento|
|cod\_prod|string|bronze.tb\_mov\_financieros.cod\_prod|No|Código del producto|
|num\_cuenta|string|bronze.tb\_mov\_financieros.num\_cuenta|Sí (personal)|Número de cuenta|
|fec\_mov|date|bronze.tb\_mov\_financieros.fec\_mov|No|Fecha del movimiento|
|hra\_mov|string|bronze.tb\_mov\_financieros.hra\_mov|No|Hora del movimiento (texto HH:MM:SS)|
|vr\_mov|bigint|bronze.tb\_mov\_financieros.vr\_mov|Sí (financiero)|Valor del movimiento en COP|
|tip\_mov|string|bronze.tb\_mov\_financieros.tip\_mov|No|Tipo de movimiento|
|cod\_canal|string|bronze.tb\_mov\_financieros.cod\_canal|No|Canal del movimiento|
|cod\_ciudad|string|bronze.tb\_mov\_financieros.cod\_ciudad|No|Código DANE de la ciudad|
|cod\_estado\_mov|string|bronze.tb\_mov\_financieros.cod\_estado\_mov|No|Estado del movimiento|
|id\_dispositivo|string|bronze.tb\_mov\_financieros.id\_dispositivo|Sí (personal)|Dispositivo desde el que se hizo|
|dispositivo\_nulo|boolean|id\_dispositivo nulo|No|Indica si falta el dispositivo|
|prom\_30d|double|promedio de vr\_mov de los 30 días previos del cliente|No|Promedio de los 30 días previos|
|desv\_30d|double|desviación estándar de vr\_mov de los 30 días previos|No|Desviación de los 30 días previos|
|n\_30d|bigint|cantidad de movimientos en los 30 días previos|No|Movimientos en los 30 días previos|
|ind\_sospechoso|int|1 si vr\_mov > prom\_30d + 3 x desv\_30d (con 5 o más movimientos previos)|No|Marca de transacción sospechosa (1 o 0)|

## silver.tb\_comisiones\_log

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|cod\_prod|string|bronze.tb\_comisiones\_log.cod\_prod|No|Código del producto|
|id\_cli|bigint|bronze.tb\_comisiones\_log.id\_cli|No|Identificador del cliente|
|id\_comision|string|bronze.tb\_comisiones\_log.id\_comision|No|Identificador de la comisión|
|fec\_cobro|date|bronze.tb\_comisiones\_log.fec\_cobro|No|Fecha de cobro|
|vr\_comision|bigint|bronze.tb\_comisiones\_log.vr\_comision|Sí (financiero)|Valor de la comisión en COP|
|tip\_comision|string|bronze.tb\_comisiones\_log.tip\_comision|No|Tipo de comisión|
|estado\_cobro|string|bronze.tb\_comisiones\_log.estado\_cobro|No|Estado del cobro|

## gold.dim\_clientes

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|id\_cli|bigint|silver.tb\_clientes\_core.id\_cli|No|Identificador del cliente|
|nombre\_completo|string|nomb\_cli + apell\_cli (ya enmascarados)|Sí (enmascarado)|Nombre completo enmascarado|
|num\_doc\_hash|string|hash SHA-256 con sal de num\_doc|Sí (hash irreversible)|Documento de identidad convertido en hash irreversible|
|edad|bigint|años entre fec\_nac y la fecha de corte|Sí (personal)|Edad en años|
|segmento|string|etiqueta legible de cod\_segmento|No|Segmento del cliente|
|cod\_segmento|string|silver.tb\_clientes\_core.cod\_segmento|No|Código de segmento (BAS, EST, PRE, ELI)|
|ciudad\_res|string|silver.tb\_clientes\_core.ciudad\_res|No|Ciudad de residencia|
|depto\_res|string|silver.tb\_clientes\_core.depto\_res|No|Departamento de residencia|
|estado\_cli|string|silver.tb\_clientes\_core.estado\_cli|No|Estado del cliente normalizado|
|canal\_adquis|string|silver.tb\_clientes\_core.canal\_adquis|No|Canal por el que se adquirió el cliente|
|score\_buro|int|silver.tb\_clientes\_core.score\_buro|Sí (personal)|Puntaje de buró de crédito (nulos imputados)|
|fec\_alta|date|silver.tb\_clientes\_core.fec\_alta|No|Fecha de alta del cliente|

## gold.dim\_productos

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|cod\_prod|string|silver.tb\_productos\_cat.cod\_prod|No|Código del producto|
|nombre\_producto|string|desc\_prod|No|Nombre del producto|
|tipo\_producto|string|tip\_prod|No|Tipo de producto|
|tasa\_ea|decimal(6,4)|silver.tb\_productos\_cat.tasa\_ea|No|Tasa efectiva anual|
|tasa\_mensual|double|(1 + tasa\_ea) ^ (1/12) - 1|No|Tasa mensual equivalente|
|plazo\_max\_meses|int|silver.tb\_productos\_cat.plazo\_max\_meses|No|Plazo máximo en meses|
|cuota\_minima|bigint|cuota\_min|No|Cuota mínima en COP|
|comision\_admin|bigint|silver.tb\_productos\_cat.comision\_admin|No|Comisión administrativa en COP|
|familia|string|Crédito, Ahorro o Transaccional según tip\_prod|No|Familia del producto|
|estado\_prod|string|silver.tb\_productos\_cat.estado\_prod|No|Estado del producto|

## gold.dim\_geografia

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|cod\_ciudad|string|catálogo fijo en 03\_gold.cod\_ciudad|No|Código DANE de la ciudad|
|ciudad|string|catálogo fijo en 03\_gold.ciudad|No|Ciudad|
|depto|string|catálogo fijo en 03\_gold.depto|No|Departamento|

## gold.dim\_canal

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|cod\_canal|string|silver.tb\_sucursales\_red + canales digitales.cod\_canal|No|Canal del movimiento|
|tipo\_canal|string|silver.tb\_sucursales\_red + canales digitales.tipo\_canal|No|Tipo de canal (digital o punto de atención)|

## gold.fact\_transacciones

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|id\_cli|bigint|silver.tb\_mov\_financieros.id\_cli|No|Identificador del cliente|
|id\_mov|bigint|silver.tb\_mov\_financieros.id\_mov|No|Identificador del movimiento|
|cod\_prod|string|silver.tb\_mov\_financieros.cod\_prod|No|Código del producto|
|num\_cuenta|string|silver.tb\_mov\_financieros.num\_cuenta|Sí (personal)|Número de cuenta|
|fec\_mov|date|silver.tb\_mov\_financieros.fec\_mov|No|Fecha del movimiento|
|hra\_mov|string|silver.tb\_mov\_financieros.hra\_mov|No|Hora del movimiento (texto HH:MM:SS)|
|vr\_mov|bigint|silver.tb\_mov\_financieros.vr\_mov|Sí (financiero)|Valor del movimiento en COP|
|tip\_mov|string|silver.tb\_mov\_financieros.tip\_mov|No|Tipo de movimiento|
|cod\_canal|string|silver.tb\_mov\_financieros.cod\_canal|No|Canal del movimiento|
|cod\_ciudad|string|silver.tb\_mov\_financieros.cod\_ciudad|No|Código DANE de la ciudad|
|cod\_estado\_mov|string|silver.tb\_mov\_financieros.cod\_estado\_mov|No|Estado del movimiento|
|id\_dispositivo|string|silver.tb\_mov\_financieros.id\_dispositivo|Sí (personal)|Dispositivo desde el que se hizo|
|dispositivo\_nulo|boolean|id\_dispositivo nulo|No|Indica si falta el dispositivo|
|promedio\_movil\_30d|double|prom\_30d de Silver|No|Promedio móvil de 30 días|
|desv\_30d|double|desviación estándar de vr\_mov de los 30 días previos|No|Desviación de los 30 días previos|
|n\_30d|bigint|cantidad de movimientos en los 30 días previos|No|Movimientos en los 30 días previos|
|ind\_sospechoso|int|1 si vr\_mov > prom\_30d + 3 x desv\_30d (con 5 o más movimientos previos)|No|Marca de transacción sospechosa (1 o 0)|
|monto\_usd|double|vr\_mov / TRM fija de 4,000|Sí (financiero)|Monto en USD|
|horario|string|HABIL si es lunes a viernes entre 8:00 y 17:59|No|HABIL o NO\_HABIL|
|mes|string|año-mes derivado de la fecha|No|Mes del registro|

## gold.fact\_cartera

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|id\_cli|bigint|silver.tb\_obligaciones.id\_cli|No|Identificador del cliente|
|id\_oblig|string|silver.tb\_obligaciones.id\_oblig|No|Identificador de la obligación|
|cod\_prod|string|silver.tb\_obligaciones.cod\_prod|No|Código del producto|
|vr\_aprobado|bigint|silver.tb\_obligaciones.vr\_aprobado|Sí (financiero)|Valor aprobado en COP|
|vr\_desembolsado|bigint|silver.tb\_obligaciones.vr\_desembolsado|Sí (financiero)|Valor desembolsado en COP|
|sdo\_capital|bigint|silver.tb\_obligaciones.sdo\_capital|Sí (financiero)|Saldo de capital en COP|
|vr\_cuota|bigint|silver.tb\_obligaciones.vr\_cuota|Sí (financiero)|Valor de la cuota en COP|
|fec\_desembolso|date|silver.tb\_obligaciones.fec\_desembolso|No|Fecha de desembolso|
|fec\_venc|date|silver.tb\_obligaciones.fec\_venc|No|Fecha de vencimiento|
|dias\_mora\_act|int|silver.tb\_obligaciones.dias\_mora\_act|No|Días de mora actuales|
|num\_cuotas\_pend|int|silver.tb\_obligaciones.num\_cuotas\_pend|No|Cuotas pendientes|
|calif\_riesgo|string|silver.tb\_obligaciones.calif\_riesgo|No|Calificación de riesgo (A a E)|
|bucket\_mora|string|rango según dias\_mora\_act|No|Rango de mora|
|clasificacion\_regulatoria|string|A a E según dias\_mora\_act|No|Clasificación regulatoria A a E|
|provision\_estimada|double|sdo\_capital x porcentaje por clasificación|Sí (financiero)|Provisión estimada en COP|
|fecha\_corte|date|fecha de corte de la cartera|No|Fecha de corte de la cartera|

## gold.fact\_rentabilidad\_cliente

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|id\_cli|bigint|silver.tb\_obligaciones + silver.tb\_comisiones\_log.id\_cli|No|Identificador del cliente|
|mes|date|año-mes derivado de la fecha|No|Mes del registro|
|ingreso\_intereses|double|vr\_desembolsado x tasa\_mensual por cada mes de vigencia|Sí (financiero)|Ingreso estimado por intereses|
|ingreso\_comisiones|bigint|suma de comisiones COBRADAS del mes|Sí (financiero)|Ingreso por comisiones cobradas|
|ingreso\_total|double|ingreso\_intereses + ingreso\_comisiones|Sí (financiero)|Ingreso total del mes|
|cltv\_12m|double|suma de ingreso\_total de los 12 meses calendario más recientes|Sí (financiero)|Valor de vida del cliente a 12 meses|

## gold.kpi\_cartera\_diaria

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|fecha\_corte|date|fecha de corte de la cartera|No|Fecha de corte de la cartera|
|cod\_prod|string|gold.fact\_cartera + gold.dim\_clientes.cod\_prod|No|Código del producto|
|segmento|string|etiqueta legible de cod\_segmento|No|Segmento del cliente|
|ciudad\_res|string|gold.fact\_cartera + gold.dim\_clientes.ciudad\_res|No|Ciudad de residencia|
|obligaciones\_activas|bigint|obligaciones con cuotas pendientes|No|Obligaciones activas|
|monto\_total\_cartera|bigint|suma de sdo\_capital|No|Monto total de cartera|
|monto\_en\_mora|bigint|suma de sdo\_capital con dias\_mora\_act > 0|No|Monto en mora|
|clientes\_en\_mora|bigint|clientes distintos con mora|No|Clientes con alguna obligación en mora|
|tasa\_mora\_pct|double|100 x monto\_en\_mora / monto\_total\_cartera|No|Tasa de mora en porcentaje|

## gold.agg\_regulatorio\_mensual

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|mes|string|año-mes derivado de la fecha|No|Mes del registro|
|cod\_prod|string|gold.fact\_transacciones.cod\_prod|No|Código del producto|
|cod\_canal|string|gold.fact\_transacciones.cod\_canal|No|Canal del movimiento|
|cod\_ciudad|string|gold.fact\_transacciones.cod\_ciudad|No|Código DANE de la ciudad|
|cuentas\_activas|bigint|cuentas distintas con movimientos aprobados|No|Cuentas activas|
|total\_transacciones|bigint|cantidad de movimientos aprobados|No|Total de transacciones|
|volumen\_cop|bigint|suma de vr\_mov|No|Volumen en COP|

## gold.vista\_cliente\_360

|Campo|Tipo|Origen|Sensible|Descripción|
|-|-|-|-|-|
|id\_cli|bigint|gold.dim\_clientes + gold.fact\_transacciones + gold.fact\_cartera.id\_cli|No|Identificador del cliente|
|nombre\_completo|string|nomb\_cli + apell\_cli (ya enmascarados)|Sí (enmascarado)|Nombre completo enmascarado|
|segmento|string|etiqueta legible de cod\_segmento|No|Segmento del cliente|
|ciudad\_res|string|gold.dim\_clientes + gold.fact\_transacciones + gold.fact\_cartera.ciudad\_res|No|Ciudad de residencia|
|productos\_usados|bigint|productos distintos usados por el cliente|No|Productos usados|
|transacciones|bigint|cantidad de movimientos del cliente|No|Transacciones del cliente|
|volumen\_cop|bigint|suma de vr\_mov|No|Volumen en COP|
|pagos\_realizados|bigint|pagos de cuota aprobados|No|Pagos realizados|
|ultimo\_pago|date|fecha del último pago de cuota|No|Fecha del último pago|
|max\_dias\_mora|int|mayor dias\_mora\_act del cliente|No|Máximo de días de mora|
|peor\_calificacion|string|peor clasificación regulatoria del cliente|No|Peor calificación regulatoria|
|saldo\_total|bigint|suma de sdo\_capital del cliente|Sí (financiero)|Saldo total en COP|



