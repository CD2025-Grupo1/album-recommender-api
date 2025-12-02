-- ===============================
--		 CREACIÓN DE TABLAS
-- ===============================

-- Tabla de Items (Catálogo fijo de 100 álbumes - ID manual)
CREATE TABLE Items (
    item_id INTEGER PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    artista VARCHAR(255) NOT NULL,
    anio INTEGER NOT NULL,
    pais VARCHAR(100) NOT NULL,    
    idioma VARCHAR(50) NOT NULL 
);

-- Tabla de Géneros
CREATE TABLE Generos (
    genero_id SERIAL PRIMARY KEY, 
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla Intermedia Items-Generos (Muchos a Muchos)
CREATE TABLE ItemGeneros (
    item_id INTEGER,
    genero_id INTEGER,
    PRIMARY KEY (item_id, genero_id),
    FOREIGN KEY (item_id) REFERENCES Items(item_id),
    FOREIGN KEY (genero_id) REFERENCES Generos(genero_id)
);

-- Tabla de Usuarios
CREATE TABLE Usuarios (
    user_id SERIAL PRIMARY KEY,
    fecha_creacion TIMESTAMP NOT NULL
);

-- Tabla de Preferencias Explícitas (Para Cold Start)
CREATE TABLE PreferenciasUsuario (
    user_id INTEGER,
    genero_id INTEGER,
    PRIMARY KEY (user_id, genero_id),
    FOREIGN KEY (user_id) REFERENCES Usuarios(user_id),
    FOREIGN KEY (genero_id) REFERENCES Generos(genero_id)
);

-- Tabla de Compras (Transaccional - Autoincremental)
CREATE TABLE Compras (
    compra_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Usuarios(user_id),
    FOREIGN KEY (item_id) REFERENCES Items(item_id)
);


-- Tabla de Matriz de Similitud (Item-Item)
CREATE TABLE MatrizSimilitud (
    item_id_a INTEGER NOT NULL,
    item_id_b INTEGER NOT NULL,
    score FLOAT NOT NULL,
    PRIMARY KEY (item_id_a, item_id_b),
    FOREIGN KEY (item_id_a) REFERENCES Items(item_id),
    FOREIGN KEY (item_id_b) REFERENCES Items(item_id)
);

CREATE INDEX idx_similitud_a ON MatrizSimilitud(item_id_a);


-- ===============================
--		 ITEMS DISPONIBLES
-- ===============================

-- GENEROS
INSERT INTO Generos (nombre) VALUES 
('Rock'), ('Rock Progresivo'), ('Hard Rock'), ('Rock Alternativo'), -- 1 a 4 
('Heavy Metal'), ('Punk'), ('Grunge'), ('Folk Rock'), -- 5 a 8
('Glam Rock'), ('Rock en Español'), ('Rock Latino'), -- 9 a 11
('Pop'), ('Pop Latino'), ('Pop Experimental'), ('Pop Rock'), -- 12 a 15
('Hip Hop'), ('Trap'), ('R&B'), ('Soul'), -- 16 a 19
('Electrónica'), ('Trip Hop'), ('Jazz'), ('Blues'), ('Tango'), -- 20 a 24 
('Reggae'), ('Folklore'), ('Música Tradicional'), -- 25 a 27
('Folk'), ('Country'), ('Urbano Latino'); -- 28 a 30

-- ITEMS

INSERT INTO Items (item_id, titulo, artista, anio, pais, idioma) VALUES
-- ROCK, POP & VARIANTES
(1, 'The Dark Side of the Moon', 'Pink Floyd', 1973, 'Reino Unido', 'Inglés'),       -- [Rock Progresivo, Rock]
(2, 'Abbey Road', 'The Beatles', 1969, 'Reino Unido', 'Inglés'),                  -- [Rock, Pop]
(3, 'Led Zeppelin IV', 'Led Zeppelin', 1971, 'Reino Unido', 'Inglés'),            -- [Hard Rock, Rock, Blues]
(4, 'A Night at the Opera', 'Queen', 1975, 'Reino Unido', 'Inglés'),              -- [Rock, Pop, Rock Progresivo]
(5, 'Rumours', 'Fleetwood Mac', 1977, 'Reino Unido', 'Inglés'),                   -- [Rock, Pop Rock]
(6, 'Hotel California', 'Eagles', 1976, 'Estados Unidos', 'Inglés'),              -- [Rock, Folk Rock]
(7, 'Back in Black', 'AC/DC', 1980, 'Australia', 'Inglés'),                       -- [Hard Rock, Rock]
(8, 'The Wall', 'Pink Floyd', 1979, 'Reino Unido', 'Inglés'),                     -- [Rock Progresivo, Rock]
(9, 'Sgt. Pepper''s Lonely Hearts Club Band', 'The Beatles', 1967, 'Reino Unido', 'Inglés'), -- [Rock, Pop]
(10, 'Exile on Main St.', 'The Rolling Stones', 1972, 'Reino Unido', 'Inglés'),   -- [Rock, Blues, Hard Rock]
(11, 'Who''s Next', 'The Who', 1971, 'Reino Unido', 'Inglés'),                    -- [Rock, Hard Rock]
(12, 'Appetite for Destruction', 'Guns N'' Roses', 1987, 'Estados Unidos', 'Inglés'), -- [Hard Rock, Rock, Heavy Metal]
(13, 'Nevermind', 'Nirvana', 1991, 'Estados Unidos', 'Inglés'),                   -- [Grunge, Rock Alternativo, Rock]
(14, 'OK Computer', 'Radiohead', 1997, 'Reino Unido', 'Inglés'),                  -- [Rock Alternativo, Electrónica, Rock]
(15, 'The Joshua Tree', 'U2', 1987, 'Irlanda', 'Inglés'),                         -- [Rock, Pop Rock]
(16, 'Californication', 'Red Hot Chili Peppers', 1999, 'Estados Unidos', 'Inglés'), -- [Rock Alternativo, Rock, Pop Rock] 
(17, 'Paranoid', 'Black Sabbath', 1970, 'Reino Unido', 'Inglés'),                 -- [Heavy Metal, Rock]
(18, '...And Justice for All', 'Metallica', 1988, 'Estados Unidos', 'Inglés'),    -- [Heavy Metal]
(19, 'London Calling', 'The Clash', 1979, 'Reino Unido', 'Inglés'),               -- [Punk, Rock, Reggae]
(20, 'Ramones', 'Ramones', 1976, 'Estados Unidos', 'Inglés'),                     -- [Punk, Rock]
(21, 'The Queen Is Dead', 'The Smiths', 1986, 'Reino Unido', 'Inglés'),           -- [Rock Alternativo, Pop] 
(22, 'Un Verano Sin Ti', 'Bad Bunny', 2022, 'Puerto Rico', 'Español'),            -- [Urbano Latino, Pop Latino, Trap]
(23, 'Artaud', 'Pescado Rabioso', 1973, 'Argentina', 'Español'),                  -- [Rock en Español, Rock, Folk Rock]
(24, 'Clics Modernos', 'Charly García', 1983, 'Argentina', 'Español'),            -- [Rock en Español, Pop Rock, New Wave]
(25, 'El amor después del amor', 'Fito Páez', 1992, 'Argentina', 'Español'),      -- [Rock en Español, Pop Rock]
(26, 'Highway 61 Revisited', 'Bob Dylan', 1965, 'Estados Unidos', 'Inglés'),      -- [Folk Rock, Rock, Blues]
(27, 'The Rise and Fall of Ziggy Stardust', 'David Bowie', 1972, 'Reino Unido', 'Inglés'), -- [Glam Rock, Rock, Pop]
(28, 'Ten', 'Pearl Jam', 1991, 'Estados Unidos', 'Inglés'),                       -- [Grunge, Rock Alternativo, Rock]
(29, 'Cupido', 'TINI', 2023, 'Argentina', 'Español'),                             -- [Pop Latino, Pop, Urbano Latino]
(30, '(What''s the Story) Morning Glory?', 'Oasis', 1995, 'Reino Unido', 'Inglés'), -- [Rock, Pop Rock]
(31, 'Thriller', 'Michael Jackson', 1982, 'Estados Unidos', 'Inglés'),            -- [Pop, R&B, Soul]
(32, 'Purple Rain', 'Prince', 1984, 'Estados Unidos', 'Inglés'),                  -- [Pop, Rock, R&B]
(33, 'Like a Prayer', 'Madonna', 1989, 'Estados Unidos', 'Inglés'),               -- [Pop, Pop Rock]
(34, 'El día que me quieras', 'Carlos Gardel', 1935, 'Argentina', 'Español'), -- [Tango, Música Tradicional]
(35, 'Motomami', 'Rosalía', 2022, 'España', 'Español'),                           -- [Pop Experimental, Urbano Latino, Pop Latino]
(36, '21', 'Adele', 2011, 'Reino Unido', 'Inglés'),                               -- [Pop, Soul, R&B]
(37, '1989', 'Taylor Swift', 2014, 'Estados Unidos', 'Inglés'),                   -- [Pop]
(38, 'The Fame', 'Lady Gaga', 2008, 'Estados Unidos', 'Inglés'),                  -- [Pop, Electrónica]
(39, 'Gold: Greatest Hits', 'ABBA', 1992, 'Suecia', 'Inglés'),                    -- [Pop] 
(40, 'Faith', 'George Michael', 1987, 'Reino Unido', 'Inglés'),                   -- [Pop, R&B, Soul]
(41, 'Future Nostalgia', 'Dua Lipa', 2020, 'Reino Unido', 'Inglés'),              -- [Pop, Electrónica] 
(42, 'Harry''s House', 'Harry Styles', 2022, 'Reino Unido', 'Inglés'),            -- [Pop, Pop Rock, Funk]
(43, '24K Magic', 'Bruno Mars', 2016, 'Estados Unidos', 'Inglés'),                -- [Pop, R&B, Funk]
(44, 'Lemonade', 'Beyoncé', 2016, 'Estados Unidos', 'Inglés'),                    -- [Pop, R&B, Hip Hop]
(45, 'Oktubre', 'Patricio Rey', 1986, 'Argentina', 'Español'),                    -- [Rock en Español, Rock, Post-Punk]
(46, 'Goodbye Yellow Brick Road', 'Elton John', 1973, 'Reino Unido', 'Inglés'),    -- [Pop, Rock, Glam Rock]
(47, 'The Stranger', 'Billy Joel', 1977, 'Estados Unidos', 'Inglés'),             -- [Pop, Rock, Soft Rock]
(48, 'Jagged Little Pill', 'Alanis Morissette', 1995, 'Canadá', 'Inglés'),        -- [Pop Rock, Rock Alternativo]
(49, 'Desde el Fin del Mundo', 'Duki', 2021, 'Argentina', 'Español'),             -- [Trap, Urbano Latino, Hip Hop]
(50, 'Anti', 'Rihanna', 2016, 'Barbados', 'Inglés'),                              -- [Pop, R&B, Hip Hop]

-- HIP HOP / RAP
(51, 'The Marshall Mathers LP', 'Eminem', 2000, 'Estados Unidos', 'Inglés'),      -- [Hip Hop, Rap]
(52, 'Ready to Die', 'The Notorious B.I.G.', 1994, 'Estados Unidos', 'Inglés'),   -- [Hip Hop, Rap]
(53, 'The Chronic', 'Dr. Dre', 1992, 'Estados Unidos', 'Inglés'),                 -- [Hip Hop, Rap]
(54, 'Illmatic', 'Nas', 1994, 'Estados Unidos', 'Inglés'),                        -- [Hip Hop, Rap]
(55, 'To Pimp a Butterfly', 'Kendrick Lamar', 2015, 'Estados Unidos', 'Inglés'),  -- [Hip Hop, Jazz Rap, Funk]
(56, 'My Beautiful Dark Twisted Fantasy', 'Kanye West', 2010, 'Estados Unidos', 'Inglés'), -- [Hip Hop, Rap, Pop]
(57, 'The Miseducation of Lauryn Hill', 'Lauryn Hill', 1998, 'Estados Unidos', 'Inglés'), -- [Hip Hop, R&B, Soul]
(58, 'All Eyez on Me', '2Pac', 1996, 'Estados Unidos', 'Inglés'),                 -- [Hip Hop, Rap]
(59, 'Enter the Wu-Tang (36 Chambers)', 'Wu-Tang Clan', 1993, 'Estados Unidos', 'Inglés'), -- [Hip Hop, Rap]
(60, 'El Payador Perseguido', 'Atahualpa Yupanqui', 1972, 'Argentina', 'Español'), -- [Folklore, Música Tradicional]
(61, 'The Blueprint', 'Jay-Z', 2001, 'Estados Unidos', 'Inglés'),                 -- [Hip Hop, Rap]
(62, 'Stankonia', 'OutKast', 2000, 'Estados Unidos', 'Inglés'),                   -- [Hip Hop, Funk, Pop]
(63, 'The Low End Theory', 'A Tribe Called Quest', 1991, 'Estados Unidos', 'Inglés'), -- [Hip Hop, Jazz Rap]
(64, 'Paul''s Boutique', 'Beastie Boys', 1989, 'Estados Unidos', 'Inglés'),       -- [Hip Hop, Rock]
(65, 'Straight Outta Compton', 'N.W.A', 1988, 'Estados Unidos', 'Inglés'),        -- [Hip Hop, Rap]

-- ELECTRÓNICA
(66, 'Random Access Memories', 'Daft Punk', 2013, 'Francia', 'Inglés'),           -- [Electrónica, Pop, Disco]
(67, 'Jolene', 'Dolly Parton', 1974, 'Estados Unidos', 'Inglés'), -- [Country, Folk, Pop]
(68, 'Violator', 'Depeche Mode', 1990, 'Reino Unido', 'Inglés'),                  -- [Electrónica, Pop Rock, Synth-pop]
(69, 'Trans-Europe Express', 'Kraftwerk', 1977, 'Alemania', 'Alemán'),            -- [Electrónica, Experimental]
(70, 'Mezzanine', 'Massive Attack', 1998, 'Reino Unido', 'Inglés'),               -- [Trip Hop, Electrónica]
(71, 'Alta Suciedad', 'Andrés Calamaro', 1997, 'Argentina', 'Español'),           -- [Rock en Español, Rock, Pop Rock]
(72, 'Dummy', 'Portishead', 1994, 'Reino Unido', 'Inglés'),                       -- [Trip Hop, Electrónica]
(73, 'Acariciando lo áspero', 'Divididos', 1991, 'Argentina', 'Español'),         -- [Rock en Español, Hard Rock]
(74, 'Selected Ambient Works 85-92', 'Aphex Twin', 1992, 'Reino Unido', 'Inglés'), -- [Electrónica, Ambient]
(75, 'Calambre', 'Nathy Peluso', 2020, 'Argentina', 'Español'),                   -- [Pop Latino, Hip Hop, Soul]

-- R&B / SOUL / JAZZ
(76, 'What''s Going On', 'Marvin Gaye', 1971, 'Estados Unidos', 'Inglés'),        -- [Soul, R&B]
(77, 'Songs in the Key of Life', 'Stevie Wonder', 1976, 'Estados Unidos', 'Inglés'), -- [Soul, R&B, Pop]
(78, 'Back to Black', 'Amy Winehouse', 2006, 'Reino Unido', 'Inglés'),            -- [Soul, R&B, Jazz]
(79, 'Blonde', 'Frank Ocean', 2016, 'Estados Unidos', 'Inglés'),                  -- [R&B, Pop Experimental, Soul]
(80, 'Libertango', 'Astor Piazzolla', 1974, 'Argentina', 'Instrumental'),         -- [Tango, Jazz]
(81, 'I Never Loved a Man the Way I Love You', 'Aretha Franklin', 1967, 'Estados Unidos', 'Inglés'), -- [Soul, R&B]
(82, 'At Last!', 'Etta James', 1960, 'Estados Unidos', 'Inglés'),                 -- [Soul, Blues, Jazz]
(83, 'Piano Bar', 'Charly García', 1984, 'Argentina', 'Español'),                 -- [Rock en Español, Rock]
(84, 'Off the Wall', 'Michael Jackson', 1979, 'Estados Unidos', 'Inglés'),        -- [R&B, Pop, Disco]
(85, 'Pies Descalzos', 'Shakira', 1995, 'Colombia', 'Español'),                   -- [Pop Latino, Pop Rock, Rock Latino]

-- JAZZ / BLUES
(86, 'Kind of Blue', 'Miles Davis', 1959, 'Estados Unidos', 'Instrumental'),      -- [Jazz, Blues]
(87, 'A Love Supreme', 'John Coltrane', 1965, 'Estados Unidos', 'Instrumental'),  -- [Jazz]
(88, 'Time Out', 'The Dave Brubeck Quartet', 1959, 'Estados Unidos', 'Instrumental'), -- [Jazz]
(89, 'Live at the Regal', 'B.B. King', 1965, 'Estados Unidos', 'Inglés'),         -- [Blues]
(90, 'Head Hunters', 'Herbie Hancock', 1973, 'Estados Unidos', 'Instrumental'),   -- [Jazz, Funk, Fusion]

-- OTROS
(91, 'Exodus', 'Bob Marley & The Wailers', 1977, 'Jamaica', 'Inglés'),            -- [Reggae]
(92, 'Legend', 'Bob Marley & The Wailers', 1984, 'Jamaica', 'Inglés'),            -- [Reggae]
(93, 'Cantora 1', 'Mercedes Sosa', 2009, 'Argentina', 'Español'),                 -- [Folklore, Música Tradicional]
(94, 'Canción Animal', 'Soda Stereo', 1990, 'Argentina', 'Español'),              -- [Rock, Rock en Español, Rock Alternativo]
(95, 'Bocanada', 'Gustavo Cerati', 1999, 'Argentina', 'Español'),                 -- [Rock en Español, Electrónica, Rock Alternativo]
(96, 'Abraxas', 'Santana', 1970, 'México', 'Inglés'),                             -- [Rock Latino, Rock, Blues]
(97, 'Buena Vista Social Club', 'Buena Vista Social Club', 1997, 'Cuba', 'Español'), -- [Música Tradicional, Jazz]
(98, 'Blue', 'Joni Mitchell', 1971, 'Canadá', 'Inglés'),                          -- [Folk, Pop]
(99, 'At Folsom Prison', 'Johnny Cash', 1968, 'Estados Unidos', 'Inglés'),        -- [Country, Folk, Blues]
(100, 'Bridge Over Troubled Water', 'Simon & Garfunkel', 1970, 'Estados Unidos', 'Inglés'); -- [Folk, Pop Rock]


-- 		ASIGNACIÓN DE GÉNEROS


-- CATEGORÍA: ROCK (General)
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Rock') FROM Items 
WHERE item_id IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,19,20,23,26,27,28,30,32,45,46,47,64,71,83,94,96);

-- CATEGORÍA: ROCK PROGRESIVO
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Rock Progresivo') FROM Items 
WHERE item_id IN (1, 4, 8);

-- CATEGORÍA: HARD ROCK
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Hard Rock') FROM Items 
WHERE item_id IN (3, 7, 10, 11, 12, 73);

-- CATEGORÍA: ROCK ALTERNATIVO
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Rock Alternativo') FROM Items 
WHERE item_id IN (13, 14, 16, 21, 28, 48, 94, 95);

-- CATEGORÍA: PUNK
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Punk') FROM Items 
WHERE item_id IN (19, 20);

-- CATEGORÍA: HEAVY METAL
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Heavy Metal') FROM Items 
WHERE item_id IN (12, 17, 18);

-- CATEGORÍA: GRUNGE
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Grunge') FROM Items 
WHERE item_id IN (13, 28);

-- CATEGORÍA: BRITPOP - SIN ÁLBUMES (BORRAR DESPUÉS)

-- CATEGORÍA: GLAM ROCK
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Glam Rock') FROM Items 
WHERE item_id IN (27, 46);

-- CATEGORÍA: ROCK EN ESPAÑOL
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Rock en Español') FROM Items 
WHERE item_id IN (23, 24, 25, 45, 71, 73, 83, 94, 95);

-- CATEGORÍA: ROCK LATINO
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Rock Latino') FROM Items 
WHERE item_id IN (85, 96);

-- CATEGORÍA: POP (General)
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Pop') FROM Items 
WHERE item_id IN (2, 4, 9, 27, 29, 31, 32, 33, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 50, 56, 62, 66, 67, 77, 84, 98);

-- CATEGORÍA: POP ROCK
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Pop Rock') FROM Items 
WHERE item_id IN (5, 15, 16, 24, 25, 30, 33, 42, 48, 68, 71, 85, 100);

-- CATEGORÍA: POP LATINO
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Pop Latino') FROM Items 
WHERE item_id IN (22, 29, 35, 75, 85);

-- CATEGORÍA: POP EXPERIMENTAL
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Pop Experimental') FROM Items 
WHERE item_id IN (35, 79);

-- CATEGORÍA: HIP HOP / RAP
INSERT INTO ItemGeneros (item_id, genero_id) 
SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Hip Hop') 
FROM Items 
WHERE (item_id BETWEEN 51 AND 65 AND item_id <> 60) 
   OR item_id IN (44, 49, 50, 75);

-- CATEGORÍA: TRAP
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Trap') FROM Items 
WHERE item_id IN (22, 49);

-- CATEGORÍA: URBANO LATINO
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Urbano Latino') FROM Items 
WHERE item_id IN (22, 29, 35, 49);

-- CATEGORÍA: R&B
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='R&B') FROM Items 
WHERE item_id IN (31, 32, 36, 40, 43, 44, 50, 57, 76, 77, 78, 79, 81, 84);

-- CATEGORÍA: SOUL
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Soul') FROM Items 
WHERE item_id IN (31, 36, 40, 57, 75, 76, 77, 78, 79, 81, 82);

-- CATEGORÍA: ELECTRÓNICA
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Electrónica') FROM Items 
WHERE item_id IN (14, 38, 41, 66, 68, 69, 70, 72, 74, 95);

-- CATEGORÍA: TRIP HOP
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Trip Hop') FROM Items 
WHERE item_id IN (70, 72);

-- CATEGORÍA: JAZZ
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Jazz') FROM Items 
WHERE item_id IN (78, 80, 82, 86, 87, 88, 90, 97);

-- CATEGORÍA: BLUES
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Blues') FROM Items 
WHERE item_id IN (3, 10, 26, 82, 86, 89, 96, 99);

-- CATEGORÍA: REGGAE
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Reggae') FROM Items 
WHERE item_id IN (19, 91, 92);

-- CATEGORÍA: FOLK / FOLK ROCK
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Folk Rock') FROM Items 
WHERE item_id IN (6, 23, 26, 67);
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Folk') FROM Items 
WHERE item_id IN (98, 99, 100);

-- CATEGORÍA: COUNTRY
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Country') FROM Items 
WHERE item_id IN (67, 99);

-- CATEGORÍA: TANGO / MÚSICA TRADICIONAL / FOLKLORE
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Tango') FROM Items 
WHERE item_id IN (34, 80);
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Folklore') FROM Items 
WHERE item_id IN (34, 60, 93);
INSERT INTO ItemGeneros (item_id, genero_id) SELECT item_id, (SELECT genero_id FROM Generos WHERE nombre='Música Tradicional') FROM Items 
WHERE item_id IN (60, 93, 97);

-- =================================================================================
-- 			 			POBLACIÓN DE USUARIOS (TOTAL: 15)
-- =================================================================================
-- IDs 1-5: Usuarios base (para simular el ecosistema y compras históricas).
-- IDs 6-15: Usuarios de prueba "Cold Start" (sin historial de compras, solo preferencias).

INSERT INTO Usuarios (user_id, fecha_creacion) VALUES 
-- Usuarios Base (Generadores de datos de entrenamiento)
(1, NOW() - INTERVAL '1 year'),   -- Veterano (Rockero)
(2, NOW() - INTERVAL '6 months'), -- Medio (Pop)
(3, NOW() - INTERVAL '3 months'), -- Reciente (Hip Hop)
(4, NOW()),                       -- Nuevo (Relleno)
(5, NOW()),                       -- Nuevo (Relleno)
-- Usuarios de Test (Casos de prueba para el Recomendador)
(6, NOW()), (7, NOW()), (8, NOW()), (9, NOW()), (10, NOW()),
(11, NOW()), (12, NOW()), (13, NOW()), (14, NOW()), (15, NOW());
-- Casos extremos para estresar sistema:
INSERT INTO Usuarios (user_id, fecha_creacion) VALUES 
(16, NOW()), -- Caso Error: Usuario sin preferencias
(17, NOW()); -- Caso Sobrecarga: Usuario con "demasiados" gustos

-- =================================================================================
-- 2. PREFERENCIAS EXPLÍCITAS (PERFILES DE GUSTO)
-- =================================================================================
-- Definimos qué le gusta a cada usuario. Esto es el INPUT principal del Cold Start.

-- --- PERFILES BASE (Usuarios 1-3) ---
INSERT INTO PreferenciasUsuario (user_id, genero_id)
SELECT 1, genero_id FROM Generos WHERE nombre IN ('Rock', 'Hard Rock', 'Rock Progresivo');

INSERT INTO PreferenciasUsuario (user_id, genero_id)
SELECT 2, genero_id FROM Generos WHERE nombre IN ('Pop', 'Pop Latino', 'Urbano Latino');

INSERT INTO PreferenciasUsuario (user_id, genero_id)
SELECT 3, genero_id FROM Generos WHERE nombre IN ('Hip Hop', 'Trap', 'R&B');

-- --- PERFILES DE TEST (Usuarios 6-15) ---

-- TEST 1: NICHOS LOCALES (Tango, Folklore y Rock en Español)
INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES (6, 24), (6, 26), (6, 10);

-- TEST 2: VOLUMEN ALTO (Pop Mainstream)
INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES (7, 12), (7, 13), (7, 30);

-- TEST 3: GÉNEROS DENSOS (Rock Clásico)
-- Objetivo: Verificar selección dentro de categorías con muchos ítems.
INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES (8, 1), (8, 3), (8, 23);

-- TEST 4: NICHOS INTERNACIONALES (Country / Folk)
-- Objetivo extra: verificar correcto funcionamiento con solo dos géneros 
INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES (9, 29), (9, 28);

-- TEST 5: HIP HOP
-- Objetivo: Revisar que no aparezca atahualpa yupanqui (id=60, en el medio del hip hop)
INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES (10, 16), (10, 17), (10, 18);

-- OTROS PERFILES VARIADOS (Electrónica, Jazz, Metal, Latino, Indie)
INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES 
(11, 20), (11, 21), (11, 14), -- Electrónica
(12, 22), (12, 19), (12, 23), -- Jazz/Soul
(13, 5), (13, 6), (13, 7),    -- Heavy/Punk
(14, 11), (14, 13), (14, 25), -- Mix Latino
(15, 4), (15, 8), (15, 21);   -- Indie/Alt

-- CASO 17 PARA ESTRESAR SISTEMA (demasiados géneros)
INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES 
(17, 1),  -- Rock
(17, 12), -- Pop
(17, 22), -- Jazz
(17, 24), -- Tango
(17, 20), -- Electrónica
(17, 25), -- Reggae
(17, 16); -- Hip Hop


-- =================================================================================
-- 3. GENERACIÓN DE ECOSISTEMA (HISTORIAL DE VENTAS)
-- =================================================================================
-- Sin estas transacciones, el algoritmo de "Más Vendidos por Género" no funciona.
-- Usamos a los usuarios 1-5 para "comprar" ítems y generar estadísticas.

-- A) HISTORIAL PERSONAL (Lo que compraron orgánicamente los usuarios 1-3)
INSERT INTO Compras (user_id, item_id, timestamp) VALUES
-- Usuario 1 (Rock)
(1, 1, NOW() - INTERVAL '5 months'),  -- Pink Floyd
(1, 3, NOW() - INTERVAL '4 months'),  -- Led Zeppelin
(1, 7, NOW() - INTERVAL '3 months'),  -- AC/DC
(1, 13, NOW() - INTERVAL '1 month'),  -- Nirvana
-- Usuario 2 (Pop)
(2, 37, NOW() - INTERVAL '5 months'), -- Taylor Swift
(2, 41, NOW() - INTERVAL '2 months'), -- Dua Lipa
(2, 35, NOW() - INTERVAL '1 month'),  -- Rosalía
(2, 29, NOW() - INTERVAL '1 week'),   -- TINI
-- Usuario 3 (Hip Hop)
(3, 51, NOW() - INTERVAL '3 months'), -- Eminem
(3, 55, NOW() - INTERVAL '2 months'), -- Kendrick Lamar
(3, 61, NOW() - INTERVAL '1 month'),  -- Jay-Z
(3, 22, NOW() - INTERVAL '2 days');   -- Bad Bunny

-- B) ACTIVACIÓN DE NICHOS (CRÍTICO PARA COLD START)
-- Generamos ventas manuales en géneros pequeños para que el algoritmo los priorice.

-- TANGO (Gardel > Piazzolla)
INSERT INTO Compras (user_id, item_id, timestamp) VALUES
(1, 34, NOW()), (2, 34, NOW()), (5, 34, NOW()), -- Gardel (3 ventas)
(3, 80, NOW()); -- Piazzolla (1 venta)

-- FOLKLORE (Mercedes Sosa > Atahualpa)
INSERT INTO Compras (user_id, item_id, timestamp) VALUES
(4, 93, NOW()), (5, 93, NOW()), (2, 93, NOW()), -- Mercedes Sosa (3 ventas)
(1, 60, NOW()), (3, 60, NOW()); -- Atahualpa (2 ventas)

-- COUNTRY (Dolly Parton > Johnny Cash)
INSERT INTO Compras (user_id, item_id, timestamp) VALUES
(2, 67, NOW()), (4, 67, NOW()), (5, 67, NOW()), -- Dolly Parton (3 ventas)
(1, 99, NOW()), (3, 99, NOW()); -- Johnny Cash (2 ventas)

-- C) BEST SELLERS GLOBALES (FALLBACKS)
-- Aseguramos que ciertos discos tengan MUCHAS ventas para rellenar listas vacías.
INSERT INTO Compras (user_id, item_id, timestamp) VALUES
-- Taylor Swift (1989) - ID 37
(1, 37, NOW()), (2, 37, NOW()), (3, 37, NOW()), (4, 37, NOW()), (5, 37, NOW()),
-- Pink Floyd (Dark Side) - ID 1
(1, 1, NOW()), (2, 1, NOW()), (3, 1, NOW()), (5, 1, NOW()),
-- Bad Bunny (Un Verano Sin Ti) - ID 22
(2, 22, NOW()), (3, 22, NOW()), (4, 22, NOW()), (5, 22, NOW()),
-- Queen (A Night at the Opera) - ID 4
(1, 4, NOW()), (3, 4, NOW()), (5, 4, NOW());

-- D) VENTAS DE RELLENO (VARIEDAD)
-- Damos algo de volumen a otros géneros para evitar ceros.
INSERT INTO Compras (user_id, item_id, timestamp) VALUES
(1, 13, NOW()), (2, 13, NOW()), (4, 13, NOW()), -- Nirvana
(3, 7, NOW()), (5, 7, NOW()), -- AC/DC
(2, 30, NOW()), (4, 30, NOW()), -- Oasis
(1, 29, NOW()), (3, 29, NOW()), -- TINI
(2, 35, NOW()), (5, 35, NOW()), -- Rosalía
(3, 49, NOW()), -- Duki
(3, 51, NOW()), (4, 51, NOW()), -- Eminem
(1, 58, NOW()), -- 2Pac
(5, 61, NOW()), -- Jay-Z
(1, 86, NOW()), (2, 86, NOW()), -- Miles Davis
(4, 89, NOW()), -- BB King
(2, 66, NOW()), (3, 66, NOW()), -- Daft Punk
(5, 74, NOW()); -- Aphex Twin