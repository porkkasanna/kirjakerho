import db

def get_clubs(page, page_size):
    sql = """SELECT b.id, b.title, b.author, b.deadline, b.user_id, u.username
             FROM bookclubs b JOIN users u ON b.user_id = u.id
             GROUP BY b.id
             ORDER BY b.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def get_club(club_id):
    sql = """SELECT b.id, b.title, b.author, b.deadline, b.user_id, u.username
             FROM bookclubs b, users u
             WHERE b.user_id = u.id AND b.id = ?"""
    result = db.query(sql, [club_id])
    return result[0] if result else None

def club_count():
    sql = "SELECT COUNT(id) FROM bookclubs"
    result = db.query(sql)
    return result[0][0] if result else None

def add_club(user_id, title, author, deadline, classes):
    sql = """INSERT INTO bookclubs (user_id, title, author, deadline, closed)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, title, author, deadline, 0])
    club_id = db.last_insert_id()

    sql = "INSERT INTO club_classes (club_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [club_id, title, value])

    return club_id

def update_club(club_id, title, author, deadline, classes):
    sql = """UPDATE bookclubs
             SET title = ?, author = ?, deadline = ?
             WHERE id = ?"""
    db.execute(sql, [title, author, deadline, club_id])

    if len(classes) > 0:
        sql = "DELETE FROM club_classes WHERE club_id = ?"
        db.execute(sql, [club_id])

        sql = "INSERT INTO club_classes (club_id, title, value) VALUES (?, ?, ?)"
        for title, value in classes:
            db.execute(sql, [club_id, title, value])

def remove_club(club_id):
    sql = "DELETE FROM bookclubs WHERE id = ?"
    db.execute(sql, [club_id])

def query_count(query, query_from):
    sql = """SELECT COUNT(id) FROM bookclubs """

    if query_from == "title":
        sql = sql + """WHERE title LIKE ?"""
    elif query_from == "author":
        sql = sql + """WHERE author LIKE ?"""
    elif query_from == "user":
        sql = """SELECT COUNT(b.id)
                 FROM bookclubs b, users u
                 WHERE b.user_id = u.id AND u.username LIKE ?"""
    elif query_from == "genre":
        sql = """SELECT COUNT(b.id) 
                 FROM bookclubs b, club_classes c
                 WHERE c.club_id = b.id AND c.value LIKE ?"""
    else:
        return 0
    
    like = "%" + query + "%"
    result = db.query(sql, [like])
    return result[0][0] if query else None

def search(query, query_from, page, page_size):
    sql = """SELECT b.id, b.title, b.author, u.username
             FROM bookclubs b, users u """
    
    if query_from == "title":
        sql = sql + """WHERE b.user_id = u.id AND b.title LIKE ?
                       ORDER BY b.id DESC
                       LIMIT ? OFFSET ?"""
    elif query_from == "author":
        sql = sql + """WHERE b.user_id = u.id AND b.author LIKE ?
                       ORDER BY b.id DESC
                       LIMIT ? OFFSET ?"""
    elif query_from == "user":
        sql = sql + """WHERE b.user_id = u.id AND u.username LIKE ?
                       ORDER BY b.id DESC
                       LIMIT ? OFFSET ?"""
    elif query_from == "genre":
        sql = """SELECT b.id, b.title, b.author, u.username
                 FROM bookclubs b, users u, club_classes c
                 WHERE 
                    b.user_id = u.id AND
                    c.club_id = b.id AND
                    c.value LIKE ?
                 ORDER BY b.id DESC
                 LIMIT ? OFFSET ?"""
    
    limit = page_size
    offset = page_size * (page - 1)
    like = "%" + query + "%"
    return db.query(sql, [like, limit, offset])

def get_reviews(club_id, page=1, page_size=5):
    sql = """SELECT r.id, r.stars, r.content, r.sent_at, r.modified_at, r.user_id, u.username
             FROM reviews r, users u
             WHERE r.user_id = u.id AND r.club_id = ?
             ORDER BY r.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [club_id, limit, offset])

def get_review(review_id):
    sql = """SELECT r.id, r.stars, r.content, r.sent_at, r.modified_at, r.club_id, r.user_id, u.username
             FROM reviews r, users u
             WHERE r.id = ? AND u.id = r.user_id"""
    result = db.query(sql, [review_id])
    return result[0] if result else None

def review_count(club_id):
    sql = "SELECT COUNT(id) FROM reviews WHERE club_id = ?"
    result = db.query(sql, [club_id])
    return result[0][0] if result else None

def add_review(stars, content, club_id, user_id, sent_at):
    sql = """INSERT INTO reviews (stars, content, club_id, user_id, sent_at, modified_at)
             VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [stars, content, club_id, user_id, sent_at, 0])

def update_review(review_id, stars, content, modified_at):
    sql = """UPDATE reviews
             SET stars = ?, content = ?, modified_at = ?
             WHERE id = ?"""
    db.execute(sql, [stars, content, modified_at, review_id])

def remove_review(review_id):
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        if title not in classes:
            classes[title] = []
        classes[title].append(value)
    
    return classes

def get_classes(club_id):
    sql = "SELECT title, value FROM club_classes WHERE club_id = ?"
    return db.query(sql, [club_id])