import sqlite3
from sqlite3 import Error

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def setup_database(self):
        self.create_connection()
        sql_create_students_table = """ CREATE TABLE IF NOT EXISTS students (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            grade text,
                                            photo blob
                                        ); """
        sql_create_attendance_table = """ CREATE TABLE IF NOT EXISTS attendance (
                                            id integer PRIMARY KEY,
                                            student_id integer NOT NULL,
                                            date text NOT NULL,
                                            time text NOT NULL,
                                            status text NOT NULL,
                                            FOREIGN KEY (student_id) REFERENCES students (id)
                                        ); """
        sql_create_notifications_table = """ CREATE TABLE IF NOT EXISTS notifications (
                                                id integer PRIMARY KEY,
                                                template text NOT NULL,
                                                settings text
                                            ); """
        self.create_table(sql_create_students_table)
        self.create_table(sql_create_attendance_table)
        self.create_table(sql_create_notifications_table)

    def add_student(self, name, grade, photo):
        sql = ''' INSERT INTO students(name, grade, photo)
                  VALUES(?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, (name, grade, photo))
        self.conn.commit()
        return cur.lastrowid

    def add_attendance_record(self, student_id, date, time, status):
        sql = ''' INSERT INTO attendance(student_id, date, time, status)
                  VALUES(?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, (student_id, date, time, status))
        self.conn.commit()
        return cur.lastrowid

    def get_attendance_records(self, start_date, end_date):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM attendance WHERE date BETWEEN ? AND ?", (start_date, end_date))
        rows = cur.fetchall()
        return rows

    def backup_database(self, backup_file):
        with sqlite3.connect(backup_file) as bck:
            self.conn.backup(bck)

    def restore_database(self, backup_file):
        with sqlite3.connect(backup_file) as bck:
            bck.backup(self.conn)

    def close_connection(self):
        if self.conn:
            self.conn.close()
