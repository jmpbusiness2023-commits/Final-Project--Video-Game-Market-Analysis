INSERT INTO games (rawg_id, game_name, release_date, user_rating, ratings_count, avg_playtime_hours)
SELECT
    rawg_id,
    game_name,
    release_date,
    user_rating,
    ratings_count,
    avg_playtime_hours
FROM games_raw;

INSERT INTO genres (genre_name)
SELECT DISTINCT genre
FROM (
    SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(genres_list, ',', n.n), ',', -1)) AS genre
    FROM games_raw
    JOIN (
        SELECT 1 n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    ) n
    ON CHAR_LENGTH(genres_list) - CHAR_LENGTH(REPLACE(genres_list, ',', '')) >= n.n - 1
) t
WHERE genre IS NOT NULL;

INSERT INTO game_genres (game_id, genre_id)
SELECT
    g.game_id,
    ge.genre_id
FROM games_raw gr
JOIN games g ON gr.rawg_id = g.rawg_id
JOIN genres ge ON gr.genres_list LIKE CONCAT('%', ge.genre_name, '%');

INSERT INTO stores (store_name)
SELECT DISTINCT TRIM(store)
FROM (
    SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(store_list, ',', n.n), ',', -1) AS store
    FROM games_raw
    JOIN (
        SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
    ) n
    ON CHAR_LENGTH(store_list) - CHAR_LENGTH(REPLACE(store_list, ',', '')) >= n.n - 1
) t
WHERE store IS NOT NULL AND store != '';

INSERT INTO game_stores (game_id, store_id)
SELECT DISTINCT
    g.game_id,
    s.store_id
FROM games_raw gr
JOIN games g ON gr.rawg_id = g.rawg_id
JOIN stores s ON FIND_IN_SET(s.store_name, gr.store_list);

INSERT INTO platforms (platform_name)
SELECT DISTINCT TRIM(platform)
FROM (
    SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(platforms_list, ',', n.n), ',', -1) AS platform
    FROM games_raw
    JOIN (
        SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
    ) n
    ON CHAR_LENGTH(platforms_list) - CHAR_LENGTH(REPLACE(platforms_list, ',', '')) >= n.n - 1
) t
WHERE platform IS NOT NULL AND platform != '';

INSERT INTO game_platforms (game_id, platform_id)
SELECT DISTINCT
    g.game_id,
    p.platform_id
FROM games_raw gr
JOIN games g ON gr.rawg_id = g.rawg_id
JOIN platforms p ON FIND_IN_SET(p.platform_name, gr.platforms_list);
