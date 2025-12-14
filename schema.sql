CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB
);

CREATE TABLE bookclubs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT NOT NULL,
    author TEXT,
    deadline TEXT,
    closed INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE club_classes (
    id INTEGER PRIMARY KEY,
    club_id INTEGER,
    title TEXT,
    value TEXT,
    FOREIGN KEY (club_id) REFERENCES bookclubs(id) ON DELETE CASCADE
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    club_id INTEGER,
    user_id INTEGER,
    stars INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
    content TEXT,
    sent_at TEXT NOT NULL,
    modified_at TEXT,
    FOREIGN KEY (club_id) REFERENCES bookclubs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_club_reviews ON reviews (club_id);
CREATE INDEX idx_user_reviews ON reviews (user_id);
CREATE INDEX idx_user_clubs ON bookclubs (user_id);
CREATE INDEX idx_club_genres ON club_classes (club_id);