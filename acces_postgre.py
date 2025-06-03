import psycopg2
# Accès aux données à partir de la vm

connection = psycopg2.connect(database="eaufrance", user="yuri", password="yuri",host='10.10.47.80' , port=5432)

cursor = connection.cursor()

cursor.execute("SELECT * from commune;")

# Fetch all rows from database
record = cursor.fetchall()

print("Data from Database:- ", record)