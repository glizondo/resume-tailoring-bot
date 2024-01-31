import sqlite3

# connection = sqlite3.connect("profile.db")


# CREATE TABLE
def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER, name TEXT, lastname TEXT,"
                   "username TEXT, city TEXT, state TEXT"
                   ", country TEXT, email TEXT, phone TEXT, linkedin TEXT)")
    connection.commit()
    connection.close()


# ADD ELEMENTS TO THE TABLE
def add_user(connection, user_id, user_name):
    cursor = connection.cursor()
    # cursor.execute(f"INSERT INTO user VALUES ({user_id}, {user_name}, '', '', '', '', '', "
    #                "'', '', '' )")
    cursor.execute(f"INSERT INTO user VALUES ({user_id}, '{user_name}', 'Smith', 'jsmith', 'Portland', 'Oregon', 'US', "
                   "'email@email.com', '248-123-1234', 'https://www.linkedin.com/in/guillermo-lizondo' )")
    print(f'Added user with id: {user_id}')
    connection.commit()
    connection.close()


# GET ELEMENTS FROM TABLE
def get_all_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    connection.commit()
    connection.close()


# DELETE ELEMENTS
def delete_user(connection, user_id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM user WHERE id=" + user_id)
    connection.commit()
    connection.close()


# UPDATE ELEMENTS
# cursor.execute("UPDATE example SET age = 31 WHERE id = 2")

# DROP TABLE
# dropTableStatement = "DROP TABLE user"
# cursor.execute(dropTableStatement)

# add_user(1, 'Luis')
# get_all_users(connection)
