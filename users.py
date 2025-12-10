from werkzeug.security import check_password_hash, generate_password_hash
import db

def get_user(user_id):
    sql = """SELECT id, username, image IS NOT NULL has_image
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_clubs(user_id, page=1, page_size=5):
    sql = """SELECT b.id, b.title, b.author, b.user_id, u.username
             FROM bookclubs b, users u
             WHERE b.user_id = u.id AND u.id = ?
             ORDER BY b.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [user_id, limit, offset])

def club_count(user_id):
    sql = "SELECT COUNT(id) FROM bookclubs WHERE user_id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None

def get_reviews(user_id, page=1, page_size=5):
    sql = """SELECT r.id, r.stars, r.content, r.club_id, b.title club_title,
                 b.author club_author, r.sent_at, r.modified_at, r.user_id, u.username
             FROM reviews r, bookclubs b, users u
             WHERE u.id = ? AND r.user_id = u.id AND r.club_id = b.id
             ORDER BY r.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [user_id, limit, offset])

def review_count(user_id):
    sql = "SELECT COUNT(id) FROM reviews WHERE user_id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None

def update_image(user_id, image):
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])

def get_image(user_id):
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None

def add_user(username, password_hash):
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def remove_user(user_id):
    sql = "DELETE FROM users WHERE id = ?"
    db.execute(sql, [user_id])