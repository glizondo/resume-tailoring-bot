import sqlite3

connection = sqlite3.connect("resume-bot.db")


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

    cursor.execute('''CREATE TABLE IF NOT EXISTS resumes (resume_id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, 
    FOREIGN KEY (user_id) REFERENCES users(user_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS work_experiences (experience_id INTEGER PRIMARY KEY, resume_id 
    INTEGER, description TEXT, FOREIGN KEY (
    resume_id) REFERENCES resumes(resume_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS education (education_id INTEGER PRIMARY KEY, resume_id INTEGER, 
    description TEXT, FOREIGN KEY (resume_id) REFERENCES resumes(resume_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS skills (skill_id INTEGER PRIMARY KEY, resume_id INTEGER, description 
    TEXT, FOREIGN KEY (resume_id) REFERENCES resumes(resume_id))''')

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


def add_resume(connection, user_id):
    cursor = connection.cursor()
    sql = '''INSERT INTO resumes (user_id, title)
                 VALUES (?, ?)'''
    cursor.execute(sql, (user_id, "resume"))
    print(f'Added resume to user_id: {user_id}')
    connection.commit()
    print(f'Resume_id: {cursor.lastrowid}')
    return cursor.lastrowid


def add_education(connection, resume_id, description):
    cursor = connection.cursor()
    sql = '''INSERT INTO education (resume_id, description)
                 VALUES (?, ?)'''
    cursor.execute(sql, (resume_id, description))
    print(f'Added education in resume_id: {resume_id}')
    connection.commit()


def add_work_experience(connection, resume_id, description):
    cursor = connection.cursor()
    sql = '''INSERT INTO work_experiences (resume_id, description)
             VALUES (?, ?)'''
    cursor.execute(sql, (resume_id, description))
    print(f'Added experience in resume_id: {resume_id}')
    connection.commit()


def add_skill(connection, resume_id, description):
    cursor = connection.cursor()
    sql = '''INSERT INTO skills (resume_id, description)
             VALUES (?, ?)'''
    cursor.execute(sql, (resume_id, description))
    print(f'Added skill in resume_id: {resume_id}')
    connection.commit()


async def insert_data_user(connection, last_name, city, state, country, email, phone, linkedin, user_id):
    cursor = connection.cursor()
    sql_update_query = f"""UPDATE users SET lastname = ?, city = ?, state = ?, country = ?, email = ?, phone = ?, 
    linkedin = ? WHERE user_id = {user_id}"""
    cursor.execute(sql_update_query, (last_name, city, state, country, email, phone, linkedin))
    connection.commit()


# GET ELEMENTS FROM TABLE
def get_all_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    connection.commit()


# DELETE ELEMENTS
def delete_user(connection, user_id):
    cursor = connection.cursor()
    print(f'Deleting {user_id}')
    cursor.execute(f"DELETE FROM users WHERE id={user_id}")
    connection.commit()
    connection.close()


def get_user_by_id(connection, user_id):
    cursor = connection.cursor()
    sql = "SELECT * FROM users WHERE user_id = ?"
    cursor.execute(sql, (user_id,))
    user = cursor.fetchone()
    connection.commit()
    return user


def get_resume_details(connection, resume_id):
    cursor = connection.cursor()

    cursor.execute('''SELECT title FROM resumes WHERE resume_id = ?''', (resume_id,))
    resume = cursor.fetchone()
    if resume:
        print("Resume Title:", resume[0])
        print("Resume Id: ", resume_id)
    else:
        print("Resume not found.")
        return

    cursor.execute('''SELECT description FROM work_experiences WHERE resume_id = ?''', (resume_id,))
    work_experiences = cursor.fetchall()
    print("\nWork Experiences:")
    for experience in work_experiences:
        print(">", experience[0])

    cursor.execute('''SELECT description FROM education WHERE resume_id = ?''', (resume_id,))
    educations = cursor.fetchall()
    print("\nEducation:")
    for education in educations:
        print(">", education[0])

    cursor.execute('''SELECT description FROM skills WHERE resume_id = ?''', (resume_id,))
    skills = cursor.fetchall()
    print("\nSkills:")
    for skill in skills:
        print(">", skill[0])


def generate_query_chat_gpt(connection, user_id, resume_id):
    cursor = connection.cursor()
    user = get_user_by_id(connection, user_id)
    query_chat_gpt = f'{user[1]} {user[2]} - {user[3]}, {user[5]} - {user[6]} - {user[7]} - {user[8]}'

    cursor.execute('''SELECT description FROM work_experiences WHERE resume_id = ?''', (resume_id,))
    work_experiences = cursor.fetchall()
    query_chat_gpt += "\nWork Experiences:"
    for experience in work_experiences:
        query_chat_gpt += experience[0]

    cursor.execute('''SELECT description FROM education WHERE resume_id = ?''', (resume_id,))
    educations = cursor.fetchall()
    query_chat_gpt += "\nEducation:"
    for education in educations:
        query_chat_gpt += education[0]

    cursor.execute('''SELECT description FROM skills WHERE resume_id = ?''', (resume_id,))
    skills = cursor.fetchall()
    query_chat_gpt += "\nSkills:"
    for skill in skills:
        query_chat_gpt += skill[0]
    print(query_chat_gpt)


# UPDATE ELEMENTS
# cursor.execute("UPDATE example SET age = 31 WHERE id = 2")

# DROP TABLE
# dropTableStatement = "DROP TABLE user"
# cursor.execute(dropTableStatement)

# add_user(1, 'Luis')
# get_all_users(connection)
# delete_user(connection, 1531227019)

# create_table(connection)

# get_resume_details(connection, 1)

# get_user_by_id(connection, 1531227019)

generate_query_chat_gpt(connection, 1531227019, 1)
