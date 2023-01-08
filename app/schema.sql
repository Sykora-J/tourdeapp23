CREATE TABLE IF NOT EXISTS developer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);
INSERT INTO developer (name) values ('John');
CREATE TABLE IF NOT EXISTS devlog (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  work_date TEXT NOT NULL,
  lang TEXT NOT NULL,
  duration INTEGER NOT NULL,
  rating INTEGER NOT NULL,
  note TEXT,
  developer_id INTEGER NOT NULL
);