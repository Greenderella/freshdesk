import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def ticket_content(json):
    return (
        json.get("description"),
        json.get("description_text"),
        json.get("due_by"),
        json.get("fr_due_by"),
        json.get("fr_escalated"),
        json.get("group_id"),
        json.get("id"),
        json.get("is_escalated"),
        json.get("priority"),
        json.get("product_id"),
        json.get("requester_id"),
        json.get("responder_id"),
        json.get("source"),
        json.get("spam"),
        json.get("status"),
        json.get("subject"),
        json.get("type"),
        json.get("created_at"),
        json.get("updated_at"),
    )


def conversation_content(json):
    return (
        json.get("ticket_id"),
        json.get("id"),
        json.get("body"),
        json.get("body_text"),
        json.get("incoming"),
        json.get("private"),
        json.get("user_id"),
        json.get("source"),
        json.get("created_at"),
        json.get("updated_at"),
    )


def tag_content(ticket_id, tag):
    return (ticket_id, tag)


def save_ticket(cur, ticket):
    cur.execute(
        """
        INSERT OR IGNORE INTO tickets(
            description,
            description_text,
            due_by,
            fr_due_by,
            fr_escalated,
            group_id,
            id,
            is_escalated,
            priority,
            product_id,
            requester_id,
            responder_id,
            source,
            spam,
            status,
            subject,
            type,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ticket_content(ticket),
    )


def save_conversation(cur, conversation):
    cur.execute(
        """
        INSERT OR IGNORE INTO conversations(
            ticket_id,
            id,
            body,
            body_text,
            incoming,
            private,
            user_id,
            source,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        conversation_content(conversation),
    )


def save_tag(cur, ticket_id, tag):
    cur.execute(
        """
        INSERT OR IGNORE INTO tags(ticket_id, name)
        VALUES (?, ?)
        """,
        tag_content(ticket_id, tag),
    )


def connect_and_create():
    database = r"tickets.db"

    sql_create_tickets_table = """
    CREATE TABLE IF NOT EXISTS tickets (
        description TEXT,
        description_text TEXT,
        due_by TEXT,
        fr_due_by TEXT,
        fr_escalated TEXT,
        group_id INTEGER,
        id INTEGER NOT NULL PRIMARY KEY,
        is_escalated TEXT,
        priority INTEGER,
        product_id INTEGER,
        requester_id INTEGER,
        responder_id INTEGER,
        source TEXT,
        spam TEXT,
        status TEXT,
        subject TEXT,
        type TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    """

    sql_create_tags_table = """
    CREATE TABLE IF NOT EXISTS tags (
        ticket_id INTEGER NOT NULL,
        name TEXT,
        UNIQUE(ticket_id, name)
    );
    """

    sql_create_conversations_table = """
    CREATE TABLE IF NOT EXISTS conversations (
        ticket_id INTEGER NOT NULL,
        id INTEGER NOT NULL PRIMARY KEY,
        body TEXT,
        body_text TEXT,
        incoming INTEGER,
        private INTEGER,
        user_id INTEGER,
        source INTEGER,
        created_at TEXT,
        updated_at TEXT
    );
    """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_tickets_table)
        create_table(conn, sql_create_tags_table)
        create_table(conn, sql_create_conversations_table)
        return conn

    print("Error! cannot create the database connection.")
    return None