from flask import Flask, request, jsonify, make_response
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
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8')
        
        # Parse JSON
        try:
            usermsg = json.loads(raw_data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"}), 400
        
        print(usermsg)
        
        if not isinstance(usermsg, dict) or 'client' not in usermsg:
            return jsonify({"error": "Missing 'client' field"}), 400
            
        airesponse = callToOpenAI(usermsg['client'])
        print(airesponse)
        
        # Convert response to JSON
        if isinstance(airesponse, bytes):
            airesponse = airesponse.decode('utf-8')
        
        # Return response as JSON
        return jsonify({
            "response": airesponse,
            "type": "code" if airesponse.startswith(('import', 'from', 'doc =', 'clr.')) else "message"
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(405)
def method_not_allowed(e):
    return 'Method not allowed', 405

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
