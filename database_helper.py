import sqlite3
import os
from flask import g

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
# print(THIS_FOLDER)
########## Database Interaction ############
DATABASE = os.path.join(THIS_FOLDER, "database.db")
# DATABASE = os.path.join(THIS_FOLDER, "Experiments/pyany_database.db")


def connect_db():
    g.db = sqlite3.connect(DATABASE)


def close_db():
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        print("Using database", DATABASE)
    return db



#### Inserters ####

def insert_into_database(sql, values=[]):
  try:
    cursor = get_db().cursor()
    if len(values) == 0:
      cursor.execute(sql)
    else:
      cursor.execute(sql, values)
    get_db().commit()
    return True
  except Exception as e:
    print(e)
    return False

def insert_item_in_database(item):
  try:
    cursor = get_db().cursor()
    if "sessionID" in item.keys():
      sql = "INSERT INTO Items (itemType, latitude, longitude, _datetime, sessionID) VALUES (?, ?, ?, ?, ?)"
      values = (item["type"], item["lat"], item["long"], item["datetime"], item["sessionID"])
    else:
      sql = "INSERT INTO Items (itemType, latitude, longitude, _datetime) VALUES (?, ?, ?, ?)"
      values = (item["type"], item["lat"], item["long"], item["datetime"])
    cursor.execute(sql, values)
    get_db().commit()
    return True
  except Exception as e:
    print(e)
    return False

def register_new_session(new_id):
  success =  insert_into_database("INSERT INTO Items (itemType, sessionID) VALUES (?, ?)", ["New Session", new_id])
  return success

def register_user_session(username, session_id):
  success = insert_into_database("INSERT INTO UserSessions (userName, sessionID) VALUES (?,?)", [username, session_id])

def add_user(username, salt, hashPass):
  success = insert_into_database("INSERT INTO Users (userName, salt, hashPass) VALUES (?, ?, ?)", [username, salt, hashPass])
  return success

def insert_item_dump(itemList):
  """ 
  Insert a big list of items
  Each item is itself a list
  [type, lat, lng, datetime, sessionID]
  """
  print("[dhb insert dump]: Received data:", itemList)
  try:
    cursor = get_db().cursor()
    sql = "INSERT INTO Items (itemType, latitude, longitude, _datetime, sessionID) VALUES (?,?,?,?,?)"
    for item in itemList:
      cursor.execute(sql, item)
    get_db().commit()
    return True
  except Exception as e:
    print(e)
    return False

def update_session_name(sessionID, newName):
  success = insert_into_database("UPDATE UserSessions SET sessionName=? WHERE sessionID=?", [newName, sessionID])
  return success

#### Getters ####
def get_from_database(sql, values=[]):
  try:
    db = get_db()
    cur = db.cursor()
    if len(values) == 0:
      cur.execute(sql)
    else:
      cur.execute(sql, values)
    rows = cur.fetchall()
    return rows
  except Exception as e:
    print(e)

def get_user_by_username(username):
  rows = get_from_database("SELECT * FROM Users WHERE username=?", [username])
  print("[get_user] userData:", rows)
  return rows

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

def get_user_sessions_numbers_and_names(username):
  rows = get_from_database("SELECT sessionID, sessionName FROM UserSessions WHERE userName=?", [username])
  return rows

def get_items_by_session_number(sessionID):
  items = get_from_database("SELECT * FROM Items WHERE sessionID=?", [sessionID])
  return items


##### Checkers #####
def check_user_token(username, token):
  cur = get_db().cursor()
  sql = "SELECT * from Users WHERE token=(?)"
  cur.execute(sql, [token])
  found = cur.fetchall()
  print("[check_token] found:", found)
  if len(found) > 0:
    return True
  else: 
    return False

def check_user_exists(username):
  rows = get_from_database("SELECT userName FROM Users WHERE username=?", [username])
  if len(rows) > 0:
    return True
  else:
    return False