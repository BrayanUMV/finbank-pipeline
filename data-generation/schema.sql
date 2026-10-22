-- Esquema de la base fuente (sistema transaccional legado de FinBank).
-- Se recrea completo en cada ejecución, por lo que la carga es repetible.

DROP TABLE IF EXISTS TB_COMISIONES_LOG CASCADE;
DROP TABLE IF EXISTS TB_MOV_FINANCIEROS CASCADE;
DROP TABLE IF EXISTS TB_OBLIGACIONES CASCADE;
DROP TABLE IF EXISTS TB_CLIENTES_CORE CASCADE;
DROP TABLE IF EXISTS TB_SUCURSALES_RED CASCADE;
DROP TABLE IF EXISTS TB_PRODUCTOS_CAT CASCADE;

CREATE TABLE TB_PRODUCTOS_CAT (
    cod_prod        VARCHAR(10) PRIMARY KEY,
    desc_prod       VARCHAR(100) NOT NULL,
    tip_prod        VARCHAR(30) NOT NULL,
    tasa_ea         NUMERIC(6,4),
    plazo_max_meses INTEGER,
    cuota_min       BIGINT,
    comision_admin  BIGINT,
    estado_prod     VARCHAR(15)
);

CREATE TABLE TB_SUCURSALES_RED (
    cod_suc    VARCHAR(10) PRIMARY KEY,
    nom_suc    VARCHAR(100),
    tip_punto  VARCHAR(20),
    ciudad     VARCHAR(50),
    depto      VARCHAR(50),
    latitud    NUMERIC(9,6),
    longitud   NUMERIC(9,6),
    activo     SMALLINT
);

CREATE TABLE TB_CLIENTES_CORE (
    id_cli       BIGINT PRIMARY KEY,
    nomb_cli     VARCHAR(100),
    apell_cli    VARCHAR(100),
    tip_doc      VARCHAR(5),
    num_doc      VARCHAR(20),
    fec_nac      DATE,
    fec_alta     DATE,
    cod_segmento VARCHAR(5),
    score_buro   INTEGER,
    ciudad_res   VARCHAR(50),
    depto_res    VARCHAR(50),
    estado_cli   VARCHAR(20),
    canal_adquis VARCHAR(20)
);

CREATE TABLE TB_OBLIGACIONES (
    id_oblig        VARCHAR(12) PRIMARY KEY,
    id_cli          BIGINT NOT NULL REFERENCES TB_CLIENTES_CORE (id_cli),
    cod_prod        VARCHAR(10) NOT NULL REFERENCES TB_PRODUCTOS_CAT (cod_prod),
    vr_aprobado     BIGINT,
    vr_desembolsado BIGINT,
    sdo_capital     BIGINT,
    vr_cuota        BIGINT,
    fec_desembolso  DATE,
    fec_venc        DATE,
    dias_mora_act   INTEGER,
    num_cuotas_pend INTEGER,
    calif_riesgo    CHAR(1)
);

-- id_mov NO es llave primaria: la fuente trae duplicados intencionales
-- que el pipeline debe detectar y tratar en Silver.
CREATE TABLE TB_MOV_FINANCIEROS (
    id_mov          BIGINT NOT NULL,
    id_cli          BIGINT NOT NULL REFERENCES TB_CLIENTES_CORE (id_cli),
    cod_prod        VARCHAR(10) NOT NULL REFERENCES TB_PRODUCTOS_CAT (cod_prod),
    num_cuenta      VARCHAR(20),
    fec_mov         DATE,
    hra_mov         TIME,
    vr_mov          BIGINT,
    tip_mov         VARCHAR(30),
    cod_canal       VARCHAR(20),
    cod_ciudad      VARCHAR(10),
    cod_estado_mov  VARCHAR(15),
    id_dispositivo  VARCHAR(30)
);
CREATE INDEX idx_mov_id_mov ON TB_MOV_FINANCIEROS (id_mov);
CREATE INDEX idx_mov_id_cli ON TB_MOV_FINANCIEROS (id_cli);
CREATE INDEX idx_mov_fec ON TB_MOV_FINANCIEROS (fec_mov);

CREATE TABLE TB_COMISIONES_LOG (
    id_comision  VARCHAR(12) PRIMARY KEY,
    id_cli       BIGINT NOT NULL REFERENCES TB_CLIENTES_CORE (id_cli),
    cod_prod     VARCHAR(10) NOT NULL REFERENCES TB_PRODUCTOS_CAT (cod_prod),
    fec_cobro    DATE,
    vr_comision  BIGINT,
    tip_comision VARCHAR(30),
    estado_cobro VARCHAR(15)
);