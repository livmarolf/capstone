CREATE TABLE IF NOT EXISTS Users(
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  active INTEGER DEFAULT 1,
  date_created TEXT NOT NULL,
  hire_date TEXT NOT NULL,
  user_type TEXT NOT NULL,
  UNIQUE(email,phone)
);

CREATE TABLE IF NOT EXISTS Competencies(
  competency_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  date_created TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Assessments(
  assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
  competency_id TEXT NOT NULL,
  name TEXT NOT NULL,
  date_created TEXT NOT NULL,
  FOREIGN KEY(competency_id)
    REFERENCES Competencies(competency_id)
);

CREATE TABLE IF NOT EXISTS Assessment_Results(
  assessment_id INTEGER PRIMARY KEY,
  user_id TEXT NOT NULL,
  competency_id TEXT NOT NULL,
  score TEXT NOT NULL,
  date_taken TEXT NOT NULL,
  manager_id TEXT NOT NULL,
  FOREIGN KEY(user_id)
    REFERENCES Users(user_id),
  FOREIGN KEY(assessment_id)
    REFERENCES Assessments(assessment_id),
  FOREIGN KEY(competency_id)
    REFERENCES Assessments(competency_id)
);