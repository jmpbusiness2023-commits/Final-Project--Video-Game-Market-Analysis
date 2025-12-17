SELECT 
    g.genre_name,
    ROUND(AVG(ga.user_rating), 2) AS avg_rating,
    COUNT(DISTINCT ga.rawg_id) AS nb_games
FROM games ga
JOIN game_genres gg ON ga.rawg_id = gg.game_id
JOIN genres g ON gg.genre_id = g.genre_id
WHERE ga.user_rating IS NOT NULL
GROUP BY g.genre_name
HAVING COUNT(DISTINCT ga.rawg_id) >= 20
ORDER BY avg_rating DESC;

SELECT 
    s.store_name,
    COUNT(DISTINCT g.rawg_id) AS nb_games
FROM game_stores gs
JOIN stores s ON gs.store_id = s.store_id
JOIN games g ON gs.rawg_id = g.rawg_id
GROUP BY s.store_name
ORDER BY nb_games DESC;






