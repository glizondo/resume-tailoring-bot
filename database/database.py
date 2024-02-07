import sqlite3

# connection = sqlite3.connect("resume-bot.db")


def check_user_exists(connection, user_id, user_name):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    rows = cursor.fetchall()
    if rows:
        print("Exists")
        return True
    else:
        print("Does not exist")
        add_user(connection, user_id, user_name)
        return False


# CREATE TABLE
def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, lastname TEXT, "
                   "city TEXT, state TEXT, country TEXT, email TEXT, phone TEXT, linkedin TEXT)")

    cursor.execute('''CREATE TABLE IF NOT EXISTS resumes (resume_id INTEGER PRIMARY KEY, user_id INTEGER,title TEXT, 
    summary TEXT, FOREIGN KEY (user_id) REFERENCES users(user_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS work_experiences (experience_id INTEGER PRIMARY KEY, resume_id 
    INTEGER, company_name TEXT, position TEXT, start_date TEXT, end_date TEXT, description TEXT, FOREIGN KEY (
    resume_id) REFERENCES resumes(resume_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS education (education_id INTEGER PRIMARY KEY, resume_id INTEGER, 
    institution TEXT, degree TEXT, start_date TEXT, end_date TEXT, description TEXT, FOREIGN KEY (resume_id) 
    REFERENCES resumes(resume_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS skills (skill_id INTEGER PRIMARY KEY, resume_id INTEGER, skill_name 
    TEXT, proficiency TEXT, FOREIGN KEY (resume_id) REFERENCES resumes(resume_id))''')

    connection.commit()
    connection.close()


# ADD ELEMENTS TO THE TABLE
def add_user(connection, user_id, name):
    cursor = connection.cursor()
    # cursor.execute(f"INSERT INTO user VALUES ({user_id}, {user_name}, '', '', '', '', '', "
    #                "'', '', '' )")
    cursor.execute(f"INSERT INTO users VALUES ({user_id}, '{name}', 'x', 'x', 'x', 'x', "
                   "'x', 'x', 'x' )")
    print(f'Added user with user_id: {user_id}')
    connection.commit()
    # connection.close()


async def insert_data_user(connection, last_name, city, state, country, email, phone, linkedin, user_id):
    cursor = connection.cursor()
    sql_update_query = f"""UPDATE users SET lastname = ?, city = ?, state = ?, country = ?, email = ?, phone = ?, 
    linkedin = ? WHERE user_id = {user_id}"""
    cursor.execute(sql_update_query, (last_name, city, state, country, email, phone, linkedin))
    connection.commit()
    connection.close()


# GET ELEMENTS FROM TABLE
def get_all_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    connection.commit()
    connection.close()


# DELETE ELEMENTS
def delete_user(connection, user_id):
    cursor = connection.cursor()
    print(f'Deleting {user_id}')
    cursor.execute(f"DELETE FROM users WHERE id={user_id}")
    connection.commit()
    connection.close()


# UPDATE ELEMENTS
# cursor.execute("UPDATE example SET age = 31 WHERE id = 2")

# DROP TABLE
# dropTableStatement = "DROP TABLE user"
# cursor.execute(dropTableStatement)

# add_user(1, 'Luis')
# get_all_users(connection)
# delete_user(connection, 1531227019)

# create_table(connection)
