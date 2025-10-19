-- Borrar primero la tabla de hechos (tiene FKs)
DROP TABLE IF EXISTS hecho_ventas CASCADE;

-- Luego las dimensiones
DROP TABLE IF EXISTS dim_producto CASCADE;
DROP TABLE IF EXISTS dim_cliente  CASCADE;
DROP TABLE IF EXISTS dim_tiempo   CASCADE;

-- Dimensión Cliente
CREATE TABLE dim_cliente (
    id_cliente     SERIAL PRIMARY KEY,
    nombre_cliente VARCHAR(50),
    edad           INT ,
    ubicacion      VARCHAR(100),
    categoria      VARCHAR(50)
);

-- Dimensión Producto
CREATE TABLE dim_producto (
    id_producto SERIAL PRIMARY KEY,
    nombre_producto VARCHAR(50),
    categoria VARCHAR(50),
    proveedor VARCHAR(50)
);

-- Dimensión Tiempo (fecha calendario)
CREATE TABLE dim_tiempo (
  id_tiempo  INT PRIMARY KEY,   -- formato yyyymmdd (ej: 20250811)
  fecha      DATE NOT NULL,
  anio       INT  NOT NULL,
  mes        INT  NOT NULL,
  dia        INT  NOT NULL
);

-- Tabla de Hechos de Ventas
CREATE TABLE hecho_ventas (
  id_venta     SERIAL PRIMARY KEY,  
  id_cliente   INT NOT NULL REFERENCES dim_cliente(id_cliente),
  id_producto  INT NOT NULL REFERENCES dim_producto(id_producto),
  id_tiempo    INT NOT NULL REFERENCES dim_tiempo(id_tiempo),
  cantidad     INT NOT NULL,
  total        NUMERIC(12,2) NOT NULL
);


