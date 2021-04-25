import cv2
import base64
from flask import Flask, render_template
from flask_cors import CORS

from src.flowManager.flowManager import FlowManager
from src.sqlConnector.sqlconnector import SQLConnector

app = Flask(__name__)
sql_connector = SQLConnector()
flow_manager = FlowManager()
CORS(app)


# ------------------------------------------------- Members --------------------------------------------------


# ------------------------------------------------- Home page ------------------------------------------------
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


# ----------------------------------------------- History section ---------------------------------------------
@app.route('/scan_history', methods=['GET'])
def scan_history():
    print("scan_history")


@app.route('/scan_history/watch/<scan_id>', methods=['GET'])
def watch_scan(scan_id):
    print("scan_history")


@app.route('/scan_history/download/<scan_id>', methods=['GET'])
def download_scan_files(scan_id):
    print("scan_history")


# ----------------------------------------------- Settings section ---------------------------------------------
@app.route('/settings', methods=['GET'])
def settings():
    print("settings")


# ----------------------------------------------- Scanning section ---------------------------------------------
@app.route('/scan', methods=['GET'])
def start_scan():
    try:
        flow_manager.start_scan_stream()
        return {'connected': False}
    except Exception:
        return {'connected': False}


@app.route('/scan/get_camera_stream', methods=['GET'])
def get_camera_stream():
    # Capture frame-by-frame
    image = flow_manager.get_last_image()
    if image is None:
        return {'image': False}
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer)
    return {'image': str(jpg_as_text)}


@app.route('/scan/take_snapshot', methods=['POST', 'GET'])
def take_snapshot_during_scan():
    flow_manager.take_snapshot()
    flow_manager.get_last_image()
    return {'snapshot': True}


@app.route('/scan/save_scan/<scan_name>', methods=['POST', 'GET'])
def save_scan(scan_name):
    flow_manager.get_and_save_scan_saved_frames(scan_name)
    return {'save_scan': True}


@app.route('/scan/restart_scan', methods=['GET'])
def restart_scan():
    flow_manager.exit_scan()
    flow_manager.start_scan_stream()
    return {'restart_scan': True}


@app.route('/scan/cancel_scan', methods=['GET'])
def cancel_scan():
    flow_manager.exit_scan()
    return {'cancel_scan': True}


@app.route('/delete_all_scans', methods=['POST'])
def delete_all_scans():
    SQLConnector().truncate_table().close()
    return {'delete_all_scans': True}


@app.route('/delete_scan/<scan_name>', methods=['POST'])
def delete_scan(scan_name):
    SQLConnector().delete_scan(scan_name).close()
    return {'delete_scan': True}


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    sql_connector.close()
