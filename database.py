from os import curdir
import sqlite3 as db
import hashlib

from numpy.core.records import record

SALT = "PasswordSalt"
DB_NAME = "database.db"


def hash(password):
    saltedPassword = password + SALT
    hashedPassword = hashlib.md5(saltedPassword.encode()).hexdigest()
    return hashedPassword


def connectToDb():
    try:
        con = db.connect(DB_NAME)
        cursor = con.cursor()
    except:
        pass
    else:
        return con, cursor

# USERS


def createUsersTable(arg):
    con, cursor = arg
    try:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users(name TEXT, surname TEXT, email TEXT NOT NULL PRIMARY KEY, password TEXT)")
        con.commit()
    except:
        pass
    else:
        return con, cursor


def initializeUsersTable():
    return createUsersTable(connectToDb())


def register(name, surname, email, password):
    con, cursor = initializeUsersTable()
    try:
        cursor.execute("INSERT INTO users VALUES(?,?,?,?)",
                       (name, surname, email, hash(password)))
    except:
        return False
    else:
        con.commit()
        con.close()
        return True


def getUserByEmail(email):
    con, cursor = initializeUsersTable()
    try:
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
    except:
        return None
    else:
        con.close()
        if not user:
            return None
        else:
            return user


def deleteUserByEmail(email):
    con, cursor = initializeUsersTable()
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    con.commit()


def login(email, password):
    con, cursor = initializeUsersTable()
    try:
        cursor.execute(
            "SELECT email, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
    except:
        return False
    else:
        if user[0] == email and user[1] == hash(password):
            return True
        return False


# OPERATIONS


def createOperationsTable(arg):
    con, cursor = arg
    try:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS operations(id TEXT NOT NULL PRIMARY KEY, email TEXT, answerKey TEXT)")
        con.commit()
    except:
        pass
    else:
        return con, cursor


def initializeOperationsTable():
    return createOperationsTable(connectToDb())


def getOperationsByEmail(email):
    con, cursor = initializeOperationsTable()
    try:
        cursor.execute("SELECT * FROM operations WHERE email = ?", (email,))
        operations = cursor.fetchall()
    except:
        return None
    else:
        con.close()
        if not operations:
            return None
        else:
            operations.reverse()
            return operations


def addOperation(id, email, answerKey):
    con, cursor = initializeOperationsTable()
    id = id.split('uploads/')[1]
    try:
        cursor.execute("INSERT INTO operations VALUES(?,?,?)",
                       (id, email, answerKey))
    except:
        return False
    else:
        con.commit()
        con.close()
        return True


def getOperationById(id):
    con, cursor = initializeOperationsTable()
    try:
        cursor.execute("SELECT * FROM operations WHERE id = ?", (id,))
        record = cursor.fetchone()
    except:
        return None
    else:
        con.close()
        if not record:
            return None
        else:
            return record


def deleteOperation(id):
    con, cursor = initializeOperationsTable()
    try:
        cursor.execute("DELETE FROM operations WHERE id = ?", (id))
    except:
        return False
    else:
        con.commit()
        con.close()
        return True

# RECORDS


def createRecordsTable(arg):
    con, cursor = arg
    try:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS records(id TEXT, nameImage TEXT, correct INT, wrong INT, empty INT, score REAL, answers TEXT, image TEXT)")
        con.commit()
    except:
        pass
    else:
        return con, cursor


def initializeRecordsTable():
    return createRecordsTable(connectToDb())


def getRecordsById(id):
    con, cursor = initializeRecordsTable()
    try:
        cursor.execute("SELECT * FROM records WHERE id = ?", (id,))
        records = cursor.fetchall()
    except:
        return None
    else:
        con.close()
        if not records:
            return None
        else:
            return records


def addRecord(id, nameImage, correct, wrong, empty, score, answer, image):
    con, cursor = initializeRecordsTable()
    id = id.split('uploads/')[1]
    try:
        cursor.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?)",
                       (id, nameImage, correct, wrong, empty, score, answer, image))
    except:
        return False
    else:
        con.commit()
        con.close()
        return True
