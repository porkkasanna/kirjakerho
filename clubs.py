import db

def get_clubs():
    sql = """SELECT b.id, b.title, b.author, b.deadline, u.username
             FROM bookclubs b, users u
             WHERE b.user_id = u.id
             ORDER BY b.id DESC"""
    return db.query(sql)

def get_club(club_id):
    sql = """SELECT b.id, b.title, b.author, b.deadline, b.user_id, u.username
             FROM bookclubs b, users u
             WHERE b.user_id = u.id AND b.id = ?"""
    result = db.query(sql, [club_id])
    return result[0]

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