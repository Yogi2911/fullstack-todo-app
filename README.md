# Full-Stack Todo App

A minimal full-stack Python web app:
- **Backend:** Flask (REST API)
- **Database:** SQLite (auto-created on first run)
- **Frontend:** HTML/CSS/JavaScript (served by Flask, talks to the API via `fetch`)

## Project structure
```
fullstack-todo-app/
├── app.py              # Flask app + REST API + SQLite
├── requirements.txt
├── templates/
│   └── index.html      # Main page
└── static/
    ├── style.css
    └── script.js
```

## Setup & Run

1. (Recommended) create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open your browser at:
   ```
   http://127.0.0.1:5000
   ```

That's it — add, check off, and delete todos. Data persists in `todos.db` (created automatically next to `app.py`).

## API endpoints

| Method | Route              | Description          |
|--------|---------------------|-----------------------|
| GET    | `/api/todos`         | List all todos        |
| POST   | `/api/todos`         | Create a todo (`{"task": "..."}`) |
| PATCH  | `/api/todos/<id>`     | Update a todo (`{"task": "...", "done": true}`) |
| DELETE | `/api/todos/<id>`     | Delete a todo         |


## Development Status

User profile functionality is currently being developed.
