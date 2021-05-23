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
        sql_create_scans_table = """ CREATE TABLE IF NOT EXISTS scans (
                                            scan_name text,
                                            frame integer,
                                            depth_matrix_location text,
                                            intrin_matrix_location text,
                                            image_location text, 
                                            PRIMARY KEY (scan_name, frame)
                                        ); """
        self._cursor.execute(sql_create_scans_table)
        self._conn.commit()

        sql_create_results_table = """ CREATE TABLE IF NOT EXISTS results (
                                            scan_name text,
                                            body_height float,
                                            shoulders float,
                                            abdomen, float,
                                            right_thigh float,
                                            left_thigh float,
                                            right_shoulder_to_elbow float,
                                            left_shoulder_to_elbow float,
                                            bmi_score float,
                                            weight float,
                                            PRIMARY KEY (scan_name)
                                        ); """
        self._cursor.execute(sql_create_results_table)
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

    def check_if_scan_exists(self, scan_name):
        query_string = f"SELECT * FROM scans WHERE scan_name = '{scan_name}' limit 1"
        self._cursor.execute(query_string)
        retVal = self._cursor.fetchall()

        if len(retVal) > 0:
            return True
        else:
            return False

    def truncate_table(self):
        query_string = f"DROP TABLE scans"
        self._cursor.execute(query_string)
        query_string = f"DROP TABLE results"
        self._cursor.execute(query_string)
        clear_folder()
        self.init_tables()
        return self

    def delete_scan(self, scan_name):
        query_string = f"DELETE FROM scans WHERE scan_name = '{scan_name}'"
        self._cursor.execute(query_string)
        query_string = f"DELETE FROM results WHERE scan_name = '{scan_name}'"
        self._cursor.execute(query_string)
        clear_scan(scan_name)
        return self

    def get_all_scan_names(self):
        query_string = f"SELECT scan_name FROM scans"
        self._cursor.execute(query_string)
        retVal = self._cursor.fetchall()
        return retVal

    def save_scan_results(self, scan_name, results):
        body_height = results['body_height']
        shoulders = results['shoulders']
        abdomen = results['abdomen']
        right_thigh = results['right_thigh']
        left_thigh = results['left_thigh']
        right_shoulder_to_elbow = results['right_shoulder_to_elbow']
        left_shoulder_to_elbow = results['left_shoulder_to_elbow']
        bmi_score = results['bmi_score']
        weight = results['weight']

        query_string = f"INSERT INTO results (scan_name, body_height, shoulders, abdomen, right_thigh, left_thigh, right_shoulder_to_elbow, " \
                       f"left_shoulder_to_elbow, bmi_score, weight) " \
                       f"VALUES ('{scan_name}', {body_height}, {shoulders}, {abdomen}, {right_thigh}, {left_thigh}, " \
                       f"{right_shoulder_to_elbow}, {left_shoulder_to_elbow}, {bmi_score}, {weight})"
        self._cursor.execute(query_string)
        self._conn.commit()
        return self

    def get_scan_results_by_name(self, scan_name):
        query_string = f"SELECT body_height, shoulders, abdomen, right_thigh, left_thigh, right_shoulder_to_elbow, " \
                       f"left_shoulder_to_elbow, bmi_score, weight FROM results WHERE scan_name = '{scan_name}' limit 1"
        self._cursor.execute(query_string)
        retVal = self._cursor.fetchall()[0]

        results = {'body_height': retVal[0], 'shoulders': retVal[1], 'abdomen': retVal[2],
                   'right_thigh': retVal[3], 'left_thigh': retVal[4], 'right_shoulder_to_elbow': retVal[5],
                   'left_shoulder_to_elbow': retVal[6], 'bmi_score': retVal[7], 'weight': retVal[8]}
        return results

    def close(self):
        self._cursor.close()
        self._conn.close()
