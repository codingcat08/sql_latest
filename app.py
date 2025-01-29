from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import script
import logging

app = Flask(__name__, static_folder='build', static_url_path='')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load OpenAI API key
openai_api_key = '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'  # Replace this with your actual API key

# Placeholder for in-memory storage
sql_queries = {}

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/store_queries', methods=['POST'])
def store_queries():
    if 'sql_file' not in request.files:
        logging.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['sql_file']
    if file.filename == '':
        logging.error("No selected file in the request")
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Read the contents of the SQL file
        sql_queries['file_content'] = file.read().decode('utf-8')
        logging.info("File uploaded and queries stored successfully")
        return jsonify({"message": "File uploaded and queries stored successfully"}), 200

@app.route('/execute_logic', methods=['GET'])
def execute_logic():
    results = {}
    if 'file_content' not in sql_queries:
        logging.error("No SQL queries stored")
        return jsonify({"error": "No SQL queries stored"}), 400

    try:
        generator = script.SQLColumnDescriptionGenerator(sql_queries['file_content'], openai_api_key)
        generator.analyze_columns()
        report = generator.generate_report()

        for index, row in report.iterrows():
            results[row['Column Name']] = {
                'source_columns': row['Source Columns'],
                'transformations': row['Transformations'],
                'description': row['Description']
            }
        logging.info("Lineage creation successful")
        return jsonify(results), 200
    except Exception as e:
        logging.error(f"Error in execute_logic: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/<path:path>')
def static_proxy(path):
    # Send other files, like CSS and JavaScript
    return send_from_directory(app.static_folder, path)

@app.route('/export_report', methods=['GET'])
def export_report():
    file_path = 'column_descriptions.xlsx'  # Path to your Excel file
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return 'File not found', 404
    
if __name__ == '__main__':
    app.run(debug=True)
