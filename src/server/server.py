from flask import Flask, g
import sqlite3

if __debug__:
    DATABASE = './main.db'
else:
    DATABASE = '/srv/fridge/fridge.db'

app = Flask(__name__)


def get_db():
    """Get the database object."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

        def make_dicts(cursor, row):
            return dict((cursor.description[idx][0], value)
                        for idx, value in enumerate(row))

        db.row_factory = make_dicts
        # db.row_factory = sqlite3.Row
    return db


with app.app_context():
    db = get_db()
    if __debug__:
        with app.open_resource('init.sql', 'r') as f:
            db.executescript(f.read())
            db.commit()


def query_db(query, args=(), one=False):
    """Execute a query and return it's results."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_db(title, content):
    """Execute a query INSERT."""
    cur = get_db().execute('INSERT INTO posts (title, content) VALUES(?, ?)',
                           (title, content))
    get_db().commit()
    cur.close()


@app.teardown_appcontext
def close_connection(exception):
    """Close database."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/api")
def hello_world():
    return "Hello, World!"


@app.route("/api/get")
def get():
    res = query_db("SELECT * FROM posts")
    return str(res)


@app.route("/api/put")
def put():
    res = insert_db("title", "Content")
    return 'ok'


if __name__ == '__main__':
    app.run(debug=__debug__)
