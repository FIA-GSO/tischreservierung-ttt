import flask
from flask import request   # wird benötigt, um die HTTP-Parameter abzufragen
from flask import jsonify   # übersetzt python-dicts in json
from flask import send_file 

app = flask.Flask(__name__)
app.config["DEBUG"] = True  # Zeigt Fehlerinformationen im Browser, statt nur einer generischen Error-Message



menu =[{    "name":"Pizza Mario",
            "belag": [
                {1:"Mozarella"},
                {2:"Tomatensauce"}
            ],
            "preis": 9.50
        },
        {
            "name":"Pizza Luigi",
            "belag": [
                {1:"Mozarella"},
                {2:"Spinat"}
            ],
            "preis": 12.50
        }
]



@app.route('/', methods=['GET'])
def home():
    return send_file('index.html')

app.run()
