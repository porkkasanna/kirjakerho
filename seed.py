import random
import sqlite3
from time import localtime, strftime

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM bookclubs")
db.execute("DELETE FROM reviews")
db.execute("DELETE FROM club_classes")

user_count = 10**3
club_count = 10**6
review_count = 10**7

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["käyttäjä" + str(i)])

genres = ["fantasia", "mysteeri", "romanssi", "historia",
           "sota", "kauhu", "jännitys", "rikos", "tieteiskirjallisuus",
           "huumori", "runokokoelma", "uskonnollinen", "klassikko",
           "nykykirjallisuus", "tietokirja", "self help", "lapset",
           "nuoret", "nuoret aikuiset", "aikuiset"]

deadlines = ["2025-12-01", "2025-12-10", "2025-12-31", "2026-03-03"]

for i in range(1, club_count + 1):
    user = random.randint(1, user_count)
    deadline = random.randint(0, 3)
    db.execute("INSERT INTO bookclubs (title, author, user_id, deadline) VALUES (?, ?, ?, ?)",
               ["Kirja " + str(i), "Kirjailija " + str(i), user, deadlines[deadline]])
    genre_amount = random.randint(0, 5)
    for j in range(genre_amount):
        genre = random.randint(0, 19)
        db.execute("INSERT INTO club_classes (club_id, title, value) VALUES (?, ?, ?)",
                    [i, "Genre", genres[genre]])

for i in range(1, review_count + 1):
    user_id = random.randint(1, user_count)
    club_id = random.randint(1, club_count)
    stars = random.randint(1, 5)
    sent_at = strftime("%d.%m.%Y, kello %H:%M", localtime())
    modified_at = strftime("%d.%m.%Y, kello %H:%M", localtime())
    if i % 2 == 0:
        db.execute("""INSERT INTO reviews (stars, content, sent_at, user_id, club_id)
                      VALUES (?, ?, ?, ?, ?)""",
                      [stars, "arvostelu" + str(i), sent_at, user_id, club_id])
    else:
        db.execute("""INSERT INTO reviews (stars, content, sent_at, user_id, club_id, modified_at)
                      VALUES (?, ?, ?, ?, ?, ?)""",
                      [stars, "arvostelu" + str(i), sent_at, user_id, club_id, modified_at])

db.commit()
db.close()
