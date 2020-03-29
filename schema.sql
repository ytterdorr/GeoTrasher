drop table if exists Items;

CREATE TABLE Items(
  itemType varchar,
  latitude varchar,
  longitude varchar, 
  _datetime datetime,
  sessionID int
);

INSERT INTO Items VALUES ("Test", "123456", "1234567", "00-00-00 00-00-00", 1);