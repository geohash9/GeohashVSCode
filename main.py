from flask import Flask, render_template, request, jsonify
import psycopg2
import os
app = Flask(__name__)

# Database connection parameters
db_params = {
    'dbname': 'Geohash',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_location', methods=['POST'])
def get_location():
    custom_code = request.form.get('custom_code')
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Search the database for the custom code and retrieve the geohashcode
    cursor.execute("SELECT geohashcode, latitude, longitude, location_name, location_description FROM geohash3 WHERE customcode = %s;", (custom_code,))
    result = cursor.fetchone()
    
    conn.close()

    if result:
        geohashcode, latitude, longitude, locationName, locationDescription = result
        return jsonify({"geohashcode": geohashcode, "latitude": latitude, "longitude": longitude, "locationName": locationName, "locationDescription": locationDescription})
    else:
        return jsonify({"error": "Custom geohash code not found"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
