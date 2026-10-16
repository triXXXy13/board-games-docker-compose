CREATE TABLE IF NOT EXISTS board_games (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    players_min INTEGER NOT NULL CHECK (players_min > 0),
    players_max INTEGER NOT NULL CHECK (players_max >= players_min),
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    genre TEXT NOT NULL,
    description TEXT NOT NULL,
    saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Демонстрационные записи клуба имеют собственные идентификаторы,
-- поэтому все игры из Web-service можно отдельно добавлять в коллекцию.
INSERT INTO board_games
(id, title, players_min, players_max, duration_minutes, genre, description)
VALUES
('club-demo-chess', 'Шахматы клуба', 2, 2, 45, 'Логическая', 'Классическая стратегическая игра для двух игроков.'),
('club-demo-checkers', 'Шашки клуба', 2, 2, 30, 'Логическая', 'Классическая настольная игра для двух игроков.')
ON CONFLICT (id) DO NOTHING;
