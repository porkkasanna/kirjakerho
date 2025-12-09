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
    closed INTEGER,
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