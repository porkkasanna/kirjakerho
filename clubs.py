import db

def get_clubs():
    sql = """SELECT b.id, b.title, b.author, b.deadline, b.user_id, u.username
             FROM bookclubs b JOIN users u ON b.user_id = u.id
             GROUP BY b.id
             ORDER BY b.id DESC"""
    return db.query(sql)

def get_club(club_id):
    sql = """SELECT b.id, b.title, b.author, b.deadline, b.user_id, u.username
             FROM bookclubs b, users u
             WHERE b.user_id = u.id AND b.id = ?"""
    result = db.query(sql, [club_id])
    return result[0] if result else None

def add_club(user_id, title, author, deadline):
    sql = """INSERT INTO bookclubs (user_id, title, author, deadline, closed)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, title, author, deadline, 0])
    club_id = db.last_insert_id()
    return club_id

def update_club(club_id, title, author, deadline):
    sql = """UPDATE bookclubs
             SET title = ?, author = ?, deadline = ?
             WHERE id = ?"""
    db.execute(sql, [title, author, deadline, club_id])

def remove_club(club_id):
    sql = "DELETE FROM bookclubs WHERE id = ?"
    db.execute(sql, [club_id])

def search(query):
    sql = """SELECT b.id, b.title, b.author, u.username
             FROM bookclubs b, users u
             WHERE 
                b.user_id = u.id AND b.title LIKE ? OR
                b.user_id = u.id AND b.author LIKE ?
             ORDER BY b.id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])

def get_reviews(club_id):
    sql = """SELECT r.id, r.stars, r.content, r.sent_at, r.modified_at, r.user_id, u.username
             FROM reviews r, users u
             WHERE r.user_id = u.id AND r.club_id = ?
             ORDER BY r.id DESC"""
    return db.query(sql, [club_id])

def get_review(review_id):
    sql = """SELECT r.id, r.stars, r.content, r.sent_at, r.modified_at, r.club_id, r.user_id, u.username
             FROM reviews r, users u
             WHERE r.id = ? AND u.id = r.user_id"""
    result = db.query(sql, [review_id])
    return result[0] if result else None

def add_review(stars, content, club_id, user_id, sent_at):
    sql = """INSERT INTO reviews (stars, content, club_id, user_id, sent_at, modified_at)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [stars, content, club_id, user_id, sent_at, 0])

def update_review(review_id, stars, content, modified_at):
    sql = """UPDATE reviews
             SET stars = ?, content = ?, modified_at = ?
             WHERE id = ?"""
    db.execute(sql, [stars, content, modified_at, review_id])

def remove_review(review_id):
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])