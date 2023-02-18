CREATE TABLE IF NOT EXISTS developer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fname TEXT NOT NULL,
  lname TEXT NOT NULL,
  username TEXT NOT NULL UNIQUE,
  mail TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  bool_admin INTEGER NOT NULL
);
INSERT INTO developer (fname, lname, username, mail, password, bool_admin)
    VALUES ('John', 'Doe', 'admin', 'admin@gmail.com', '123456', 1);
CREATE TABLE IF NOT EXISTS devlog (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  work_date TEXT NOT NULL,
  lang TEXT NOT NULL,
  duration INTEGER NOT NULL,
  rating INTEGER NOT NULL,
  note TEXT,
  developer_id INTEGER NOT NULL
);
INSERT INTO devlog (work_date, lang, duration, rating, note, developer_id) VALUES ('2023-02-18', 'Python', 60, 5, 'First log note', 1);
INSERT INTO devlog (work_date, lang, duration, rating, note, developer_id) VALUES ('2023-02-17', 'Java', 120, 3, 'Second log note', 1);
INSERT INTO devlog (work_date, lang, duration, rating, note, developer_id) VALUES ('2023-01-18', 'C++', 600, 1, '', 1);