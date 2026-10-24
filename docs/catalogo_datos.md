# Catálogo de datos

Generado desde los esquemas reales de las capas Silver y Gold. Sensible = contiene datos personales o financieros por cliente.

## silver.tb_productos_cat

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| cod_prod | string | bronze.tb_productos_cat.cod_prod | No | Código del producto |
| desc_prod | string | bronze.tb_productos_cat.desc_prod | No | Descripción del producto |
| tip_prod | string | bronze.tb_productos_cat.tip_prod | No | Tipo de producto |
| tasa_ea | decimal(6,4) | bronze.tb_productos_cat.tasa_ea | No | Tasa efectiva anual |
| plazo_max_meses | int | bronze.tb_productos_cat.plazo_max_meses | No | Plazo máximo en meses |
| cuota_min | bigint | bronze.tb_productos_cat.cuota_min | No | Cuota mínima en COP |
| comision_admin | bigint | bronze.tb_productos_cat.comision_admin | No | Comisión administrativa en COP |
| estado_prod | string | bronze.tb_productos_cat.estado_prod | No | Estado del producto |

## silver.tb_sucursales_red

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| cod_suc | string | bronze.tb_sucursales_red.cod_suc | No | Código de la sucursal o punto de atención |
| nom_suc | string | bronze.tb_sucursales_red.nom_suc | No | Nombre del punto |
| tip_punto | string | bronze.tb_sucursales_red.tip_punto | No | Tipo de punto de atención |
| ciudad | string | bronze.tb_sucursales_red.ciudad | No | Ciudad |
| depto | string | bronze.tb_sucursales_red.depto | No | Departamento |
| latitud | decimal(9,6) | bronze.tb_sucursales_red.latitud | No | Latitud |
| longitud | decimal(9,6) | bronze.tb_sucursales_red.longitud | No | Longitud |
| activo | smallint | bronze.tb_sucursales_red.activo | No | Indica si el punto está activo |
| coordenadas_nulas | boolean | latitud o longitud nulas | No | Indica si faltan coordenadas |

## silver.tb_clientes_core

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| cod_segmento | string | bronze.tb_clientes_core.cod_segmento | No | Código de segmento (BAS, EST, PRE, ELI) |
| id_cli | bigint | bronze.tb_clientes_core.id_cli | No | Identificador del cliente |
| nomb_cli | string | bronze.tb_clientes_core.nomb_cli | Sí (enmascarado) | Nombre del cliente (solo 2 letras visibles) |
| apell_cli | string | bronze.tb_clientes_core.apell_cli | Sí (enmascarado) | Apellidos del cliente (solo 2 letras visibles) |
| tip_doc | string | bronze.tb_clientes_core.tip_doc | No | Tipo de documento |
| fec_nac | date | bronze.tb_clientes_core.fec_nac | Sí (personal) | Fecha de nacimiento |
| fec_alta | date | bronze.tb_clientes_core.fec_alta | No | Fecha de alta del cliente |
| score_buro | int | bronze.tb_clientes_core.score_buro | Sí (personal) | Puntaje de buró de crédito (nulos imputados) |
| ciudad_res | string | bronze.tb_clientes_core.ciudad_res | No | Ciudad de residencia |
| depto_res | string | bronze.tb_clientes_core.depto_res | No | Departamento de residencia |
| estado_cli | string | bronze.tb_clientes_core.estado_cli | No | Estado del cliente normalizado |
| canal_adquis | string | bronze.tb_clientes_core.canal_adquis | No | Canal por el que se adquirió el cliente |
| score_buro_imputado | boolean | score_buro nulo antes de imputar | No | Indica si el score se imputó con la mediana del segmento |
| num_doc_hash | string | hash SHA-256 con sal de num_doc | Sí (hash irreversible) | Documento de identidad convertido en hash irreversible |

## silver.tb_obligaciones

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| id_cli | bigint | bronze.tb_obligaciones.id_cli | No | Identificador del cliente |
| id_oblig | string | bronze.tb_obligaciones.id_oblig | No | Identificador de la obligación |
| cod_prod | string | bronze.tb_obligaciones.cod_prod | No | Código del producto |
| vr_aprobado | bigint | bronze.tb_obligaciones.vr_aprobado | Sí (financiero) | Valor aprobado en COP |
| vr_desembolsado | bigint | bronze.tb_obligaciones.vr_desembolsado | Sí (financiero) | Valor desembolsado en COP |
| sdo_capital | bigint | bronze.tb_obligaciones.sdo_capital | Sí (financiero) | Saldo de capital en COP |
| vr_cuota | bigint | bronze.tb_obligaciones.vr_cuota | Sí (financiero) | Valor de la cuota en COP |
| fec_desembolso | date | bronze.tb_obligaciones.fec_desembolso | No | Fecha de desembolso |
| fec_venc | date | bronze.tb_obligaciones.fec_venc | No | Fecha de vencimiento |
| dias_mora_act | int | bronze.tb_obligaciones.dias_mora_act | No | Días de mora actuales |
| num_cuotas_pend | int | bronze.tb_obligaciones.num_cuotas_pend | No | Cuotas pendientes |
| calif_riesgo | string | bronze.tb_obligaciones.calif_riesgo | No | Calificación de riesgo (A a E) |

## silver.tb_mov_financieros

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| id_cli | bigint | bronze.tb_mov_financieros.id_cli | No | Identificador del cliente |
| id_mov | bigint | bronze.tb_mov_financieros.id_mov | No | Identificador del movimiento |
| cod_prod | string | bronze.tb_mov_financieros.cod_prod | No | Código del producto |
| num_cuenta | string | bronze.tb_mov_financieros.num_cuenta | Sí (personal) | Número de cuenta |
| fec_mov | date | bronze.tb_mov_financieros.fec_mov | No | Fecha del movimiento |
| hra_mov | string | bronze.tb_mov_financieros.hra_mov | No | Hora del movimiento (texto HH:MM:SS) |
| vr_mov | bigint | bronze.tb_mov_financieros.vr_mov | Sí (financiero) | Valor del movimiento en COP |
| tip_mov | string | bronze.tb_mov_financieros.tip_mov | No | Tipo de movimiento |
| cod_canal | string | bronze.tb_mov_financieros.cod_canal | No | Canal del movimiento |
| cod_ciudad | string | bronze.tb_mov_financieros.cod_ciudad | No | Código DANE de la ciudad |
| cod_estado_mov | string | bronze.tb_mov_financieros.cod_estado_mov | No | Estado del movimiento |
| id_dispositivo | string | bronze.tb_mov_financieros.id_dispositivo | Sí (personal) | Dispositivo desde el que se hizo |
| dispositivo_nulo | boolean | id_dispositivo nulo | No | Indica si falta el dispositivo |
| prom_30d | double | promedio de vr_mov de los 30 días previos del cliente | No | Promedio de los 30 días previos |
| desv_30d | double | desviación estándar de vr_mov de los 30 días previos | No | Desviación de los 30 días previos |
| n_30d | bigint | cantidad de movimientos en los 30 días previos | No | Movimientos en los 30 días previos |
| ind_sospechoso | int | 1 si vr_mov > prom_30d + 3 x desv_30d (con 5 o más movimientos previos) | No | Marca de transacción sospechosa (1 o 0) |

## silver.tb_comisiones_log

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| cod_prod | string | bronze.tb_comisiones_log.cod_prod | No | Código del producto |
| id_cli | bigint | bronze.tb_comisiones_log.id_cli | No | Identificador del cliente |
| id_comision | string | bronze.tb_comisiones_log.id_comision | No | Identificador de la comisión |
| fec_cobro | date | bronze.tb_comisiones_log.fec_cobro | No | Fecha de cobro |
| vr_comision | bigint | bronze.tb_comisiones_log.vr_comision | Sí (financiero) | Valor de la comisión en COP |
| tip_comision | string | bronze.tb_comisiones_log.tip_comision | No | Tipo de comisión |
| estado_cobro | string | bronze.tb_comisiones_log.estado_cobro | No | Estado del cobro |

## gold.dim_clientes

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| id_cli | bigint | silver.tb_clientes_core.id_cli | No | Identificador del cliente |
| nombre_completo | string | nomb_cli + apell_cli (ya enmascarados) | Sí (enmascarado) | Nombre completo enmascarado |
| num_doc_hash | string | hash SHA-256 con sal de num_doc | Sí (hash irreversible) | Documento de identidad convertido en hash irreversible |
| edad | bigint | años entre fec_nac y la fecha de corte | Sí (personal) | Edad en años |
| segmento | string | etiqueta legible de cod_segmento | No | Segmento del cliente |
| cod_segmento | string | silver.tb_clientes_core.cod_segmento | No | Código de segmento (BAS, EST, PRE, ELI) |
| ciudad_res | string | silver.tb_clientes_core.ciudad_res | No | Ciudad de residencia |
| depto_res | string | silver.tb_clientes_core.depto_res | No | Departamento de residencia |
| estado_cli | string | silver.tb_clientes_core.estado_cli | No | Estado del cliente normalizado |
| canal_adquis | string | silver.tb_clientes_core.canal_adquis | No | Canal por el que se adquirió el cliente |
| score_buro | int | silver.tb_clientes_core.score_buro | Sí (personal) | Puntaje de buró de crédito (nulos imputados) |
| fec_alta | date | silver.tb_clientes_core.fec_alta | No | Fecha de alta del cliente |

## gold.dim_productos

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| cod_prod | string | silver.tb_productos_cat.cod_prod | No | Código del producto |
| nombre_producto | string | desc_prod | No | Nombre del producto |
| tipo_producto | string | tip_prod | No | Tipo de producto |
| tasa_ea | decimal(6,4) | silver.tb_productos_cat.tasa_ea | No | Tasa efectiva anual |
| tasa_mensual | double | (1 + tasa_ea) ^ (1/12) - 1 | No | Tasa mensual equivalente |
| plazo_max_meses | int | silver.tb_productos_cat.plazo_max_meses | No | Plazo máximo en meses |
| cuota_minima | bigint | cuota_min | No | Cuota mínima en COP |
| comision_admin | bigint | silver.tb_productos_cat.comision_admin | No | Comisión administrativa en COP |
| familia | string | Crédito, Ahorro o Transaccional según tip_prod | No | Familia del producto |
| estado_prod | string | silver.tb_productos_cat.estado_prod | No | Estado del producto |

## gold.dim_geografia

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| cod_ciudad | string | catálogo fijo en 03_gold.cod_ciudad | No | Código DANE de la ciudad |
| ciudad | string | catálogo fijo en 03_gold.ciudad | No | Ciudad |
| depto | string | catálogo fijo en 03_gold.depto | No | Departamento |

## gold.dim_canal

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| cod_canal | string | silver.tb_sucursales_red + canales digitales.cod_canal | No | Canal del movimiento |
| tipo_canal | string | silver.tb_sucursales_red + canales digitales.tipo_canal | No | Tipo de canal (digital o punto de atención) |

## gold.fact_transacciones

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| id_cli | bigint | silver.tb_mov_financieros.id_cli | No | Identificador del cliente |
| id_mov | bigint | silver.tb_mov_financieros.id_mov | No | Identificador del movimiento |
| cod_prod | string | silver.tb_mov_financieros.cod_prod | No | Código del producto |
| num_cuenta | string | silver.tb_mov_financieros.num_cuenta | Sí (personal) | Número de cuenta |
| fec_mov | date | silver.tb_mov_financieros.fec_mov | No | Fecha del movimiento |
| hra_mov | string | silver.tb_mov_financieros.hra_mov | No | Hora del movimiento (texto HH:MM:SS) |
| vr_mov | bigint | silver.tb_mov_financieros.vr_mov | Sí (financiero) | Valor del movimiento en COP |
| tip_mov | string | silver.tb_mov_financieros.tip_mov | No | Tipo de movimiento |
| cod_canal | string | silver.tb_mov_financieros.cod_canal | No | Canal del movimiento |
| cod_ciudad | string | silver.tb_mov_financieros.cod_ciudad | No | Código DANE de la ciudad |
| cod_estado_mov | string | silver.tb_mov_financieros.cod_estado_mov | No | Estado del movimiento |
| id_dispositivo | string | silver.tb_mov_financieros.id_dispositivo | Sí (personal) | Dispositivo desde el que se hizo |
| dispositivo_nulo | boolean | id_dispositivo nulo | No | Indica si falta el dispositivo |
| promedio_movil_30d | double | prom_30d de Silver | No | Promedio móvil de 30 días |
| desv_30d | double | desviación estándar de vr_mov de los 30 días previos | No | Desviación de los 30 días previos |
| n_30d | bigint | cantidad de movimientos en los 30 días previos | No | Movimientos en los 30 días previos |
| ind_sospechoso | int | 1 si vr_mov > prom_30d + 3 x desv_30d (con 5 o más movimientos previos) | No | Marca de transacción sospechosa (1 o 0) |
| monto_usd | double | vr_mov / TRM fija de 4,000 | Sí (financiero) | Monto en USD |
| horario | string | HABIL si es lunes a viernes entre 8:00 y 17:59 | No | HABIL o NO_HABIL |
| mes | string | año-mes derivado de la fecha | No | Mes del registro |

## gold.fact_cartera

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| id_cli | bigint | silver.tb_obligaciones.id_cli | No | Identificador del cliente |
| id_oblig | string | silver.tb_obligaciones.id_oblig | No | Identificador de la obligación |
| cod_prod | string | silver.tb_obligaciones.cod_prod | No | Código del producto |
| vr_aprobado | bigint | silver.tb_obligaciones.vr_aprobado | Sí (financiero) | Valor aprobado en COP |
| vr_desembolsado | bigint | silver.tb_obligaciones.vr_desembolsado | Sí (financiero) | Valor desembolsado en COP |
| sdo_capital | bigint | silver.tb_obligaciones.sdo_capital | Sí (financiero) | Saldo de capital en COP |
| vr_cuota | bigint | silver.tb_obligaciones.vr_cuota | Sí (financiero) | Valor de la cuota en COP |
| fec_desembolso | date | silver.tb_obligaciones.fec_desembolso | No | Fecha de desembolso |
| fec_venc | date | silver.tb_obligaciones.fec_venc | No | Fecha de vencimiento |
| dias_mora_act | int | silver.tb_obligaciones.dias_mora_act | No | Días de mora actuales |
| num_cuotas_pend | int | silver.tb_obligaciones.num_cuotas_pend | No | Cuotas pendientes |
| calif_riesgo | string | silver.tb_obligaciones.calif_riesgo | No | Calificación de riesgo (A a E) |
| bucket_mora | string | rango según dias_mora_act | No | Rango de mora |
| clasificacion_regulatoria | string | A a E según dias_mora_act | No | Clasificación regulatoria A a E |
| provision_estimada | double | sdo_capital x porcentaje por clasificación | Sí (financiero) | Provisión estimada en COP |
| fecha_corte | date | fecha de corte de la cartera | No | Fecha de corte de la cartera |

## gold.fact_rentabilidad_cliente

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| id_cli | bigint | silver.tb_obligaciones + silver.tb_comisiones_log.id_cli | No | Identificador del cliente |
| mes | date | año-mes derivado de la fecha | No | Mes del registro |
| ingreso_intereses | double | vr_desembolsado x tasa_mensual por cada mes de vigencia | Sí (financiero) | Ingreso estimado por intereses |
| ingreso_comisiones | bigint | suma de comisiones COBRADAS del mes | Sí (financiero) | Ingreso por comisiones cobradas |
| ingreso_total | double | ingreso_intereses + ingreso_comisiones | Sí (financiero) | Ingreso total del mes |
| cltv_12m | double | suma de ingreso_total de los 12 meses calendario más recientes | Sí (financiero) | Valor de vida del cliente a 12 meses |

## gold.kpi_cartera_diaria

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| fecha_corte | date | fecha de corte de la cartera | No | Fecha de corte de la cartera |
| cod_prod | string | gold.fact_cartera + gold.dim_clientes.cod_prod | No | Código del producto |
| segmento | string | etiqueta legible de cod_segmento | No | Segmento del cliente |
| ciudad_res | string | gold.fact_cartera + gold.dim_clientes.ciudad_res | No | Ciudad de residencia |
| obligaciones_activas | bigint | obligaciones con cuotas pendientes | No | Obligaciones activas |
| monto_total_cartera | bigint | suma de sdo_capital | No | Monto total de cartera |
| monto_en_mora | bigint | suma de sdo_capital con dias_mora_act > 0 | No | Monto en mora |
| clientes_en_mora | bigint | clientes distintos con mora | No | Clientes con alguna obligación en mora |
| tasa_mora_pct | double | 100 x monto_en_mora / monto_total_cartera | No | Tasa de mora en porcentaje |

## gold.agg_regulatorio_mensual

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| mes | string | año-mes derivado de la fecha | No | Mes del registro |
| cod_prod | string | gold.fact_transacciones.cod_prod | No | Código del producto |
| cod_canal | string | gold.fact_transacciones.cod_canal | No | Canal del movimiento |
| cod_ciudad | string | gold.fact_transacciones.cod_ciudad | No | Código DANE de la ciudad |
| cuentas_activas | bigint | cuentas distintas con movimientos aprobados | No | Cuentas activas |
| total_transacciones | bigint | cantidad de movimientos aprobados | No | Total de transacciones |
| volumen_cop | bigint | suma de vr_mov | No | Volumen en COP |

## gold.vista_cliente_360

| Campo | Tipo | Origen | Sensible | Descripción |
|---|---|---|---|---|
| id_cli | bigint | gold.dim_clientes + gold.fact_transacciones + gold.fact_cartera.id_cli | No | Identificador del cliente |
| nombre_completo | string | nomb_cli + apell_cli (ya enmascarados) | Sí (enmascarado) | Nombre completo enmascarado |
| segmento | string | etiqueta legible de cod_segmento | No | Segmento del cliente |
| ciudad_res | string | gold.dim_clientes + gold.fact_transacciones + gold.fact_cartera.ciudad_res | No | Ciudad de residencia |
| productos_usados | bigint | productos distintos usados por el cliente | No | Productos usados |
| transacciones | bigint | cantidad de movimientos del cliente | No | Transacciones del cliente |
| volumen_cop | bigint | suma de vr_mov | No | Volumen en COP |
| pagos_realizados | bigint | pagos de cuota aprobados | No | Pagos realizados |
| ultimo_pago | date | fecha del último pago de cuota | No | Fecha del último pago |
| max_dias_mora | int | mayor dias_mora_act del cliente | No | Máximo de días de mora |
| peor_calificacion | string | peor clasificación regulatoria del cliente | No | Peor calificación regulatoria |
| saldo_total | bigint | suma de sdo_capital del cliente | Sí (financiero) | Saldo total en COP |
