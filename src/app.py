from flask import Flask, render_template

app = Flask(__name__)

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
def watch_scan():
    print("scan_history")


@app.route('/scan_history/download/<scan_id>', methods=['GET'])
def download_scan_files():
    print("scan_history")


# ----------------------------------------------- Settings section ---------------------------------------------
@app.route('/settings', methods=['GET'])
def settings():
    print("settings")


# ----------------------------------------------- Scanning section ---------------------------------------------
@app.route('/scan', methods=['GET'])
def start_scan():
    print("start scan")


@app.route('/scan/get_camera_stream', methods=['GET'])
def get_camera_stream():
    print("start scan")


@app.route('/scan/take_snapshot', methods=['POST', 'GET'])
def take_snapshot_during_scan():
    print("cancel scan")


@app.route('/scan/restart_scan', methods=['GET'])
def restart_scan():
    print("cancel scan")


@app.route('/scan/cancel_scan', methods=['GET'])
def cancel_scan():
    print("cancel scan")


if __name__ == '__main__':
    app.run(debug=True)
