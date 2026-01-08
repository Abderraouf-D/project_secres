from flask import Flask, request, jsonify
import yaml
import os

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <body>
        <h1>Nexus Internal Configuration Interface</h1>
        <p>Please submit your configuration to <code>/process_config</code>.</p>
    </body>
    </html>
    """

@app.route('/process_config', methods=['POST'])
def process_config():
    data = request.data
    if not data:
        return "Error: No data provided", 400

    try:
        
        config = yaml.load(data, Loader=yaml.Loader)
        
        if isinstance(config, dict):
            return jsonify({"status": "Config processed", "config": config})
        else:
            return "Error: Invalid config format. Expected YAML dictionary.", 400
            
    except Exception as e:
        return f"YAML Config Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)