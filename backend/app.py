from flask import Flask, request, jsonify
from flask_cors import CORS
from NLPAgent.formattedCode import run_query

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/financial-query', methods=['POST'])
def financial_query():
    data = request.json
    query = data.get('query')
    
    try:
        result = run_query(query)
        
        return jsonify({
            'output_format': result.get('output_format'),
            'chart_type': result.get('chart_type'),
            'readable_resp': result.get('readable_resp'),
            'formatted_chart_data': result.get('query_rows', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
