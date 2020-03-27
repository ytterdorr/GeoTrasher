import flask
import sqlite3
from gevent.pywsgi import WSGIServer
import csv

from flask import Flask
from flask import g, request, send_from_directory, json
app = Flask(__name__, static_url_path="")

DATABASE = "database.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def insert_item_in_database(item):
  cursor = get_db().cursor()
  sql = "INSERT INTO Items (itemType, latitude, longitude, _datetime) VALUES (?, ?, ?, ?)"
  values = (item["type"], item["lat"], item["long"], item["datetime"])
  cursor.execute(sql, values)
  get_db().commit()

def get_all_items():
  db = get_db()
  cur = db.cursor()
  sql = "SELECT * FROM Items"
  cur.execute(sql)
  rows = cur.fetchall()
  cur.close()
  return rows
  



@app.route('/')
def hello_world():
  # return "Go home"
  return send_from_directory(".", "geo-test.html")

@app.route("/item", methods=["POST"])
def add_item():
  item = request.get_json()
  insert_item_in_database(item)
  return "item"

@app.route("/get_data", methods=["GET"])
def get_data():
  items = get_all_items()
  return json.dumps(items)

@app.route("/all_data.csv", methods=["GET"])
def get_csv_data():
  items = get_all_items()
  with open("temp.csv", "w") as f:
    wr = csv.writer(f)
    wr.writerows([["type", "latitude", "longitude", "datetime"]])
    wr.writerows(items)
  return send_from_directory(".", "temp.csv")

if __name__ == "__main__":
  # app.run()
  PORT = 5000
  http_server = WSGIServer(('', PORT), app)
  print("serving on port: {}".format(PORT))
  http_server.serve_forever()
