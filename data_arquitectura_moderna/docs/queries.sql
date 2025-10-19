-- Total ventas por mes y categoria
SELECT d.anio, d.mes, p.categoria, SUM(f.total) AS total_ventas
FROM hecho_ventas f
JOIN dim_tiempo d ON f.id_tiempo = d.id_tiempo
JOIN dim_producto p ON f.id_producto = p.id_producto
GROUP BY d.anio, d.mes, p.categoria
ORDER BY d.anio, d.mes, p.categoria;

-- Top clientes por total ventas
SELECT c.nombre_cliente, c.ubicacion, SUM(f.total) AS total_ventas
FROM hecho_ventas f
JOIN dim_cliente c ON f.id_cliente = c.id_cliente
GROUP BY c.nombre_cliente, c.ubicacion
ORDER BY total_ventas DESC
LIMIT 10;

-- Año acumulativo por mes 
SELECT
  d.anio, d.mes,
  SUM(f.total) AS ventas_mes,
  SUM(SUM(f.total)) OVER (PARTITION BY d.anio ORDER BY d.mes) AS ventas_ytd
FROM hecho_ventas f
JOIN dim_tiempo d ON f.id_tiempo = d.id_tiempo
GROUP BY d.anio, d.mes
ORDER BY d.anio, d.mes;
