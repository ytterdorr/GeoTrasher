-- drop table if exists Items;
-- drop table if exists Users;
-- drop table if exists UserSessions;

CREATE TABLE IF NOT EXISTS Items(
  itemType varchar,
  latitude varchar,
  longitude varchar, 
  _datetime datetime,
  sessionID int
);

CREATE TABLE IF NOT EXISTS Users(
  userName varchar not null,
  userPass varchar not null,
  token varchar,
  primary key (userName)
);

CREATE TABLE IF NOT EXISTS UserSessions(
  userName varchar,
  sessionID int
);

-- INSERT INTO Items VALUES ("Test", "123456", "1234567", "00-00-00 00-00-00", 1);
