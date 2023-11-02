from flask import render_template, redirect, url_for, request, Blueprint, g, flash, make_response
from .db import get_db
from .htmx import htmx

from .auth import login_required
# this seems weird, why can't i import utils.data (__init__ exists)
from .utils import data

bp = Blueprint('argue', __name__, url_prefix='/argue')

@bp.route('/')
@login_required
def index():
    db = get_db()
    arguments = db.execute(
            'SELECT * FROM argument ORDER BY created DESC',
            ()
            ).fetchall()

    # get list of all the premises ids of each argument
    arguments_premises = dict()
    arguments_conclusions = dict()
    md = dict()
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

        

    # create tree diagram structure of argument in html

    premises = db.execute(
            'SELECT * FROM premise WHERE user_id = ? ORDER BY created DESC',
            (g.user['id'],)
            ).fetchall()
    conclusions = db.execute(
            'SELECT * FROM conclusion WHERE user_id = ? ORDER BY created DESC',
            (g.user['id'],)
            ).fetchall()



    return render_template('argue/overview.html',
                           arguments=arguments,
                           premises=premises,
                           conclusions=conclusions,
                           arguments_premises=arguments_premises,
                           arguments_conclusions=arguments_conclusions,
                           md=md)

@bp.route('/connect', methods=('GET', 'POST'))
@login_required
def connect():

    db = get_db()

    if htmx:
        base_template = 'basics/_partial.html'
    else:
        base_template = 'base.html'

    if request.method == 'POST':
        argument_id = request.form.get('arg')
        prem_conc = request.form.get('prem_conc')
        if not argument_id or not prem_conc:
            return make_response("Bad request", 400)
        import ast
        prem_conc = ast.literal_eval(prem_conc)

        print(f"Connecting {prem_conc['category']} {prem_conc['id']} to argument {argument_id}")

        try:
            if prem_conc['category'] == 'premise':
                db.execute("""
                        INSERT INTO argument_premise (argument_id, premise_id) VALUES (?, ?)
                        """,
                        (argument_id, prem_conc['id'])
                        )
            elif prem_conc['category'] == 'conclusion':
                db.execute("""
                        INSERT INTO argument_conclusion (argument_id, conclusion_id) VALUES (?, ?)
                        """,
                        (argument_id, prem_conc['id'])
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

    return render_template('argue/connect.html', base_template=base_template, arguments=arguments, conclusions_premises=conclusions_premises)

@bp.route('/list', methods=('GET','POST'))
@login_required
def list_overview():
    # hacky
    re = request.args.get('re')

    if htmx and re:
        print("htmx is enabled")
        base_template = 'basics/_partial.html'
    else:
        base_template = 'base.html'

    if request.method == 'POST':
        items = data.get_all(get_db(), g, request)
        return render_template('argue/list.html', base_template = base_template, items=items)

    items = data.get_all(get_db(), g, request)
    return render_template('argue/list.html', base_template=base_template, items=items) 

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


@bp.route('/delete/<category>/<int:id>', methods=('DELETE',))
@login_required
def delete(id, category):
    print(f"Deleting {category} {id}")
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
@login_required
def details(id, category):

    db = get_db()
    if htmx:
        print("htmx is enabled in details")
        base_template = 'basics/_partial.html'
    else:
        base_template = 'base.html'

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
        return redirect(url_for('argue.list_overview', re=True))

    if not item:
        flash("Requested item does not exist (anymore?)")
        return redirect(url_for('argue.list_overview', re=True))

    return render_template('argue/details.html', base_template=base_template, item=item, category=category)
    
@bp.route('/edit/<category>/<int:id>', methods=('GET', 'PUT'))
@login_required
def edit(id, category):

    db = get_db()

    if htmx:
        print("htmx is enabled in edit")
        base_template = 'basics/_partial.html'
    else:
        base_template = 'base.html'

    if request.method == 'PUT':
        title = request.form['title']
        content = request.form['content']
        print("im putting")

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
        # hacky
        return redirect(url_for('argue.list_overview', re=True))

    return render_template('argue/edit.html', base_template=base_template, item=item, category=category)


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

    md_prems = "".join([f"### {prem['title']}\n{prem['content']}\n" for prem in prems])
    md_concs = "".join([f"### {conc['title']}\n{conc['content']}\n" for conc in concs])
    

    markdown = f"""
    # {argument['title']}
    {argument['content']}
    ## Premises
    {md_prems}
    ## Conclusion
    {md_concs}
    Link: [{request.url_root}argue/details/argument/{id}]({request.url_root}argue/details/argument/{id})
    """
    markdown = markdown.replace("\n", "\\n")
    markdown = " ".join(markdown.split())
    print(markdown)
    resp = f'''
    <script>
        navigator.clipboard.writeText("{markdown}")
    </script>
    '''
    print(resp)
    return resp
