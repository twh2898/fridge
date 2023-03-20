CREATE TABLE IF NOT EXISTS fridge_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    channel INT NOT NULL,
    temp_c FLOAT NOT NULL,
    temp_f FLOAT NOT NULL
);

-- INSERT INTO fridge_data (channel, temp_c, temp_f) VALUES(1, 0.2, 0.3);
-- INSERT INTO fridge_data (channel, temp_c, temp_f) VALUES(1, 0.2, 0.3);
-- INSERT INTO fridge_data (channel, temp_c, temp_f) VALUES(1, 0.2, 0.3);
-- INSERT INTO fridge_data (channel, temp_c, temp_f) VALUES(1, 0.2, 0.3);
-- INSERT INTO fridge_data (channel, temp_c, temp_f) VALUES(1, 0.2, 0.3);
-- INSERT INTO fridge_data (channel, temp_c, temp_f) VALUES(1, 0.2, 0.3);
-- INSERT INTO fridge_data (channel, temp_c, temp_f) VALUES(1, 0.2, 0.3);
