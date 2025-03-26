-- Seed Games Table
INSERT INTO games (title, platform, genre, release_date) VALUES
('Super Mario 64', 'Nintendo 64', 'Platformer', '1996-06-23'),
('The Legend of Zelda: Ocarina of Time', 'Nintendo 64', 'Action-Adventure', '1998-11-21'),
('Hollow Knight', 'PC', 'Metroidvania', '2017-02-24'),
('Celeste', 'PC', 'Platformer', '2018-01-25'),
('Dark Souls', 'PC', 'Action RPG', '2011-09-22'),
('Elden Ring', 'PC', 'Action RPG', '2022-02-25'),
('Hades', 'PC', 'Roguelike', '2020-09-17'),
('Metroid Dread', 'Nintendo Switch', 'Metroidvania', '2021-10-08'),
('Minecraft', 'PC', 'Sandbox', '2011-11-18'),
('Portal', 'PC', 'Puzzle', '2007-10-09');

-- Seed Categories Table
INSERT INTO categories (game_id, name, description, world_record_time, world_record_holder) VALUES
(1, '16 Stars', 'Complete the game by collecting 16 stars', 900.54, 'Cheese'),
(1, '70 Stars', 'Complete the game by collecting 70 stars', 2792.65, 'Simply'),
(1, '120 Stars', 'Complete the game by collecting all 120 stars', 6235.22, 'Liam'),
(2, 'Any%', 'Complete the game as fast as possible', 1041.12, 'Torje'),
(2, '100%', 'Complete the game with 100% completion', 13825.45, 'ZFG'),
(3, 'Any%', 'Complete the game as fast as possible', 1980.33, 'Pestilent'),
(3, '112%', 'Complete the game with full completion', 10825.74, 'Vysuals'),
(4, 'Any%', 'Complete the game as fast as possible', 1645.87, 'TGH'),
(4, 'All Chapters', 'Complete all chapters including B-sides', 5328.92, 'Buhbai'),
(5, 'Any%', 'Complete the game as fast as possible', 3190.21, 'Catalystz'),
(5, 'All Bosses', 'Defeat all bosses in the game', 6785.43, 'Elajjaz'),
(6, 'Any%', 'Complete the game as fast as possible', 4860.57, 'Distortion2'),
(6, 'All Remembrances', 'Collect all remembrances in the game', 10980.35, 'Seki'),
(7, 'Fresh File', 'Complete the game from a new save file', 1200.98, 'Vorime'),
(8, 'Any%', 'Complete the game as fast as possible', 4320.75, 'Oatsngoats'),
(9, 'Any%', 'Complete the game by killing the Ender Dragon', 1520.64, 'Couriway'),
(9, 'All Achievements', 'Earn all achievements in the game', 15430.22, 'TheeSizzler'),
(10, 'Any%', 'Complete the game as fast as possible', 480.89, 'Msushi');

-- Seed Runs Table
INSERT INTO runs (game_id, category_id, date, completion_time, is_personal_best, notes) VALUES
-- Super Mario 64 runs
(1, 1, '2023-01-15', 1350.66, 0, 'First attempt at 16 stars, lost time on Bowser throws'),
(1, 1, '2023-01-20', 1290.33, 1, 'Better run but made mistakes in BitDW'),
(1, 2, '2023-02-05', 3600.45, 1, 'My first 70 star run, happy with the result'),

-- Ocarina of Time runs
(2, 4, '2023-02-12', 2250.77, 1, 'Still learning the wrong warps, but decent run'),
(2, 4, '2023-02-18', 2310.22, 0, 'Failed WESS in Shadow Temple'),

-- Hollow Knight runs
(3, 6, '2023-03-10', 3150.88, 1, 'First serious any% attempt'),
(3, 6, '2023-03-15', 3350.45, 0, 'Got lost in Deepnest'),
(3, 7, '2023-04-02', 12500.36, 1, 'First 112% completion run, very exhausting'),

-- Celeste runs
(4, 8, '2023-04-15', 2250.55, 0, 'Decent run but died a lot on chapter 3'),
(4, 8, '2023-04-22', 2150.32, 1, 'New PB! Clean run with only a few deaths'),

-- Dark Souls runs
(5, 10, '2023-05-01', 4500.67, 1, 'First any% attempt, died to O&S multiple times'),
(5, 11, '2023-05-15', 8900.44, 1, 'All bosses run, struggled with DLC bosses'),

-- Elden Ring runs
(6, 12, '2023-06-01', 7200.33, 1, 'First speedrun attempt, need to optimize route'),
(6, 13, '2023-06-20', 14500.22, 1, 'All remembrances run, Malenia took forever'),

-- Hades runs
(7, 14, '2023-07-05', 1800.11, 1, 'Used the shield, got good RNG with boons'),

-- Metroid Dread runs
(8, 15, '2023-07-15', 5400.88, 1, 'First attempt, still learning the sequence breaks'),

-- Minecraft runs
(9, 16, '2023-08-01', 2400.45, 0, 'Got lucky with nether spawn'),
(9, 16, '2023-08-10', 2200.34, 1, 'Better seed but died in the nether'),

-- Portal runs
(10, 18, '2023-08-20', 900.56, 0, 'First serious attempt, chamber 18 gave me trouble'),
(10, 18, '2023-08-25', 850.23, 1, 'Good run but not a PB');
