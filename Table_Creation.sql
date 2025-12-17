-- Active: 1761643009426@@localhost@3306@video_game_market
USE video_game_market;

DROP TABLE IF EXISTS games;
CREATE TABLE games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    rawg_id INT NOT NULL,
    game_name VARCHAR(255),
    release_date DATE,
    user_rating FLOAT,
    ratings_count INT,
    avg_playtime_hours FLOAT
);


DROP TABLE IF EXISTS platforms;
CREATE TABLE platforms (
    platform_id INT AUTO_INCREMENT PRIMARY KEY,
    platform_name VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS genres;
CREATE TABLE genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(100) UNIQUE
);

DROP TABLE IF EXISTS stores;
CREATE TABLE stores (
    store_id INT AUTO_INCREMENT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS game_platforms;
CREATE TABLE game_platforms (
    game_id INT,
    platform_id INT,
    PRIMARY KEY (game_id, platform_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id)
);

DROP TABLE IF EXISTS game_genres;
CREATE TABLE game_genres (
    game_id INT,
    genre_id INT,
    PRIMARY KEY (game_id, genre_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

DROP TABLE IF EXISTS game_stores;
CREATE TABLE game_stores (
    game_id INT,
    store_id INT,
    PRIMARY KEY (game_id, store_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
