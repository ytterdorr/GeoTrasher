import flask
import sqlite3
from gevent.pywsgi import WSGIServer
import csv
import io
import os
import bcrypt
import secrets


from flask import Flask
from flask import g, request, make_response, send_file, send_from_directory, json, render_template
# from flask_cors import CORS, cross_origin

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


##### CORS ######
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response



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

    with open(THIS_FOLDER + "/tempfile.csv", "w") as f:
      writer = csv.writer(f)
      writer.writerows(csvList)
    filepath = THIS_FOLDER + "/tempfile.csv"
    return send_file(filepath, attachment_filename=filename, as_attachment=True)

@app.route("/start_session/<username>", methods=["GET"])
def start_session(username):
  if username == "" or username == None:
    username == "Anonymous"
  """ Returns a unique session ID """
  latest_id = dbh.get_latest_sessionID()
  new_id = str(int(latest_id) + 1)
  dbh.register_new_session(new_id)
  dbh.register_user_session(username, new_id)
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
  saltHash = dbh.get_from_database("SELECT salt, hashPass FROM USERS WHERE userName=?", [username])
  print("[Sign in] saltHash:", saltHash)
  if len(saltHash) == 0:
    return json.dumps({"success": False, "message": "Username or Password incorrect", "data":""})
  salt = saltHash[0][0]
  passHash = saltHash[0][1]

  # Check hashing
  if bcrypt.hashpw(password.encode("utf8"), salt) != passHash:
    return json.dumps({"success": False, "message": "Username or Password incorrect", "data":""})


  # Create token
  token = secrets.token_hex(16)
  insertSuccess = dbh.insert_into_database("UPDATE Users SET token=? WHERE userName=?", [token, username])
  if not insertSuccess:
    return json.dumps({"success": False, "message": "Error updating database", "data":""})


  return_obj = {"success": True, "message": "Signing in", "data": token}
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

@app.route("/dump_data", methods=["POST"])
def dump_data():
  """ 
    Takes a json object that looks like this:
    { data: [[type, lat, lng, time, sessionID], ...]}
  """
  data = request.json["data"]
  success = dbh.insert_item_dump(data)
  return json.dumps({"success": success})


""" How do I get this to accept token in headers?"""
@app.route("/user_sessions/<username>/", methods=["GET"])
# @cross_origin(origin='*',headers=['Content-Type','Authorization','Redirect'])
def get_user_sessions(username):
  # Check user auth
  print(request)
  # tokenSuccess = dbh.check_user_token(username, token)
  # if tokenSuccess == False:
  #   return json.dumps({"success": False, "message": "Authorization fail. Get a new token.", "data": []})

  #### Get user data
  receivedData = dbh.get_user_sessions_numbers_and_names(username)
  print (receivedData)

  sendData = []
  for sID, sName in receivedData:
    # Get items
    items = dbh.get_items_by_session_number(sID)

    # Make session name
    sessionName = sName
    if sessionName == None or sessionName == "":
      sessionName = "Session {}".format(sID)

    # Get item count
    itemCountDict = count_items(items)
    print(itemCountDict)

    sendData.append({ "title": sessionName, "data": items, "itemCount": itemCountDict })

  success = True
  return json.dumps({"success": success, "message": "Session Data", "data": sendData})

def count_items(item_list):
  counterDict = {}
  for item in item_list:
    item_type = item[0]
    if item_type not in counterDict:
      counterDict[item_type] = 1
    else:
      counterDict[item_type] += 1
  return counterDict

if __name__ == "__main__":
  # app.run()
  PORT = 5000
  http_server = WSGIServer(('', PORT), app)
  print("serving on port: {}".format(PORT))
  http_server.serve_forever()
