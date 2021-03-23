import os
import sqlite3


def clear_folder():
    for file in os.scandir("fileStorage"):
        if file.name.endswith(".txt") or file.name.endswith(".png"):
            os.unlink(file.path)


def clear_scan(scan_name):
    for file in os.scandir("fileStorage"):
        if file.name.startswith(scan_name):
            os.unlink(file.path)


class SQLConnector:

    def __init__(self):
        self._conn = sqlite3.connect('fileStorage/go_database.db')
        self._cursor = self._conn.cursor()

    def init_tables(self):
        sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS scans (
                                            scan_name text,
                                            frame integer,
                                            depth_matrix_location text,
                                            intrin_matrix_location text,
                                            image_location text, 
                                            PRIMARY KEY (scan_name, frame)
                                        ); """
        self._cursor.execute(sql_create_projects_table)
        self._conn.commit()
        return self

    def save_scan(self, scan_name, scan_depth_loc, scan_intrin_loc, image_location, frame_number):
        query_string = f"INSERT INTO scans (scan_name, frame, depth_matrix_location, intrin_matrix_location, image_location) " \
                       f"VALUES ('{scan_name}', {frame_number}, '{scan_depth_loc}'," \
                       f" '{scan_intrin_loc}', '{image_location}')"
        print(query_string)
        self._cursor.execute(query_string)
        self._conn.commit()
        return self

    def load_scan_by_name(self, scan_name):
        query_string = f"SELECT * FROM scans WHERE scan_name = '{scan_name}' ORDER BY frame ASC"
        self._cursor.execute(query_string)
        retVal = self._cursor.fetchall()
        return retVal

    def load_only_one_frame(self, scan_name, frame_number):
        query_string = f"SELECT * FROM scans WHERE scan_name = '{scan_name}' AND frame = {frame_number}"
        self._cursor.execute(query_string)
        retVal = self._cursor.fetchall()
        return retVal

    def truncate_table(self):
        query_string = f"DROP TABLE scans"
        self._cursor.execute(query_string)
        clear_folder()
        self.init_tables()
        return self

    def delete_scan(self, scan_name):
        query_string = f"DELETE FROM scans WHERE scan_name = '{scan_name}'"
        self._cursor.execute(query_string)
        clear_scan(scan_name)
        return self

    def get_all_scan_names(self):
        query_string = f"SELECT scan_name FROM scans"
        self._cursor.execute(query_string)
        retVal = self._cursor.fetchall()
        return retVal

    def close(self):
        self._cursor.close()
        self._conn.close()
