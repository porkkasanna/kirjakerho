CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB
);

CREATE TABLE bookclubs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    title TEXT,
    author TEXT,
    deadline TEXT,
    closed INTEGER
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE club_classes (
    id INTEGER PRIMARY KEY,
    club_id INTEGER REFERENCES bookclubs,
    title TEXT,
    value TEXT
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    club_id INTEGER REFERENCES bookclubs,
    user_id INTEGER REFERENCES users,
    stars INTEGER,
    content TEXT,
    sent_at TEXT,
    modified_at TEXT
);