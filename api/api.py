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
    return '''<h1>Buchung für Tische im ___</h1>
<p></p>'''

def estConnection():
    conn = sqlite3.connect('db/buchungssystem.sqlite')
    conn.row_factory = dict_factory
    return conn.cursor()

#TODO payload checken
@app.route('/tables/free', methods=['GET'])
def show_free_tables():
    date = request.args.get('date')
    
    try:
        cur = estConnection()
        query = '''
        SELECT t.tischnummer
        FROM tische t
        WHERE t.tischnummer NOT IN (
            SELECT DISTINCT r.tischnummer
            FROM reservierungen r
            WHERE (
                r.zeitpunkt >= ? 
                AND r.zeitpunkt < DATETIME(?, '+30 minutes')
            ) AND r.storniert = 'False'
        );
        '''
        cur.execute(query, (date, date))
        result = cur.fetchall()

        return jsonify(result)

    except Exception as e:
        return str(e)
    finally:
        cur.close()

@app.route('/tables/reserved', methods=['GET'])
def api2():
    cur = estConnection()
    all_books = cur.execute('SELECT * FROM;').fetchall()

    return jsonify(all_books)



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()