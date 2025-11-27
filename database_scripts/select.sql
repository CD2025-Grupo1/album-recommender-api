-- Este archivo contiene algunos listados y SELECTs útiles para la base de datos.

-- ========================
--   LISTADOS GENERALES
-- ========================

-- Listado álbumes (géneros concatenados)
SELECT 
    i.item_id,
    i.titulo, 
    i.artista, 
    STRING_AGG(g.nombre, ', ') AS generos,
	i.pais,
	i.idioma
FROM Items i
JOIN ItemGeneros ig ON i.item_id = ig.item_id
JOIN Generos g ON ig.genero_id = g.genero_id
GROUP BY i.item_id, i.titulo, i.artista
ORDER BY i.item_id;

-- Ver géneros de un álbum por título
SELECT i.titulo, g.nombre 
FROM Items i
JOIN ItemGeneros ig ON i.item_id = ig.item_id
JOIN Generos g ON ig.genero_id = g.genero_id
WHERE i.titulo = 'Thriller';

-- Álbumes por género
SELECT g.nombre, COUNT(ig.item_id) as cantidad_albumes
FROM Generos g
JOIN ItemGeneros ig ON g.genero_id = ig.genero_id
GROUP BY g.nombre
ORDER BY cantidad_albumes DESC;

-- Chequeo cantidad de todo
SELECT 
    (SELECT COUNT(*) FROM Items) AS total_items, -- Debe dar 100
    (SELECT COUNT(*) FROM Generos) AS total_generos, -- Debe dar aprox 31
    (SELECT COUNT(*) FROM ItemGeneros) AS total_relaciones; -- Debe dar más de 100 (aprox 200-250)

SELECT * FROM generos


-- PARA USUARIOS Y PREFERENCIAS

SELECT 
    u.user_id, 
    u.fecha_creacion::date, 
    'Preferencia Explícita' as tipo,
    g.nombre as detalle
FROM Usuarios u
JOIN PreferenciasUsuario pu ON u.user_id = pu.user_id
JOIN Generos g ON pu.genero_id = g.genero_id
-- WHERE u.user_id IN (6, 9, 17) -- Descomentar para filtrar usuarios especificos

UNION ALL

SELECT 
    u.user_id, 
    u.fecha_creacion::date,
    'Compra Realizada' as tipo,
    i.titulo || ' (' || i.artista || ')' as detalle
FROM Usuarios u
JOIN Compras c ON u.user_id = c.user_id
JOIN Items i ON c.item_id = i.item_id

ORDER BY user_id, tipo DESC; -- Tipo DESC pone 'Preferencia' antes que 'Compra' usualmente


-- Ranking de Ventas por Género (Simula la lógica del Cold Start)
-- Muestra qué álbum gana en cada categoría
SELECT 
    g.nombre as genero,
    i.titulo,
    COUNT(c.compra_id) as ventas_totales
FROM Generos g
JOIN ItemGeneros ig ON g.genero_id = ig.genero_id
JOIN Items i ON ig.item_id = i.item_id
LEFT JOIN Compras c ON i.item_id = c.item_id
GROUP BY g.nombre, i.titulo
ORDER BY g.nombre ASC, ventas_totales DESC;

-- Top Sellers Globales (El Fallback del sistema)
SELECT 
    i.titulo, 
    i.artista, 
    COUNT(c.compra_id) as ventas
FROM Items i
JOIN Compras c ON i.item_id = c.item_id
GROUP BY i.titulo, i.artista
ORDER BY ventas DESC
LIMIT 10;

-- Pares de álbumes comprados juntos (Base del Item-Item)
SELECT 
    i1.titulo AS album_A,
    i2.titulo AS album_B,
    COUNT(*) AS veces_comprados_juntos
FROM Compras c1
JOIN Compras c2 ON c1.user_id = c2.user_id AND c1.item_id < c2.item_id
JOIN Items i1 ON c1.item_id = i1.item_id
JOIN Items i2 ON c2.item_id = i2.item_id
GROUP BY album_A, album_B
ORDER BY veces_comprados_juntos DESC
LIMIT 10;


-- ========================
-- 	  Integridad de Datos
-- ========================


-- Buscar géneros HUÉRFANOS (sin ítems asociados)
SELECT g.genero_id, g.nombre 
FROM Generos g
LEFT JOIN ItemGeneros ig ON g.genero_id = ig.genero_id
WHERE ig.item_id IS NULL;

-- Ver géneros con menos de 2 álbumes (provocan fallback)
SELECT 
    g.genero_id,
    g.nombre, 
    COUNT(ig.item_id) as total_albums
FROM Generos g
LEFT JOIN ItemGeneros ig ON g.genero_id = ig.genero_id
GROUP BY g.genero_id, g.nombre
HAVING COUNT(ig.item_id) < 2
ORDER BY total_albums ASC;
