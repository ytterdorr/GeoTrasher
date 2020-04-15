import flask
import sqlite3
from gevent.pywsgi import WSGIServer
import csv
import io
import os
import bcrypt


from flask import Flask
from flask import g, request, make_response, send_file, send_from_directory, json, render_template
import database_helper as dbh



app = Flask(__name__, static_url_path="")

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
# print(THIS_FOLDER)
# ########## Database Interaction ############
# DATABASE = os.path.join(THIS_FOLDER, "database.db")

@app.before_request
def before_request():
  dbh.connect_db()

@app.teardown_request
def teardown_request(exception): 
  dbh.close_db()

@app.teardown_appcontext
def close_connection(exception):
  dbh.close_db()


# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

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
  dbh.insert_item_in_database(item)
  return "item"

@app.route("/get_data", methods=["GET"])
def get_data():
  items = dbh.get_all_items()
  return json.dumps(items)


@app.route('/download/<sessionID>')
def download(sessionID):
    """
    To download the whole dataset as a csv file
    
    If sessionID is given, should return only specific session data
    otherwise returns full Item database. 

    """ 
    if int(sessionID) > 0:
      items = dbh.get_session_data(sessionID)
    else: 
      items = dbh.get_all_items()
    # Prepare csv file
    columns = [["type", "latitude", "longitude", "datetime", "sessionID"]]
    csvList = columns + items

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
      items = dbh.get_session_data(sessionID)
    else: 
      items = dbh.get_all_items()
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
  latest_id = dbh.get_latest_sessionID()
  new_id = str(int(latest_id) + 1)
  print("latest_id", latest_id)

  return new_id

@app.route("/get_session_items/<sessionID>")
def get_session_items(sessionID):
  if sessionID == 0:
    session_data = dbh.get_all_items()
  else:
    session_data = dbh.get_session_data(sessionID)
  return json.dumps(session_data)

@app.route("/get_session_item_count/<sessionID>")
def get_session_item_count(sessionID):
  if sessionID == "0":
    print("SessionID: 0")
    session_data = dbh.get_all_items()
  else:
    session_data = dbh.get_session_data(sessionID)
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

#### user stuff

def check_if_user_exists(username):
  dbh.get_user_by_username(username)
  pass

@app.route("/sign_in", methods=["POST"])
def sign_in():
  return_obj = {"success": False, "message": "Something went wrong", "data": ""}
  
  # Get userdata/check if user exists
  username = request.json["username"]
  password = request.json["password"]

  # Check none of them is empty
  fieldEmpty = (username == "") or (password == "")
  if fieldEmpty:
    return json.dumps({"success": False, "message": "Please fill in both username and password", "data": ""})
  
  # Check if user exists, get salt
  saltHash = dbh.get_from_database("SELECT salt, hashPass FROM USERS WHERE userName=?", [username])[0]
  print("[Sign in] saltHash:", saltHash)
  if len(saltHash) == 0:
    return json.dumps({"success": False, "message": "Username or Password incorrect", "data":""})
  salt = saltHash[0]
  passHash = saltHash[1]
  
  # Check hashing
  if bcrypt.hashpw(password.encode("utf8"), salt) != passHash:
    return json.dumps({"success": False, "message": "Username or Password incorrect", "data":""})

  return_obj = {"success": True, "message": "Signing in", "data": "TODO_RANDOM_TOKEN"}
  return json.dumps(return_obj)
    

@app.route("/sign_up", methods=["POST"])
def sign_up():
  # Get user input
  username = request.json["username"]
  password = request.json["password"]

  # Check none of them is empty
  fieldEmpty = (username == "") or (password == "")
  if fieldEmpty:
    return json.dumps({"success": False, "message": "Please fill in both username and password", "data": ""})
  
  # Check user does not already exist
  if dbh.check_user_exists(username):
    return json.dumps({"success": False, "message": "User '{}' already exists".format(username), "data": ""})

  # All is well, encrypt and store
  salt = bcrypt.gensalt()
  hashPwd = bcrypt.hashpw(password.encode('utf8'), salt)

  successful_add = dbh.add_user(username, salt, hashPwd)
  if not successful_add:
    return json.dumps({"success": False, "message": "error when storing new user", "data": ""})

  return_obj = {"success": True, "message": "sign Up", "data":""}
  return json.dumps(return_obj)


if __name__ == "__main__":
  # app.run()
  PORT = 5000
  http_server = WSGIServer(('', PORT), app)
  print("serving on port: {}".format(PORT))
  http_server.serve_forever()
