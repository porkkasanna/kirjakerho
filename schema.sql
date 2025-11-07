CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE bookclubs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    title TEXT,
    author TEXT,
    deadline TEXT,
    closed INTEGER
);

CREATE TABLE genres (
    id INTEGER PRIMARY KEY,
    club_id INTEGER REFERENCES bookclubs
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    club_id INTEGER REFERENCES bookclubs,
    user_id INTEGER REFERENCES users,
    stars INTEGER,
    review TEXT,
    sent_at TEXT
);