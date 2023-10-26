import flask
from flask import request, jsonify
import sqlite3
import datetime

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def establish_connection(needs_conn = False):
    if needs_conn:
      return sqlite3.connect('db/buchungssystem.sqlite')
    conn = sqlite3.connect('db/buchungssystem.sqlite')
    conn.row_factory = dict_factory
    return conn.cursor()

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Buchung für Tische im ___</h1>
<p></p>'''

@app.route('/tables', methods=['GET'])
def show_free_tables():
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Zeitpunkt nicht angegeben'}), 400
    
    cur = establish_connection()
    try:
        # Alle Tischenummern zurückgeben, welche nicht belegt sind/storniert sind
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

@app.route('/reservations', methods=['GET'])
def show_reserved_tables_today():
    current_date = datetime.date.today()
    
    cur = establish_connection()
    try:
        # Alle Tischenummern zurückgeben, welche belegt oder storniert sind für den Tag
        query = '''
        SELECT t.tischnummer
        FROM tische t
        WHERE t.tischnummer IN (
            SELECT DISTINCT r.tischnummer
            FROM reservierungen r
            WHERE (
              r.zeitpunkt < DATETIME(?, '+1 day')
            ) AND r.storniert = 'False'
        );
        '''
        cur.execute(query, (current_date))
        result = cur.fetchall()

        return jsonify(result)

    except Exception as e:
        return str(e)
    finally:
        cur.close()

@app.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    tischnummer = data.get('tischnummer')
    zeitpunkt = data.get('zeitpunkt')
    
    if not tischnummer or not zeitpunkt:
        return jsonify({'error': 'Ungültige Anfrage'}), 400
    
    try:
        conn = establish_connection(needs_conn = True)
        conn.row_factory = dict_factory
        cur = conn.cursor()
        
        # Überprüfen, ob der ausgewählte Tisch zu diesem Zeitpunkt verfügbar ist
        availability_query = '''
        SELECT COUNT(*) 
        FROM reservierungen 
        WHERE zeitpunkt = ? AND tischnummer = ? AND storniert = 'False'
        '''
        
        cur.execute(availability_query, (zeitpunkt, tischnummer))
        is_table_available = cur.fetchone()[0]
        
        if is_table_available > 0:
            return jsonify({'error': 'Der ausgewählte Tisch ist nicht verfügbar'}), 400
        
        pin = 1337
        reservierungsnummer = 42
        
        # Hinzufügen der Reservierung zur Datenbank
        insert_query = '''
        INSERT INTO reservierungen (zeitpunkt, tischnummer, pin, storniert)
        VALUES (?, ?, ?, 'False')
        '''
        
        cur.execute(insert_query, (zeitpunkt, tischnummer, pin))
        conn.commit()
        
        return jsonify({'reservierungsnummer': reservierungsnummer, 'pin': pin})
    
    except Exception as e:
        return str(e)
    finally:
        cur.close()
        conn.close()

@app.route('/reservations/<int:reservierungsnummer>', methods=['DELETE'])
def cancel_reservation(reservierungsnummer):
    data = request.get_json()
    received_pin = data.get('pin')
    
    if not received_pin:
        return jsonify({'error': 'Ungültige Anfrage'}), 400
    
    try:
        conn = establish_connection()
        cur = conn.cursor()
        
        # Überprüfen, ob die Reservierung existiert und nicht bereits storniert wurde
        check_reservation_query = '''
        SELECT storniert, pin
        FROM reservierungen
        WHERE reservierungsnummer = ?
        '''
        
        cur.execute(check_reservation_query, (reservierungsnummer,))
        reservation = cur.fetchone()
        
        if not reservation:
            return jsonify({'error': 'Reservierung nicht gefunden'}), 404
        
        if reservation['storniert'] == 'True':
            return jsonify({'error': 'Reservierung bereits storniert'}), 400
        
        if int(received_pin) != int(reservation['pin']):
            return jsonify({'error': 'Ungültiger PIN'}), 400
        
        # Markieren der Reservierung als storniert
        cancel_query = '''
        UPDATE reservierungen
        SET storniert = 'True'
        WHERE reservierungsnummer = ?
        '''
        
        cur.execute(cancel_query, (reservierungsnummer))
        conn.commit()
        
        return jsonify({'message': 'Reservierung storniert'})
    
    except Exception as e:
        return str(e)
    finally:
        cur.close()
        conn.close()

@app.errorhandler(404)

def page_not_found(e):
  return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()
