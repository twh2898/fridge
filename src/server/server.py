from flask import Flask, g, request
import sqlite3
from dateutil.parser import parse as dateparse

if __debug__:
    DATABASE = '../reader/fridge.db'
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
    return db


with app.app_context():
    db = get_db()


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


# GET channel or all, must have a start time (something like since)

SELECT_DATA_QUERY = '''
SELECT *
FROM fridge_data
WHERE created > datetime(?)
ORDER BY created
'''


@app.route("/fridge", methods=['GET'])
def get_fridge():
    start = request.args.get('start')
    if not start:
        return 'Request must contain key start', 400
    res = query_db(SELECT_DATA_QUERY, (start,))
    return res


SELECT_CHANNEL_QUERY = '''
SELECT *
FROM fridge_data
WHERE channel = ? AND created > datetime(?)
ORDER BY created
'''


@app.route("/fridge/<int:channel>", methods=['GET'])
def get_channel(channel: int):
    start = request.args.get('start')
    if not start:
        return 'Request must contain key start', 400
    res = query_db(SELECT_CHANNEL_QUERY, (channel, start,))
    return res


if __name__ == '__main__':
    app.run(debug=__debug__)
