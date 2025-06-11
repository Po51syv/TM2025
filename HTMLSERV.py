import socket
from flask import Flask, request, jsonify, render_template_string
import threading

# TCP Server setup
HOST = '0.0.0.0'
PORT = 12345

# Dictionary to hold multiple robot connections
robot_connections = {}  # key: robot_id, value: conn

# Background thread to accept multiple connections
def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"TCP Server listening on port {PORT}...")

    robot_counter = 1
    while True:
        conn, addr = server_socket.accept()
        robot_id = f"Robot{robot_counter}"
        robot_counter += 1
        robot_connections[robot_id] = conn
        print(f"{robot_id} connected from {addr}")

threading.Thread(target=tcp_server, daemon=True).start()

# Flask Web App
app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Robot Control</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; }
        .grid {
            display: grid; grid-template-columns: 100px 100px 100px;
            grid-gap: 10px; justify-content: center;
        }
        button, select {
            padding: 20px; font-size: 24px;
            background-color: #4CAF50; color: white;
            border: none; border-radius: 10px;
        }
        button:active { background-color: #367c39; }
        .exit { background-color: #f44336; }
        #status { margin-top: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Contrôle Multi-Robot</h1>
    <label for="robot">Robot:</label>
    <select id="robot">
        {% for robot_id in robots %}
            <option value="{{ robot_id }}">{{ robot_id }}</option>
        {% endfor %}
    </select>
    <div class="grid">
        <div></div>
        <button onclick="sendCmd('f')">↑</button>
        <div></div>
        <button onclick="sendCmd('l')">←</button>
        <button onclick="sendCmd('s')">■</button>
        <button onclick="sendCmd('r')">→</button>
        <div></div>
        <button onclick="sendCmd('b')">↓</button>
        <div></div>
    </div>
    <br>
    <button class="exit" onclick="sendCmd('exit')">❌ Exit</button>
    <div id="status"></div>

    <script>
        function sendCmd(cmd) {
            const robot = document.getElementById('robot').value;
            fetch(`/send?cmd=${cmd}&robot=${robot}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = data.message;
                })
                .catch(error => {
                    document.getElementById('status').textContent = 'Erreur: ' + error;
                });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, robots=robot_connections.keys())

@app.route('/send')
def send():
    cmd = request.args.get('cmd')
    robot_id = request.args.get('robot')

    if robot_id not in robot_connections:
        return jsonify(message="Robot non connecté.")

    conn = robot_connections[robot_id]

    if cmd == 'exit':
        try:
            conn.sendall(b's')
            conn.close()
        except:
            pass
        del robot_connections[robot_id]
        return jsonify(message=f"{robot_id} déconnecté.")
    
    if cmd in ['f', 'b', 'l', 'r', 's']:
        try:
            conn.sendall(cmd.encode())
            return jsonify(message=f"Commande '{cmd}' envoyée à {robot_id} !")
        except Exception as e:
            return jsonify(message=f"Erreur d'envoi: {str(e)}")

    return jsonify(message="Commande invalide.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
