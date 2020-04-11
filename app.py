import flask
import sqlite3
from gevent.pywsgi import WSGIServer
import csv
import io
import os

from flask import Flask
from flask import g, request, make_response, send_file, send_from_directory, json, render_template
app = Flask(__name__, static_url_path="")

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(THIS_FOLDER)
########## Database Interaction ############
DATABASE = os.path.join(THIS_FOLDER, "database.db")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        print("Using database", DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def insert_item_in_database(item):
  cursor = get_db().cursor()
  if "sessionID" in item.keys():
    sql = "INSERT INTO Items (itemType, latitude, longitude, _datetime, sessionID) VALUES (?, ?, ?, ?, ?)"
    values = (item["type"], item["lat"], item["long"], item["datetime"], item["sessionID"])
  else:
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

def get_session_data(sessionID): 
  db = get_db()
  cur = db.cursor()
  sql = "SELECT * FROM Items WHERE sessionID=?"
  cur.execute(sql, [sessionID])
  rows = cur.fetchall()
  return rows
  
def get_latest_sessionID():
  cur = get_db().cursor()
  sql = "SELECT MAX(sessionID) from Items"
  cur.execute(sql)
  maxID = cur.fetchall()[0][0]
  return maxID


##### CORS ######

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response

app.after_request(add_cors_headers)




##### Routing ######

@app.route('/')
def hello_world():
  # return "Go home"
  return render_template("geo-test.html")

@app.route("/session")
def session():
  return render_template("session.html")

@app.route("/item", methods=["POST"])
def add_item():
  item = request.get_json()
  insert_item_in_database(item)
  return "item"

@app.route("/get_data", methods=["GET"])
def get_data():
  items = get_all_items()
  return json.dumps(items)

# @app.route("/csv_data", methods=["GET"])
# def get_csv_data():
#   items = get_all_items()
#   print(items)
#   with open("temp.csv", "w") as f:
#     f.truncate(0)
#     wr = csv.writer(f)
#     wr.writerows([["type", "latitude", "longitude", "datetime"]])
#     wr.writerows(items)
#   return send_file("temp.csv", mimetype="text/csv")

@app.route('/download/<sessionID>')
def download(sessionID):
    """
    To download the whole dataset as a csv file
    
    If sessionID is given, should return only specific session data
    otherwise returns full Item database. 

    """ 
    if int(sessionID) > 0:
      items = get_session_data(sessionID)
    else: 
      items = get_all_items()
    # Prepare csv file
    columns = [["type", "latitude", "longitude", "datetime", "sessionID"]]
    csvList = columns + items
    # si = io.StringIO()
    # cw = csv.writer(si)
    # cw.writerows(csvList)
    # output = make_response(si.getvalue())
    # output.headers["Content-Disposition"] = "attachment; filename=trash_geodata.csv"
    # output.headers["Content-type"] = "text/csv"
    # return output

    with open("tempfile.csv", "w") as f:
      writer = csv.writer(f)
      writer.writerows(csvList)
    filepath = THIS_FOLDER + "/tempfile.csv"
    return send_file(filepath, attachment_filename="testName.csv", as_attachment=True)

@app.route('/download_with_filename/<sessionID>/<filename>')
def download_with_filename(sessionID, filename):
    """
    To download the whole dataset as a csv file
    
    If sessionID is given, should return only specific session data
    otherwise returns full Item database. 

    """ 
    if int(sessionID) > 0:
      items = get_session_data(sessionID)
    else: 
      items = get_all_items()
    # Prepare csv file
    columns = [["type", "latitude", "longitude", "datetime", "sessionID"]]
    csvList = columns + items

    with open("tempfile.csv", "w") as f:
      writer = csv.writer(f)
      writer.writerows(csvList)
    filepath = THIS_FOLDER + "/tempfile.csv"
    return send_file(filepath, attachment_filename=filename, as_attachment=True)

@app.route("/start_session", methods=["GET"])
def start_session():
  """ Returns a unique session ID """
  latest_id = get_latest_sessionID()
  new_id = str(int(latest_id) + 1)
  print("latest_id", latest_id)

  return new_id

@app.route("/get_session_items/<sessionID>")
def get_session_items(sessionID):
  if sessionID == 0:
    session_data = get_all_items()
  else:
    session_data = get_session_data(sessionID)
  # session_data = get_session_data(sessionID)
  return json.dumps(session_data)

@app.route("/get_session_item_count/<sessionID>")
def get_session_item_count(sessionID):
  if sessionID == "0":
    print("SessionID: 0")
    session_data = get_all_items()
  else:
    session_data = get_session_data(sessionID)
  # Count items of types
  items = {"Nikotin": 0, "Annat": 0}
  for item in session_data:
    itemType = item[0]
    if itemType not in items.keys():
      items[itemType] = 1
    else:
      items[itemType] += 1
  print(items)
  return(items)



if __name__ == "__main__":
  # app.run()
  PORT = 5000
  http_server = WSGIServer(('', PORT), app)
  print("serving on port: {}".format(PORT))
  http_server.serve_forever()
