from werkzeug.security import check_password_hash, generate_password_hash
import db

def get_user(user_id):
    sql = """SELECT id, username, image IS NOT NULL has_image
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_clubs(user_id):
    sql = """SELECT id, title, author 
             FROM bookclubs WHERE user_id = ?
             ORDER BY id DESC"""
    return db.query(sql, [user_id])

def get_reviews(user_id):
    sql = """SELECT r.id, r.stars, r.club_id, b.title club_title,
                 b.author club_author, r.sent_at, r.modified_at
             FROM reviews r, bookclubs b
             WHERE r.user_id = ? AND r.club_id = b.id
             ORDER BY r.id DESC"""
    return db.query(sql, [user_id])

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