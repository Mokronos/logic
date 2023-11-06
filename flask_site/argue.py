from flask import render_template, redirect, url_for, request, Blueprint, g, flash, Markup, escape
from .db import get_db
from .htmx import htmx

from .auth import login_required
from .utils import data
from .utils.helpers import htmx_required

import json
import textwrap

bp = Blueprint('argue', __name__, url_prefix='/')

@bp.route('/', methods=('GET',))
@htmx_required
def overview():
    db = get_db()
    arguments = db.execute(
            'SELECT argument.*, user.username FROM argument JOIN user ON argument.user_id = user.id ORDER BY created DESC',
            ()
            ).fetchall()

    # get list of all the premises ids of each argument
    # there might be a better way to do this, via a join or something
    arguments_premises = dict()
    arguments_conclusions = dict()
    for argument in arguments:
        prems = db.execute(
                'SELECT id,title,content FROM argument_premise INNER JOIN premise ON argument_premise.premise_id = premise.id WHERE argument_premise.argument_id = ?',
                (argument['id'],)
                ).fetchall()
        arguments_premises[argument['id']] = prems
        concs = db.execute(
                'SELECT id,title,content FROM argument_conclusion INNER JOIN conclusion ON argument_conclusion.conclusion_id = conclusion.id WHERE argument_conclusion.argument_id = ?',
                (argument['id'],)
                ).fetchall()
        arguments_conclusions[argument['id']] = concs

    return {'template': 'argue/overview.html',
            'context': {'arguments': arguments, 'arguments_premises': arguments_premises, 'arguments_conclusions': arguments_conclusions}}


@bp.route('/connect', methods=('GET', 'POST'))
@htmx_required
@login_required
def connect():

    db = get_db()

    if request.method == 'POST':

        argument_id = request.form.get('arg')
        category = request.form.get('category')
        id = 1

        arg_ids = db.execute("""
                            SELECT id FROM argument WHERE user_id = ?
                            """,
                            (g.user['id'],)
                            ).fetchall()

        try:
            if category == 'premise':
                db.execute("""
                        INSERT INTO argument_premise (argument_id, premise_id) VALUES (?, ?)
                        """,
                        (argument_id, id)
                        )
            elif category == 'conclusion':
                db.execute("""
                        INSERT INTO argument_conclusion (argument_id, conclusion_id) VALUES (?, ?)
                        """,
                        (argument_id, id)
                        )
            db.commit()
        except db.IntegrityError:
            flash("This item is already connected to the argument")
            return redirect(url_for('argue.connect'))

        return redirect(url_for('argue.connect'))


    arguments = db.execute("""
            SELECT argument.id, argument.title FROM argument 
            WHERE argument.user_id = ?
            """,
            (g.user['id'],)
            ).fetchall()

    conclusions_premises = db.execute("""
                                      SELECT * FROM (
                                        SELECT 'premise' AS category, title, content, id, created, user_id FROM premise UNION
                                        SELECT 'conclusion' AS category, title, content, id, created, user_id FROM conclusion)
                                        WHERE user_id = ?
                                      """,
                                      (g.user['id'],)
                                      ).fetchall()

    return 'argue/connect.html', {'arguments': arguments, 'conclusions_premises': conclusions_premises}

@bp.route('/list', methods=('GET','POST'))
@htmx_required
def list_overview():

    if request.method == 'POST':
        items = data.get_all(get_db(), g, request)
        return 'argue/list.html', {'items': items}

    items = data.get_all(get_db(), g, request)
    return 'argue/list.html', {'items': items}


@bp.route('/create/<category>', methods=('GET', 'POST'))
@htmx_required
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
                    return redirect(url_for('argue.overview'))

            flash(error)

        return 'argue/create_argument.html'
    
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
                    return redirect(url_for('argue.overview'))

            flash(error)

        db = get_db()
        arguments = db.execute(
                'SELECT id, title FROM argument WHERE user_id = ? ORDER BY created DESC',
                (g.user['id'],)
                ).fetchall()

        return 'argue/create_premise.html', {'arguments': arguments}

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
                    return redirect(url_for('argue.overview'))

            flash(error)
        db = get_db()
        arguments = db.execute(
                'SELECT id, title FROM argument WHERE user_id = ? ORDER BY created DESC',
                (g.user['id'],)
                ).fetchall()

        return 'argue/create_conclusion.html', {'arguments': arguments}
    return redirect(url_for('argue.overview'))


@bp.route('/delete/<category>/<int:id>', methods=('DELETE',))
@login_required
def delete(id, category):
    db = get_db()
    check = None
    if category == 'argument':
        check = db.execute('DELETE FROM argument WHERE id = ? AND user_id = ?', (id, g.user['id']))
    elif category == 'premise':
        check = db.execute('DELETE FROM premise WHERE id = ? AND user_id = ?', (id, g.user['id']))
    elif category == 'conclusion':
        check = db.execute('DELETE FROM conclusion WHERE id = ? AND user_id = ?', (id, g.user['id']))

    if check and check.rowcount == 0:
        flash("You don't have permission to delete this item")
        return "", 403
    db.commit()
    return "", 200


@bp.route('/details/<category>/<int:id>', methods=('GET',))
@htmx_required
def details(id, category):

    db = get_db()

    if category == 'argument':
        item = db.execute(
                "SELECT * FROM argument WHERE id = ?",
                (id,)
                ).fetchone()
    elif category == 'premise':
        item = db.execute(
                "SELECT * FROM premise WHERE id = ?",
                (id,)
                ).fetchone()
    elif category == 'conclusion':
        item = db.execute(
                "SELECT * FROM conclusion WHERE id = ?",
                (id,)
                ).fetchone()
    else:
        return redirect(url_for('argue.list_overview'))

    if not item:
        flash("Requested item does not exist (anymore?)")
        return redirect(url_for('argue.list_overview'))

    return 'argue/details.html', {'item': item, 'category': category}

    
@bp.route('/edit/<category>/<int:id>', methods=('GET', 'PUT'))
@htmx_required
@login_required
def edit(id, category):

    db = get_db()

    if request.method == 'PUT':
        title = request.form['title']
        content = request.form['content']

        if category == 'argument':
            db.execute(
                "UPDATE argument SET title = ?, content = ? WHERE id = ?",
                (title, content, id)
                )
        elif category == 'premise':
            db.execute(
                "UPDATE premise SET title = ?, content = ? WHERE id = ?",
                (title, content, id)
                )
        elif category == 'conclusion':
            db.execute(
                "UPDATE conclusion SET title = ?, content = ? WHERE id = ?",
                (title, content, id)
                )
        db.commit()

        return redirect(url_for('argue.details', category=category, id=id), code=303)

    if category == 'argument':
        item = db.execute(
                "SELECT * FROM argument WHERE id = ?",
                (id,)
                ).fetchone()
    elif category == 'premise':
        item = db.execute(
                "SELECT * FROM premise WHERE id = ?",
                (id,)
                ).fetchone()
    elif category == 'conclusion':
        item = db.execute(
                "SELECT * FROM conclusion WHERE id = ?",
                (id,)
                ).fetchone()
    else:
        return redirect(url_for('argue.list_overview'))

    return 'argue/edit.html', {'item': item, 'category': category}


@bp.route('/share/<int:id>', methods=('GET',))
def share(id):
    db = get_db()

    # get argument info
    argument = db.execute(
            "SELECT * FROM argument WHERE id = ?",
            (id,)
            ).fetchone()

    # get premises and conclusions
    prems = db.execute(
            "SELECT * FROM premise WHERE id IN (SELECT premise_id FROM argument_premise WHERE argument_id = ?)",
            (id,)
            ).fetchall()
    concs = db.execute(
            "SELECT * FROM conclusion WHERE id IN (SELECT conclusion_id FROM argument_conclusion WHERE argument_id = ?)",
            (id,)
            ).fetchall()

    # escape probably not necessary, not using in html, only script tags
    # Build markdown content for premises
    md_prems = '\n'.join([f"- **{escape(prem['title'])}**: {escape(prem['content'])}\n" for prem in prems])

    # Build markdown content for conclusions
    md_concs = '\n'.join([f"- **{escape(conc['title'])}**: {escape(conc['content'])}\n" for conc in concs])

    # Construct the entire markdown string
    markdown = (
        f"# Argument Title: {escape(argument['title'])}\n\n"
        f"{escape(argument['content'])}\n\n"
        "## Premises\n"
        f"{md_prems}\n\n"
        "## Conclusions\n"
        f"{md_concs}\n\n"
        f"---\n\n"
        f"[Link to Full Argument Details]({request.url_root}argue/details/argument/{id})"
    )

    # Escape the markdown for safe inclusion in a JavaScript string
    escaped_markdown = json.dumps(markdown)

    # Generate the script snippet to copy the escaped markdown
    script = f'''
    <script>
        navigator.clipboard.writeText({escaped_markdown})
    </script>
    '''
    return script

@bp.route('/status', methods=('GET',))
def status():
    return render_template('basics/flash.html')
