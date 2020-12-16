import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def ticket_content(json):
    return (json["description"],json["description_text"],json["due_by"],json["fr_due_by"],json["fr_escalated"],json["group_id"],json["id"],json["is_escalated"],json["priority"],json["product_id"],json["requester_id"],json["responder_id"],json["source"],json["spam"],json["status"],json["subject"],json["type"],json["created_at"],json["updated_at"])

def conversation_content(json):
    return (json["ticket_id"],json["body"],json["id"],json["body_text"],json["created_at"],json["updated_at"])

def tag_content(ticket_id, tag):
    return (ticket_id, tag)

def save_ticket(cur, ticket):
    try:
        cur.execute("INSERT INTO tickets(description,description_text,due_by,fr_due_by,fr_escalated,group_id,id,is_escalated,priority,product_id,requester_id,responder_id,source,spam,status,subject,type,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ticket_content(ticket))
    except:
        print("Ticket with ID  ", ticket["id"]," was already in the DB, skipping") 

def save_conversation(cur, conversation):
    try:
        cur.execute("INSERT INTO conversations(ticket_id, body, id, body_text, created_at,updated_at) VALUES (?,?,?,?,?,?)", conversation_content(conversation))
    except:
        print("Conversation with ID  ", conversation["id"]," was already in the DB, skipping") 

def save_tag(cur, ticket_id, tag):
    cur.execute("INSERT INTO tags(ticket_id, name) VALUES (?,?)", tag_content(ticket_id, tag))

def connect_and_create():
    database = r"tickets.db"

    sql_create_tickets_table = """ CREATE TABLE IF NOT EXISTS tickets (
                                        description TEXT,description_text TEXT,due_by INTEGER,fr_due_by INTEGER,fr_escalated TEXT,group_id TEXT,id INTEGER NOT NULL PRIMARY KEY,is_escalated TEXT,priority INTEGER,product_id INTEGER,requester_id INTEGER,responder_id INTEGER,source TEXT,spam TEXT,status TEXT,subject TEXT,type INTEGER,created_at INTEGER,updated_at INTEGER
                                    ); """

    sql_create_tags_table = """CREATE TABLE IF NOT EXISTS tags (
                                    ticket_id INTEGER NOT NULL, name TEXT
                                );"""

    sql_create_conversations_table = """CREATE TABLE IF NOT EXISTS conversations (
                                    ticket_id INTEGER NOT NULL, id INTEGER NOT NULL, body TEXT, body_text TEXT, created_at INTEGER,updated_at INTEGER
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create tickets table
        create_table(conn, sql_create_tickets_table)

        # create tags table
        create_table(conn, sql_create_tags_table)

        # create conversation table
        create_table(conn, sql_create_conversations_table)

        return conn
    else:
        print("Error! cannot create the database connection.")

#insane copypasta: https://www.sqlitetutorial.net/sqlite-python/create-tables/
