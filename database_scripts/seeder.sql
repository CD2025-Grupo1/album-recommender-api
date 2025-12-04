-- =================================================================================
-- SEEDER DE POBLACIÓN MASIVA
-- =================================================================================
-- Este script genera 200 usuarios siguiendo 5 arquetipos de comportamiento.
-- Se ejecuta dentro de una transacción anónima (DO BLOCK) para PostgreSQL.

DO $$
DECLARE
    -- Contadores y variables de control
    i INT;
    t INT;
    new_user_id INT;
    num_transactions INT;
    target_item INT;
    rand_prob FLOAT;
    days_ago INT;
    
    -- Definición de Arquetipos (Arrays de IDs de Géneros)
    -- Rockero: Rock(1), Progresivo(2), Hard(3), Alt(4), Metal(5), Punk(6), Grunge(7), FolkRock(8), Glam(9), Esp(10)
    genres_rock INT[] := ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; 
    
    -- Pop: Pop(12), Latino(13), Exp(14), PopRock(15), Urbano(30), R&B(18)
    genres_pop INT[] := ARRAY[12, 13, 14, 15, 30, 18];
    
    -- Urbano: HipHop(16), Trap(17), R&B(18), Soul(19), Urbano(30)
    genres_urbano INT[] := ARRAY[16, 17, 18, 19, 30];
    
    -- Nicho: Elec(20), Trip(21), Jazz(22), Blues(23), Tango(24), Reggae(25), Folk(26,27,28), Country(29)
    genres_nicho INT[] := ARRAY[20, 21, 22, 23, 24, 25, 26, 27, 28, 29];
    
    -- Variables temporales para asignación
    target_genres INT[];
    probability_threshold FLOAT;
    
BEGIN

PERFORM setval(pg_get_serial_sequence('Usuarios', 'user_id'), (SELECT MAX(user_id) FROM Usuarios));

    -- Vamos a generar 200 usuarios en total
    -- Distribución: 
    -- 1. Rockeros (30% -> 60 usuarios)
    -- 2. Pop (25% -> 50 usuarios)
    -- 3. Urbano (20% -> 40 usuarios)
    -- 4. Nicho (15% -> 30 usuarios)
    -- 5. Explorador (10% -> 20 usuarios)

    FOR i IN 1..200 LOOP
        
        -- Determinar Arquetipo según el índice del bucle
        IF i <= 60 THEN
            target_genres := genres_rock;
            probability_threshold := 0.80; -- 80% fidelidad
        ELSIF i <= 110 THEN
            target_genres := genres_pop;
            probability_threshold := 0.70; -- 70% fidelidad
        ELSIF i <= 150 THEN
            target_genres := genres_urbano;
            probability_threshold := 0.80; -- 80% fidelidad
        ELSIF i <= 180 THEN
            target_genres := genres_nicho;
            probability_threshold := 0.90; -- 90% fidelidad
        ELSE
            -- Explorador: Sin géneros fijos, comportamiento aleatorio
            target_genres := NULL; 
            probability_threshold := 0.00; -- 0% fidelidad 
        END IF;

        -- Crear Usuario
        INSERT INTO Usuarios (fecha_creacion) 
        VALUES (NOW() - (floor(random() * 365) || ' days')::interval)
        RETURNING user_id INTO new_user_id;

        -- Insertar Preferencias Explícitas (3 géneros al azar del arquetipo)
        -- Si es explorador (target_genres es NULL), elegimos 3 de cualquier lado.
        IF target_genres IS NOT NULL THEN
            INSERT INTO PreferenciasUsuario (user_id, genero_id)
            SELECT new_user_id, g_id
            FROM unnest(target_genres) as g_id
            ORDER BY random()
            LIMIT 3;
        ELSE
            INSERT INTO PreferenciasUsuario (user_id, genero_id)
            SELECT new_user_id, genero_id
            FROM Generos
            ORDER BY random()
            LIMIT 3;
        END IF;

        -- Generar Historial de Compras
        -- Entre 10 y 40 compras por usuario
        num_transactions := floor(random() * 31 + 10)::int;

        FOR t IN 1..num_transactions LOOP
            rand_prob := random();
            
            -- Selección del Ítem
            IF target_genres IS NOT NULL AND rand_prob < probability_threshold THEN
                -- Elegir un ítem que pertenezca a sus géneros objetivo
                SELECT item_id INTO target_item
                FROM ItemGeneros
                WHERE genero_id = ANY(target_genres)
                ORDER BY random()
                LIMIT 1;
            ELSE
                -- Elegir cualquier ítem del catálogo
                SELECT item_id INTO target_item
                FROM Items
                ORDER BY random()
                LIMIT 1;
            END IF;

            -- Fecha aleatoria en el último año
            days_ago := floor(random() * 365)::int;

            -- Evitar duplicados exactos (mismo item comprado por el usuario)
            -- (Opcional: si tu sistema permite recompras, puedes quitar el IF NOT EXISTS)
            IF NOT EXISTS (SELECT 1 FROM Compras WHERE user_id = new_user_id AND item_id = target_item) THEN
                INSERT INTO Compras (user_id, item_id, timestamp)
                VALUES (
                    new_user_id, 
                    target_item, 
                    NOW() - (days_ago || ' days')::interval
                );
            END IF;
            
        END LOOP; -- Fin bucle transacciones

    END LOOP; -- Fin bucle usuarios

    RAISE NOTICE 'Se han generado exitosamente 200 usuarios sintéticos con sus respectivas transacciones.';
END $$;