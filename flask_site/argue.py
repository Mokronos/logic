from flask import render_template, redirect, url_for, request, Blueprint, g, flash
from .db import get_db

from .auth import login_required

bp = Blueprint('argue', __name__, url_prefix='/argue')

@bp.route('/')
@login_required
def index():
    db = get_db()
    arguments = db.execute(
            'SELECT * FROM argument WHERE user_id = ? ORDER BY created DESC',
            (g.user['id'],)
            ).fetchall()

    # get list of all the premises ids of each argument
    arguments_premises = dict()
    arguments_conclusions = dict()
    for argument in arguments:
        arguments_premises[argument['id']] = db.execute(
                'SELECT premise_id FROM argument_premise WHERE argument_id = ?',
                (argument['id'],)
                ).fetchall()
        arguments_conclusions[argument['id']] = db.execute(
                'SELECT conclusion_id FROM argument_conclusion WHERE argument_id = ?',
                (argument['id'],)
                ).fetchall()

    # create tree diagram structure of argument in html

    premises = db.execute(
            'SELECT * FROM premise WHERE user_id = ? ORDER BY created DESC',
            (g.user['id'],)
            ).fetchall()
    conclusions = db.execute(
            'SELECT * FROM conclusion WHERE user_id = ? ORDER BY created DESC',
            (g.user['id'],)
            ).fetchall()

    return render_template('argue/overview_new.html',
                           arguments=arguments,
                           premises=premises,
                           conclusions=conclusions,
                           arguments_premises=arguments_premises,
                           arguments_conclusions=arguments_conclusions)


@bp.route('/create/<category>', methods=('GET', 'POST'))
@login_required
def create(category):
    if category == 'argument':
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']

            db = get_db()
            error = None

            if not title:
                error = 'Title is required.'
            elif not content:
                error = 'Description is required.'

            if error is None:
                try:
                    db.execute(
                            'INSERT INTO argument (title, content, user_id) VALUES (?, ?, ?)',
                            (title, content, g.user['id'])
                            )
                    db.commit()
                except db.IntegrityError:
                    error = f"Argument {title} is already registered."
                else:
                    return redirect(url_for('argue.index'))

            flash(error)

        return render_template('argue/create_argument.html')
    
    if category == 'premise':
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            argument_id = request.form['argument_id']

            db = get_db()
            error = None

            if not title:
                error = 'Title is required.'
            elif not content:
                error = 'Description is required.'

            if error is None:
                try:
                    cur = db.execute(
                            'INSERT INTO premise (title, content, user_id) VALUES (?, ?, ?)',
                            (title, content, g.user['id'])
                            )
                    db.execute(
                            'INSERT INTO argument_premise (argument_id, premise_id) VALUES (?, ?)',
                            (argument_id, cur.lastrowid)
                            )
                    db.commit()
                except db.IntegrityError:
                    error = f"Premise {title} is already registered."
                else:
                    return redirect(url_for('argue.index'))

            flash(error)

        db = get_db()
        arguments = db.execute(
                'SELECT id, title FROM argument WHERE user_id = ? ORDER BY created DESC',
                (g.user['id'],)
                ).fetchall()

        return render_template('argue/create_premise.html', arguments=arguments)

    if category == 'conclusion':
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            argument_id = request.form['argument_id']

            db = get_db()
            error = None

            if not title:
                error = 'Title is required.'
            elif not content:
                error = 'Description is required.'

            if error is None:
                try:
                    cur = db.execute(
                            'INSERT INTO conclusion (title, content, user_id) VALUES (?, ?, ?)',
                            (title, content, g.user['id'])
                            )

                    db.execute(
                            'INSERT INTO argument_conclusion (argument_id, conclusion_id) VALUES (?, ?)',
                            (argument_id, cur.lastrowid)
                            )

                    db.commit()
                except db.IntegrityError:
                    error = f"Conclusion {title} is already registered."
                else:
                    return redirect(url_for('argue.index'))

            flash(error)
        db = get_db()
        arguments = db.execute(
                'SELECT id, title FROM argument WHERE user_id = ? ORDER BY created DESC',
                (g.user['id'],)
                ).fetchall()

        return render_template('argue/create_conclusion.html', arguments=arguments)
    return redirect(url_for('argue.index'))


@bp.route('/delete/<int:id>', methods=('DELETE',))
@login_required
def delete(id):
    print(f"Deleting argument {id}")
    db = get_db()
    check = db.execute('DELETE FROM argument WHERE id = ? AND user_id = ?', (id, g.user['id']))
    if check.rowcount == 0:
        return "", 403
    db.commit()
    return "", 200
