import sqlite3
import os
from flask import g

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
# print(THIS_FOLDER)
########## Database Interaction ############
DATABASE = os.path.join(THIS_FOLDER, "database.db")


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

def add_user(username, password):
  pass

#### Getters ####
def get_from_database(sql, values=[])
  db = get_db()
  cur = db.cursor()
  if len(values) == 0:
    cur.execute(sql)
  else:
    cur.execute(sql, values)
  rows = cur.fetchall()
  return rows

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


##### Checkers #####
def check_token(token):
  cur = get_db().cursor()
  sql = "SELECT * from Users WHERE token=(?)"
  cur.execute(sql, [token])
  found = cur.fetchall()
  print("[check_token] found:", found)
  if len(found) > 0:
    return True
  else: 
    return False