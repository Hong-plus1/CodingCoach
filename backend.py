# from flask import Flask, request, jsonify
# import subprocess

# app = Flask(__name__)

# @app.route('/execute', methods=['POST'])
# def execute_code():
#     data = request.get_json()
#     code = data['code']
#     try:
#         result = subprocess.run(['python', '-c', code], capture_output=True, text=True, timeout=10)
#         return jsonify({'output': result.stdout, 'error': result.stderr})
#     except subprocess.TimeoutExpired:
#         return jsonify({'error': '代码执行超时'}), 400

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8000)


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

@app.post("/execute")
def execute_code(request: CodeRequest):
    try:
        # 执行代码
        result = subprocess.run(
            ["python", "-c", request.code],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return {"output": result.stdout}
        else:
            return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="代码执行超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))