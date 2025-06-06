from flask import Flask, render_template, request, jsonify
import pymysql
import datetime

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'  
app.config['MYSQL_DB'] = 'students'

# Function to get the MySQL connection
def get_db_connection():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Route for the main page
@app.route('/')
def index():
    return render_template('gemechis.html')  

# Route for the thicker page
@app.route('/thicker')
def thicker():
    return render_template('registers.html')  # Thicker page

@app.route('/get_student/<barcode>', methods=['GET'])
def get_student(barcode):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    student_id, 
                    CONCAT(First_name, ' ', Father_name, ' ', G_Father_name) AS full_name, 
                    sex,
                    (SELECT SUM(service_charge) FROM cafteria WHERE student_id = (SELECT student_id FROM aastu_students WHERE barcode = %s)) AS total_service_charge
                FROM 
                    aastu_students 
                WHERE 
                    barcode = %s
            """, (barcode, barcode))
            student = cursor.fetchone()
            if student:
                return jsonify(student)
            else:
                return jsonify({'error': 'No Longer AASTU student'})
    finally:
        connection.close()

@app.route('/submit', methods=['POST'])
def submit():
    barcode = request.form['barcode']
    service_time = request.form['service_time']
    status = 'used'
    service_charge = 33.33

    service_datetime = datetime.datetime.strptime(service_time, '%Y-%m-%dT%H:%M')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT student_id, CONCAT(First_name, ' ', Father_name, ' ', G_Father_name) AS full_name, sex FROM aastu_students WHERE barcode = %s",
                (barcode,)
            )
            student = cursor.fetchone()
            if student:
                full_name = student['full_name']
                sex = student['sex']

                # Additional logic and database operations can be added here

                net_charge = 3000 - service_charge  # Simplified for this example

                # Insert into cafteria
                cursor.execute(
                    "INSERT INTO cafteria (student_id, full_name, service_time, status, service_charge, net_charge, sex) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (student['student_id'], full_name, service_time, status, service_charge, net_charge, sex)
                )
                connection.commit()
                return jsonify({'message': 'New record created successfully', 'full_name': full_name, 'student_id': student['student_id'], 'net_charge': net_charge, 'sex': sex})
            else:
                return jsonify({'error': 'Student not found! ❌'}), 404
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)