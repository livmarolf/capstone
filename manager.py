from multiprocessing import connection
import sqlite3
import datetime
import csv
import bcrypt

connection = sqlite3.connect('capstone.db')
cursor = connection.cursor()

class User:

  def __init__(self):
    option = input("Would you like to login or create an account? (L)ogin/(C)reate/(Q)uit: ")
    if option in 'Ll':
      return User.login(self)
    elif option in 'Cc':
      return User.create_user(self)
    elif option in 'Qq':
      return quit()
    else:
      option = input("Would you like to login or create an account? (L)ogin/(C)reate/(Q)uit: ")

  def create_user(self):
    self.first_name = input("Enter first name: ")
    self.last_name = input("Enter last name: ")
    self.phone = input("Enter phone: ")
    self.email = input("Enter email: ")
    self.password = input("Enter password: ")
    hashed_password = User.pass_hash(self, self.password)
    self.date_created = datetime.date.today()
    self.hire_date = datetime.date.today()
    self.user_type = input("Enter user type (U)ser/(M)anager: ").upper()

    sql_statement = "INSERT INTO Users (first_name, last_name, phone, email, password, date_created, hire_date, user_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    values = self.first_name, self.last_name, self.phone, self.email, hashed_password, self.date_created, self.hire_date, self.user_type
    cursor.execute(sql_statement, values)
    connection.commit()

    print("Successful. Please Login now.")
    return self.login()

  def pass_hash(self, password):
    salt = bcrypt.gensalt()
    bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(bytes, salt)
    return hashed

  def restart(self):
    option = input("Continue to other options or quit? (C)ontinue/(Q)uit: ")
    if option in 'Cc':
      return self.show_actions_user()
    elif option in 'Qq':
      return quit()
    else:
      print("Value entered is not an option...")
      self.restart()

  def email_in_use(self, email):
    sql_statement = "SELECT email FROM Users"
    email_list = cursor.execute(sql_statement).fetchall()
    emails = []
    for e in email_list:
      emails.append(e[0])
    if email in emails:
      print("Email taken.")
      return False
    else:
      return True

  def write_csv_avg(self, header, data):
    with open('comp_avg.csv', 'w', encoding='UTF8') as f:
      writer = csv.writer(f)
      writer.writerow(header)
      for row in data:
        writer.writerow(row)
    return

  def write_csv_assess(self, header, data):
    with open('assessments.csv', 'w', encoding='UTF8') as f:
      writer = csv.writer(f)
      writer.writerow(header)
      for row in data:
        writer.writerow(row)
    return

  def view_assessments(self):
    sql_statement = """
      SELECT DISTINCT assessment_id, c.name, a.name
      FROM Assessments a, Competencies c
      JOIN Competencies
      ON a.competency_id = c.competency_id
    """
    assessments = cursor.execute(sql_statement).fetchall()
    print(f'{"Assessment ID":<16} {"Competency":<22} {"Name/Des"}')
    for assessment in assessments:
      print(f"{assessment[0]:<15}{assessment[1][:20]:<22}{assessment[2]}")
    return

  def login(self):
    email = input("Enter email: ")
    password = input("Enter password: ")
    sql_statement = "SELECT user_id, email, password, user_type FROM Users WHERE email = ?"
    fetched_user = cursor.execute(sql_statement, (email,)).fetchone()
    if fetched_user == None:
      print("Not found")
      option = input("Try again? (y/n): ")
      if option in 'Yy':
        return User.login(self)
      else:
        return quit()
    elif bcrypt.checkpw(password.encode('utf-8'), fetched_user[2]):
      self.user_type = fetched_user[3]
      self.user_id = fetched_user[0]
      if self.user_type == "M":
        Manager.show_actions_manager(self)
      print("Successful login.")
      return self.show_actions_user()
    else:
      print("Something you answered was incorrect.")
      option = input("Try again? (y/n): ")
      if option in 'Yy':
        return User.login(self)
      else:
        return quit()
  
  def show_actions_user(self):
    print("1. View my assessments and scores \n2. Edit my information \n3. My competencies \n4. Average competency score \n5. Read a CSV \n(Q)uit")
    selection = input("Enter number of preferable option here: ")
    if selection == "1":
      return self.view_my_assessments()
    elif selection == "2":
      return self.edit_user_info()
    elif selection == "3":
      return self.view_competencies()
    elif selection == "4":
      return self.view_avg_competency()
    elif selection == "5":
      return self.read_csv_assess_res()
    elif selection in 'Qq':
      return exit()
    else:
      self.show_actions_user()
  
  def view_my_assessments(self):
    sql_statement = """
    SELECT ar.user_id, (u.first_name || " " || u.last_name), a.name, ar.score
    FROM Assessment_Results ar
    JOIN Users u 
    ON  ar.user_id = u.user_id
    JOIN Assessments a
    ON a.assessment_id = ar.assessment_id
    WHERE u.user_id = ?
    """
    assessments = cursor.execute(sql_statement, (self.user_id,)).fetchall()
    print("User ID   User Name            Assessment Name                Score")
    for assess in assessments:
      print(f"{assess[0]:<10} {assess[1]:<20} {assess[2]:<30} {assess[3]}")
    write = input("Write this to a csv? (y/n): ")
    if write in 'Yy':
      headers = ["User ID", "User Name", "Assessment Name", "Score"]
      self.write_csv_assess(headers, assessments)
      print("Done \u2713")
      return self.restart()
    else:
      return self.restart()

  def edit_user_info(self, user_id):
    sql_statement = """
      SELECT first_name, last_name, phone, email, password
      FROM Users
      WHERE user_id = ?
    """
    info = cursor.execute(sql_statement, (user_id,)).fetchone()
    print(f"(1)First Name: {info[0]}")
    print(f"(2)Last Name: {info[1]}")
    print(f"(3)Email: {info[2]}")
    print(f"(4)Phone: {info[3]}")
    print(f"(5)Password: {info[4]}")

    option = input("Select number of field you want to change: ")
    if option == "1":
      new = input("Enter new first name: ")
      sql_statement = """
        UPDATE Users
        SET first_name = ?
        WHERE user_id = ?
      """
      cursor.execute(sql_statement, (new, user_id,))
      print("Success \u2713")
    elif option == "2":
      new = input("Enter new last name: ")
      sql_statement = """
        UPDATE Users 
        SET last_name = ?
        WHERE user_id = ?
      """
      cursor.execute(sql_statement, (new, user_id,))
      print("Success \u2713")
    elif option == "3":
      new = input("Enter new email: ")
      while self.email_in_use(new) == False:
        new = input("Enter a different email: ")
      sql_statement = """
        UPDATE Users
        SET email = ?
        WHERE user_id = ?
      """
      cursor.execute(sql_statement, (new, user_id,))
    elif option == "4":
      new = input("Enter new phone: ")
      sql_statement = """
        UPDATE Users 
        SET phone = ?
        WHERE user_id = ?
      """
      cursor.execute(sql_statement, (new, user_id,))
      print("Success \u2713")
    elif option == "5":
      old_pass = input("Enter old password: ")
      sql_statement = """
        SELECT password
        FROM Users
        WHERE user_id = ?
      """
      old_hashed = cursor.execute(sql_statement, (user_id,)).fetchone()
      if bcrypt.checkpw(old_pass.encode('utf-8'), old_hashed[0]):
        new_pass = input("Enter new password: ")
        new_hashed = User.pass_hash(self, new_pass)
        sql_statement = """
          UPDATE Users
          SET password = ?
          WHERE user_id = ?
        """
        cursor.execute(sql_statement, (new_hashed, user_id,))
        print("Success \u2713")
      else:
        print("Password incorrect")
    connection.commit()
    return self.restart()

  def view_competencies(self):
    sql_statement = """
      SELECT competency_id, name
      FROM Competencies
    """
    competencies = cursor.execute(sql_statement).fetchall()
    print(f'{"Comp ID":<16} {"Name"}')
    for comp in competencies:
      print(f'{comp[0]:<16} {comp[1]}')
    return

  def view_avg_competency(self):
    sql_statement = """
      SELECT ar.competency_id, c.name, AVG(ar.score)
      FROM Competencies c, Assessment_Results ar
      WHERE ar.user_id = ?
      AND c.competency_id = ar.competency_id
      GROUP BY ar.competency_id
    """
    average = cursor.execute(sql_statement, (self.user_id,)).fetchall()
    print(f'{"Comp ID":<16} {"Name/Des":<24} {"Avg of all assessments"}')
    for avg in average:
      print(f'{avg[0]:<16} {avg[1]:<24} {avg[2]}')
    write = input("Write to a csv? (y)/(n): ")
    if write in 'Yy':
      headers = ["Comp ID", "Name/Des", "Avg of all assessments"]
      self.write_csv_avg(headers, average)
      print("Successfully written.")
      return self.restart()
    else:
      return self.restart()

  def read_csv_assess_res(self):
    print("File must have 4 columns.\n")
    file = input("Enter file name to read. Include .csv. ex'filename.csv' Enter here: ")
    with open(file, 'r') as csv:
      data = csv.readlines()
      for row in data:
        row = row.split(',')
        print(f"{row[0]:<20}{row[1]:<20}{row[2]:<30}{row[3]}")
    return self.restart()

class Manager(User):
  def restart_m(self):
    option = input("Continue to other options or quit? (C)ontinue/(Q)uit: ")
    if option in 'Cc':
      return self.show_actions_manager()
    elif option in 'Qq':
      return quit()
    else:
      print("Value entered is not an option...")
      self.restart_m()

  def write_csv_assess(self, header, data):
    with open('assessments.csv', 'w', encoding='UTF8') as f:
      writer = csv.writer(f)
      writer.writerow(header)
      for row in data:
        writer.writerow(row)
    return

  def show_actions_manager(self):
    print("""
    A manager can interact with users and competencies.
    They can perform specific actions on each.
    (1)Users
    (2)Competencies
    (Q)uit
    """)
    choice = input("Select the number of which one you would like to access: ")
    if choice == "1":
      return self.view_act_u()
    elif choice == "2":
      return self.view_act_comp()
    elif choice in 'Qq':
      return quit()
    else:
      print("What you entered was not an option.")
      choice = input("Select the number of which one you would like to access: ")

  def view_act_u(self):
    print("""
    (1) Create a new User/Manager
    (2) View all users
    (3) Search for a user by name
    (Q)uit
    """)
    option = input("Select an option from above. Enter here: ")
    if option == "1":
      return self.add_um()
    elif option == "2":
      return self.view_users()
    elif option == "3":
      return self.search()
    elif option in 'Qq':
      return quit()
    else:
      self.view_act_u()

  def add_um(self):
    self.first_name = input("Enter first name: ")
    self.last_name = input("Enter last name: ")
    self.email = input("Enter email: ")
    while User.email_in_use(self, self.email) == False:
      self.email = input("\nEnter a different email. Enter: ")
    self.password = input("Enter password: ")
    hashed_password = User.pass_hash(self, self.password)
    self.phone = input("Enter phone number: ")
    date_created = datetime.date.today()
    hire_date = datetime.date.today()
    user_type = input("Enter user type (user/manager). Enter: ").upper()
    sql_statement = """
        INSERT INTO Users (
            first_name, last_name, email, password, phone, date_created, hire_date, user_type
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?
        )
    """
    values = self.first_name, self.last_name, self.email, hashed_password, self.phone, date_created, hire_date, user_type
    cursor.execute(sql_statement, values)
    connection.commit()
    print("\nAccount created successfully.")
    return self.restart_m()

  def view_users(self):
    sql_statement = """
      SELECT user_id, first_name, last_name, phone, email
      FROM Users
    """
    users = cursor.execute(sql_statement).fetchall()
    print(f'{"User ID":<10} {"First":<16} {"Last":<16} {"Phone":<12} {"Email"}')
    for user in users:
      print(f"{user[0]:<9} {user[1]:<16} {user[2]:<16} {user[3]:<12} {user[4]}")
    return self.perform_act_on_u()

  def search(self):
    search = input("Enter name to search: ")
    sql_statement = """
      SELECT user_id, first_name, last_name, phone, email FROM Users
      WHERE first_name LIKE ('%' || ? || '%')
      OR last_name LIKE ('%' || ? || '%')
    """
    found_users = cursor.execute(sql_statement, (search, search,)).fetchall()
    print(f'{"User ID":<10} {"First":<16} {"Last":16} {"Phone":<12} {"Email"}')
    for user in found_users:
      print(f"{user[0]:<9} {user[1]:<16} {user[2]:<16} {user[3]:<12} {user[4]}")
    return self.perform_act_on_u()

  def perform_act_on_u(self):
    user_id = input("Enter user ID to perform action on: ")
    print("""
    (1) Edit user
    (2) View assessments and competencies for user
    (3) Give use a score
    (4) Delete a user
    (5) Main menu
    (Q)uit
    """)
    option = input("Select a number from above: ")
    if option == "1":
      return User.edit_user_info(self, user_id)
    elif option == "2":
      return self.view_all_u_assess()
    elif option == "3":
      self.give_score(user_id)
      return
    elif option == "4":
      return self.delete_user(user_id)
    elif option == "5":
      return self.show_actions_manager()
    elif option in 'Qq':
      return quit()
    else:
      return self.perform_act_on_u()

  def view_all_u_assess(self):
    sql_statement = """
    SELECT ar.user_id, (u.first_name || " " || u.last_name), a.name, ar.score
    FROM Assessment_Results ar
    JOIN Users u 
    ON  ar.user_id = u.user_id
    JOIN Assessments a
    ON a.assessment_id = ar.assessment_id
    """
    assessments = cursor.execute(sql_statement).fetchall()
    print(f'{"User ID":<10} {"Name":<20} {"Assessment name":<30} {"Score":<10}')
    for assessment in assessments:
      print(f"{assessment[0]:<10} {assessment[1]:<20} {assessment[2][:28]:<30} {assessment[3]}")
    write = input("Would you like to write this to csv? (y)/(n): ")
    if write in 'Yy':
      headers = ["User ID", "Name", "Assessment Name", "Score"]
      self.write_csv_assess(headers, assessments)
      print("Wrote successfully")
      return self.restart()
    else:
      self.restart_m()

  def give_score(self, user_id):
    User.view_competencies(self)
    comp = input("Choose a competency ID to view assessments: ")
    self.view_assessments_comp(comp)
    assessment = input("Select assessment ID to give score: ")
    score = input("Enter a score for this assessment (0-5): ")
    date_taken = datetime.date.today()
    sql_statement = """
      SELECT competency_id FROM Assessments
      WHERE assessment_id = ?
    """
    comp_id = cursor.execute(sql_statement, (assessment,)).fetchone()
    second_sql = """
      INSERT INTO Assessment_Results (assessment_id, user_id, competency_id, score, date_taken, manager_id)
      VALUES (?, ?, ?, ?, ?, ?)
    """
    values = assessment, user_id, comp_id[0], score, date_taken, self.user_id
    cursor.execute(second_sql, values)
    connection.commit()
    print("Success. Score updated.")
    return self.restart_m()
    
  def view_assessments_comp(self, competency_id):
    sql_statement = """
      SELECT DISTINCT assessment_id, c.name, a.name
      FROM Assessments a, Competencies c
      JOIN Competencies
      ON a.competency_id = c.competency_id
      WHERE c.competency_id = ?
    """
    assessments = cursor.execute(sql_statement, (competency_id,)).fetchall()
    print(f'{"Assessment id":<16} {"Competency":<20} {"Name/Des"}')
    for assessment in assessments:
      print(f"{assessment[0]:<16}{assessment[1]:<20}{assessment[2]}")
    return

  def delete_user(self, user_id):
    option = input("Would you like to (1)Deactivate user or (2)Delete completely? ")
    if option == "1":
      sql_statement = """
      UPDATE Users 
      SET active = 0
      WHERE user_id = ?
      """
      cursor.execute(sql_statement, (user_id,))
      connection.commit()
      print("Successfully deactivated.")
    elif option == "2":
      second_sql = """
      DELETE FROM User
      WHERE user_id = ?
      """
      cursor.execute(second_sql, (user_id,))
      connection.commit()
      print("Successfully deleted.")
    else:
      print("That entry is not acceptable.")
      return self.delete_user()


  def view_act_comp(self):
    print("""
    (1) Create a competency
    (2) Edit competencies
    (3) Delete a competency
    (4) Create an assessment
    (5) Edit assessments
    (6) Delete an assessment
    (Q)uit
    """)
    option = input("Enter a selection from above: ")
    if option == "1":
      return self.create_comp()
    elif option == "2":
      return self.edit_comp()
    elif option == "3":
      return self.delete_comp()
    elif option == "4":
      return self.create_assess()
    elif option == "5":
      return self.edit_assess()
    elif option == "6":
      return self.delete_assess()
    elif option in 'Qq':
      return quit()
    else:
      return self.view_act_comp()

  def create_comp(self):
    new_comp = input("Enter the name of the competency you'd like to create: ")
    date_created = datetime.date.today()
    date = date_created
    sql_statement = """
    INSERT INTO Competencies (name, date_created)
    VALUES (?, ?)
    """
    cursor.execute(sql_statement, (new_comp, date,))
    connection.commit()
    print("Competency has been created.")
    return self.restart_m()

  def edit_comp(self):
    User.view_competencies(self)
    selection = input("Select the id of the competency you would like to edit: ")
    edit = input("Enter the new name/description for the Name field: ")
    sql_statement = """
    UPDATE Competencies 
    SET name = ?
    WHERE competency_id = ?
    """
    values = edit, selection
    cursor.execute(sql_statement, values)
    connection.commit()
    print("Edit successful.")
    return self.restart_m()

  def delete_comp(self):
    self.view_competencies()
    selection = input("Enter the id of the competency you would like to delete: ")
    sql_statement = """
    DELETE FROM Competencies
    WHERE competency_id = ?
    """

    second_sql = """
    UPDATE Assessments
    SET competency_id = 'Deleted'
    WHERE competency_id = ?
    """

    third_sql = """
    UPDATE Assessment_Results
    SET competency_id = 'Deleted'
    WHERE competency_id = ?
    """
    cursor.execute(sql_statement, (selection,))
    cursor.execute(second_sql, (selection,))
    cursor.execute(third_sql, (selection,))
    connection.commit()
    print("Competency Deleted.")
    return self.restart_m()

  def create_assess(self):
    User.view_competencies(self)
    competency = input("Choose the competency ID associated with this assessment: ")
    assess_name = input("Enter a name for this assessment: ")
    date_created = datetime.date.today()
    sql_statement = """
      INSERT INTO Assessments (competency_id, name, date_created)
      VALUES (?, ?, ?)
    """
    values = competency, assess_name, date_created
    cursor.execute(sql_statement, values)
    connection.commit()
    print("Assessment created.")
    return self.restart_m()

  def edit_assess(self):
    User.view_assessments()
    assessment = input("Choose an assessment ID to edit: ")
    new_name = input("Enter a new name/Description: ")
    sql_statement = """
      UPDATE Assessments
      SET name = ?
      WHERE assessment_id = ?
    """
    values = new_name, assessment
    cursor.execute(sql_statement, values)
    connection.commit()
    print("Successfully changed.")
    return self.restart_m()

  def delete_assess(self):
    self.view_assessments()
    assessment = input("Choose an assessment to delete. Enter ID here: ")
    sql_statement = """
      DELETE FROM Assessments
      WHERE assessment_id = ?
    """
    second_sql = """
      UPDATE Assessment_Results
      SET assessment_id = 'Deleted'
      WHERE assessment_id = ?
    """
    cursor.execute(sql_statement, (assessment,))
    cursor.execute(second_sql, (assessment,))
    connection.commit()
    print("Deleted.")
    return self.restart_m()


Liv = Manager()
connection.commit()