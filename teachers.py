from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


import json

TEACHERS_FILE = "teachers.json"


def read_teachers():
    try:
        with open(TEACHERS_FILE, 'r') as file:
            teachers_data = json.load(file)
        return teachers_data
    except FileNotFoundError:
        # If the file doesn't exist, return an empty list
        return []

def write_teachers(teachers_data):
    try:
        with open(TEACHERS_FILE, 'w') as file:
            json.dump(teachers_data, file, indent=2)
            return jsonify({"success":"Data inserted successfully"}),200
    except:
        return jsonify({"Error":"Some thing went wrong"}),400

@app.route('/show_teachers', methods=['GET'])
@cross_origin()
def show_teachers():
    return jsonify(read_teachers())

    
@app.route('/add_teacher', methods=['POST'])
@cross_origin()
def add_teacher():
    data = request.get_json()
    
    # Validate required fields
    if 'full_name' not in data or 'age' not in data or 'dob' not in data or 'num_classes' not in data:
        return jsonify({"error": "Expected keys i.e., full_name, age, dob, num_classes in the JSON Data"}), 400

    teachers_data = read_teachers()
    # Generate a unique ID for the new teacher
    new_teacher_id = max([t.get('id', 0) for t in teachers_data], default=0) + 1

    new_teacher = {
        "id": new_teacher_id,
        "full_name": data['full_name'],
        "age": data["age"],
        "dob": data["dob"],
        "num_classes": data["num_classes"]
    }

    teachers_data.append(new_teacher)
    write_teachers(teachers_data)
    return jsonify({"success": "Data inserted successfully"}), 200

@app.route('/delete_teacher/<int:id>', methods=['DELETE'])
@cross_origin()
def delete_teacher(id):
    teachers=read_teachers()
    try:
        # Find the teacher by ID
        teacher = next((t for t in teachers if t["id"] == id), None)

        if teacher:
            # Remove the teacher's record
            modified_teachers = [t for t in teachers if t["id"] != id]
            write_teachers(modified_teachers)
            return jsonify({"message": f"Teacher deleted successfully"})
        else:
            return jsonify({"error": f"Teacher not found"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/update_teacher/<int:id>', methods=['PUT'])
@cross_origin()
def update_teacher(id):
    data = request.get_json()

    # Validate required fields
    if 'full_name' not in data or 'age' not in data or 'dob' not in data or 'num_classes' not in data:
        return jsonify({"error": "Expected keys  i.e., full_name, age,dob,num_classes in the JSON Data"}), 400

    teachers = read_teachers()
    try:
        # Find the teacher by ID
        teacher = next((t for t in teachers if t["id"] == id), None)
        if teacher:
            # Remove the updated teacher's record
            modified_teachers = [t for t in teachers if t["id"] != id]

            update_teacher = {
                "id": id,
                "full_name": data['full_name'],
                "age": data["age"],
                "dob": data["dob"],
                "num_classes": data["num_classes"]
            }

            modified_teachers.append(update_teacher)
            write_teachers(modified_teachers)
            return jsonify({"success": f"Teacher updated successfully"})
        else:
            return jsonify({"error": f"Unable to update Teacher"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search_teachers/<name>', methods=['GET'])
@cross_origin()
def search_teachers(name):
    teachers = read_teachers()
    filtered_teacher = next((t for t in teachers if t["full_name"] == name),None)
    if filtered_teacher is None:
        return jsonify({"Success":"No data found"}),200
    else:
        return filtered_teacher

@app.route('/filtered_criteria', methods=['GET'])
@cross_origin()
def filtered_criteria():
    # Get filter parameters from the query string
    age = request.args.get('age', type=int)
    num_classes = request.args.get('num_classes', type=int)

    if age is None and num_classes is None:
        return jsonify({"error": "At least one filter parameter (age or num_classes) is required"}), 400

    teachers = read_teachers()
    
    filtered_teachers = teachers

    if age is not None:
        filtered_teachers = [teacher for teacher in filtered_teachers if teacher.get('age') == age]

    if num_classes is not None:
        filtered_teachers = [teacher for teacher in filtered_teachers if teacher.get('num_classes') == num_classes]

    if not filtered_teachers:
        return jsonify({"Success": "No data found"}), 200

    return jsonify(filtered_teachers)


@app.route('/')
def index():
    return render_template('index.html', teachers=read_teachers())
if __name__ == '__main__':
    app.run(debug=True)