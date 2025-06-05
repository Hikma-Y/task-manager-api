from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = 'tasks.json'

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If file is empty or corrupted, start fresh
        return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)


# Get with optional filtering by 'done' status
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    status = request.args.get('done')
    if status is not None:
        if status.lower() == 'true':
            tasks = [task for task in tasks if task['done']]
        elif status.lower() == 'false':
            tasks = [task for task in tasks if not task['done']]
    return jsonify(tasks)



#post with validation
@app.route('/api/tasks', methods=['POST'])
def add_task():
    tasks = load_tasks()
    data = request.get_json()
    
    # Validation: Title must not be empty or just spaces
    if not data or not data.get('title', '').strip():
        return jsonify({"error": "Task title is required"}), 400

    new_task = {
        "id": (tasks[-1]['id'] + 1) if tasks else 1,
        "title": data.get("title").strip(),
        "description": data.get("description", "").strip(),
        "done": False
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    for task in tasks:
        if task['id'] == task_id:
            task['done'] = data.get('done', task['done'])
            task['title'] = data.get('title', task['title'])
            task['description'] = data.get('description', task['description'])
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            deleted = tasks.pop(i)
            save_tasks(tasks)
            return jsonify(deleted)
    return jsonify({"error": "Task not found"}), 404

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>Task Manager API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f6f8;
                color: #333;
                margin: 40px auto;
                max-width: 600px;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2a9d8f;
                font-weight: 700;
            }
            p {
                font-size: 1.1rem;
            }
            ul {
                list-style-type: none;
                padding-left: 0;
            }
            li {
                background: #e0f7f5;
                margin: 10px 0;
                padding: 10px 15px;
                border-left: 5px solid #2a9d8f;
                font-weight: 600;
                border-radius: 4px;
                font-size: 1rem;
            }
            code {
                background-color: #d1e7e0;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <h1>✅ Task Manager API is Running</h1>
        <p>Use the following endpoints to manage your tasks:</p>
        <ul>
            <li><code>GET /api/tasks</code> - List all tasks</li>
            <li><code>POST /api/tasks</code> - Add a new task (send JSON with "title")</li>
            <li><code>PUT /api/tasks/&lt;id&gt;</code> - Update a task (send JSON with "done", "title", or "description")</li>
            <li><code>DELETE /api/tasks/&lt;id&gt;</code> - Delete a task</li>
        </ul>
    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(debug=True)
