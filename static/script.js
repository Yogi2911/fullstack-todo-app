const form = document.getElementById("todo-form");
const input = document.getElementById("task-input");
const list = document.getElementById("todo-list");
const emptyState = document.getElementById("empty-state");

async function fetchTodos() {
  const res = await fetch("/api/todos");
  const todos = await res.json();
  renderTodos(todos);
}

function renderTodos(todos) {
  list.innerHTML = "";
  emptyState.hidden = todos.length !== 0;

  todos.forEach((todo) => {
    const li = document.createElement("li");
    li.className = "todo-item" + (todo.done ? " done" : "");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = !!todo.done;
    checkbox.addEventListener("change", () => toggleTodo(todo.id, checkbox.checked));

    const span = document.createElement("span");
    span.textContent = todo.task;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "✕";
    deleteBtn.addEventListener("click", () => deleteTodo(todo.id));

    li.appendChild(checkbox);
    li.appendChild(span);
    li.appendChild(deleteBtn);
    list.appendChild(li);
  });
}

async function addTodo(task) {
  await fetch("/api/todos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task }),
  });
  await fetchTodos();
}

async function toggleTodo(id, done) {
  await fetch(`/api/todos/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ done }),
  });
  await fetchTodos();
}

async function deleteTodo(id) {
  await fetch(`/api/todos/${id}`, { method: "DELETE" });
  await fetchTodos();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const task = input.value.trim();
  if (!task) return;
  input.value = "";
  await addTodo(task);
});

fetchTodos();
