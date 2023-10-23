from werkzeug.security import generate_password_hash


def add_data(db):
    db.executemany(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            [("admin", generate_password_hash("95@WtTjjMFKyZN6")),
             ("admin2", generate_password_hash("95@WtTjjMFKyZN5"))]
            )
    db.executemany(
            'INSERT INTO argument (title, content, user_id, id) VALUES (?, ?, ?, ?)',
            [("Example Argument", "This is an example argument", 1, 1),
             ("Example Argument 2", "This is an example argument 2", 1, 2),
             ("Example Argument 3", "This is an example argument 3", 2, 3)]
            )
    db.executemany(
            'INSERT INTO premise (title, content, user_id, id) VALUES (?, ?, ?, ?)',
            [("Example Premise", "This is an example premise", 1, 1),
             ("Example Premise 2", "This is an example premise 2", 1, 2),
             ("Example Premise 3", "This is an example premise 3", 1, 3),
             ("Example Premise 4", "This is an example premise 4", 2, 4)]
            )
    db.executemany(
            'INSERT INTO conclusion (title, content, user_id, id) VALUES (?, ?, ?, ?)',
            [("Example Conclusion", "This is an example conclusion", 1, 1),
             ("Example Conclusion 2", "This is an example conclusion 2", 1, 2),
             ("Example Conclusion 3", "This is an example conclusion 3", 2, 3)]
            )
    db.executemany(
            'INSERT INTO argument_premise (argument_id, premise_id) VALUES (?, ?)',
            [(1, 1), (1, 2), (1, 3), (2, 4)]
            )
    db.executemany(
            'INSERT INTO argument_conclusion (argument_id, conclusion_id) VALUES (?, ?)',
            [(1, 1), (2, 2), (3, 3)]
            )
    db.commit()

if __name__ == "__main__":
    from .db import get_db
    add_data(get_db())
    print("im in init_db.py")
