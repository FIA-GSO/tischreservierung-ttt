import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''

#TODO payload checken, db aufrufen
@app.route('/tables/free', methods=['GET'])
def api_all():
    conn = sqlite3.connect('db/buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_entries = cur.execute('SELECT * FROM tische;').fetchall()

    return jsonify(all_entries)

@app.route('/tables/reserved', methods=['GET'])
def api2():
    conn = sqlite3.connect('db/buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM;').fetchall()

    return jsonify(all_books)



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()