from flask import Flask, request, jsonify
import json
from chatgpt import *

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET'])
def test():
    return "Please use Post"

@app.route('/', methods=['POST'])
def send_msg():
    try:
        # Get raw data and decode it
        raw_data = request.get_data()
        print("Debug - Raw data type:", type(raw_data))
        print("Debug - Raw data:", repr(raw_data))
        
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8')
            print("Debug - Decoded data:", repr(raw_data))
        
        # Parse JSON
        try:
            usermsg = json.loads(raw_data)
            print("Debug - Parsed JSON:", repr(usermsg))
        except json.JSONDecodeError as je:
            error_msg = f"Invalid JSON format: {str(je)}"
            print("Debug - JSON Error:", error_msg)
            return jsonify({"error": error_msg}), 400
        
        if not isinstance(usermsg, dict):
            error_msg = f"Expected dict, got {type(usermsg)}"
            print("Debug - Type Error:", error_msg)
            return jsonify({"error": error_msg}), 400
            
        if 'client' not in usermsg:
            error_msg = "Missing 'client' field in request"
            print("Debug - Field Error:", error_msg)
            return jsonify({"error": error_msg}), 400
            
        # Get AI response
        try:
            airesponse = callToOpenAI(usermsg['client'])
            print("Debug - AI Response:", repr(airesponse))
        except Exception as ai_error:
            error_msg = f"AI Error: {str(ai_error)}"
            print("Debug - AI Error:", error_msg)
            return jsonify({"error": error_msg}), 500
        
        # Determine response type
        is_code = any([
            airesponse.startswith(('import', 'from', 'doc =', 'clr.')),
            'FilteredElementCollector' in airesponse,
            'BuiltInCategory' in airesponse,
            'doc = __revit__' in airesponse
        ])
        
        # Return response as JSON
        response_data = {
            "response": airesponse,
            "type": "code" if is_code else "message"
        }
        print("Debug - Response data:", repr(response_data))
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Server Error: {type(e).__name__} - {str(e)}"
        print("Debug - Server Error:", error_msg)
        return jsonify({"error": error_msg}), 500

@app.errorhandler(405)
def method_not_allowed(e):
    return 'Method not allowed', 405

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
