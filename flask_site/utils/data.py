def get_all(db, g, request):

    q = request.form.get('q')
    own = request.form.get('own')

    items = db.execute("""
            SELECT U.*, user.username FROM (
            SELECT * FROM (
            SELECT 'argument' AS category, title, content, id, created, user_id FROM argument UNION
            SELECT 'premise' AS category, title, content, id, created, user_id FROM premise UNION
            SELECT 'conclusion' AS category, title, content, id, created, user_id FROM conclusion)
            AS U
            WHERE title LIKE ? AND (? = 0 OR user_id = ?)
            ORDER BY title DESC) AS U
            JOIN user ON user.id = U.user_id
            """, ('%' + (q if q else "") + '%', 1 if own == 'on' else 0, g.user['id'])).fetchall()

    return items