-- Distribución por Idioma
SELECT 
    idioma,
    COUNT(*) as cantidad,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Items), 1) as porcentaje
FROM Items
GROUP BY idioma
ORDER BY cantidad DESC;

-- Distribución Geográfica (Países)
SELECT 
    pais,
    COUNT(*) as cantidad
FROM Items
GROUP BY pais
ORDER BY cantidad DESC;

-- Distribución Temporal (Décadas)
SELECT 
    t.inicio_decada,
    TO_CHAR(t.inicio_decada, 'FM9999') || ' - ' || TO_CHAR(t.inicio_decada + 9, 'FM9999') as rango_decada,
    COUNT(*) as cantidad
FROM (
    SELECT (FLOOR((anio - 1) / 10) * 10) + 1 as inicio_decada
    FROM Items
) t
GROUP BY t.inicio_decada
ORDER BY t.inicio_decada ASC;

-- Resumen General ("La foto del sistema")
SELECT
    (SELECT COUNT(*) FROM Items) as total_items,
    (SELECT COUNT(*) FROM Generos) as total_generos,
    (SELECT COUNT(DISTINCT artista) FROM Items) as total_artistas_unicos,
    (SELECT COUNT(*) FROM ItemGeneros) as total_etiquetas_asignadas;