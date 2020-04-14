
import argparse
import os.path
import sqlite3
import csv

def insert_row_in_db(row, db):
  cur = db.cursor
  if len(row) == 5:
    sql = "Insert into Items ()

def main(csv_file, db_url):


  # Initialize database
  db = sqlite3.connect(db_url)
  # Read data
  with open(csv_file, newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
      if row[0] == "type":
        continue
      






if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--file", dest="input_file", help="Input file, csv")
  parser.add_argument("--database", dest="db_url", help="database url")
  args = parser.parse_args()
  inf = args.input_file
  db_url = args.db_url
  main(inf, db_url)