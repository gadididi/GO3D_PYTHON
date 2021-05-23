from src.sqlConnector.sqlconnector import SQLConnector


def run_all_tests():
    test_score = 0
    test_cases = 0

    SQLConnector().init_tables().close()
    if truncation_test() is True:
        test_score += 1
        test_cases += 1
    else:
        print(f"Table truncation was unsuccessful")
        test_cases += 1

    if result_insertion_test() is True:
        test_score += 1
        test_cases += 1
    else:
        print(f"Insertion test was unsuccessful")
        test_cases += 1

    if deletion_test() is True:
        test_score += 1
        test_cases += 1
    else:
        print(f"Deletion test was unsuccessful")
        test_cases += 1

    if test_score == test_cases:
        return True
    else:
        return False


def result_insertion_test():
    sql_con = SQLConnector()

    results = {'body_height': 1.0, 'abdomen': 2.0, 'shoulders': 3.0, 'right_shoulder_to_elbow': 4.0,
               'left_shoulder_to_elbow': 5.0, 'right_thigh': 6.0, 'left_thigh': 7.0, 'bmi_score': 8.0, 'weight': 9.0}

    sql_con.save_scan_results("test_scan_name", results)

    saved_results = sql_con.get_scan_results_by_name("test_scan_name")
    sql_con.close()

    if results['body_height'] != saved_results['body_height']:
        return False
    if results['abdomen'] != saved_results['abdomen']:
        return False
    if results['shoulders'] != saved_results['shoulders']:
        return False
    if results['right_shoulder_to_elbow'] != saved_results['right_shoulder_to_elbow']:
        return False
    if results['left_shoulder_to_elbow'] != saved_results['left_shoulder_to_elbow']:
        return False
    if results['right_thigh'] != saved_results['right_thigh']:
        return False
    if results['left_thigh'] != saved_results['left_thigh']:
        return False
    if results['bmi_score'] != saved_results['bmi_score']:
        return False
    if results['weight'] != saved_results['weight']:
        return False
    return True


def deletion_test():
    sql_con = SQLConnector()

    try:
        sql_con.delete_scan("test_scan_name")
        sql_con.get_scan_results_by_name("test_scan_name")
    except IndexError:
        return True
    finally:
        sql_con.close()
    return False


def truncation_test():
    sql_con = SQLConnector()
    sql_con.truncate_table()

    scan_names = sql_con.get_all_scan_names()
    sql_con.close()
    if len(scan_names) < 1:
        return True
    else:
        return False
