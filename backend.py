from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    code = data['code']
    try:
        result = subprocess.run(['python', '-c', code], capture_output=True, text=True, timeout=10)
        return jsonify({'output': result.stdout, 'error': result.stderr})
    except subprocess.TimeoutExpired:
        return jsonify({'error': '代码执行超时'}), 400

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)