from datetime import datetime
from typing import Optional

tasks_db = []
task_id_counter = 1


def get_tasks():
    return {"tasks": tasks_db}


def _normalize_iso_datetime(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError("due_date must be a string in ISO format")

    cleaned = value.strip()
    if not cleaned:
        return None

    datetime.fromisoformat(cleaned)
    return cleaned


def add_task(title: str, description: str = "", due_date: str = None):
    global task_id_counter
    normalized_due_date = _normalize_iso_datetime(due_date)
    task = {
        "id": task_id_counter,
        "title": title,
        "description": description,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "due_date": normalized_due_date,
        "reminder_sent": False,
        "reminder_sent_at": None
    }
    tasks_db.append(task)
    task_id_counter += 1
    return {"success": True, "task": task}


def update_task(task_id: int, title: str = None, description: str = None, completed: bool = None, due_date: str = None):
    for task in tasks_db:
        if task["id"] == task_id:
            if title is not None:
                task["title"] = title
            if description is not None:
                task["description"] = description
            if completed is not None:
                task["completed"] = completed
            if due_date is not None:
                normalized_due_date = _normalize_iso_datetime(due_date)
                task["due_date"] = normalized_due_date
                task["reminder_sent"] = False
                task["reminder_sent_at"] = None
            return {"success": True, "task": task}
    return {"success": False, "error": "Task not found"}


def delete_task(task_id: int):
    global tasks_db
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            deleted_task = tasks_db.pop(i)
            return {"success": True, "task": deleted_task}
    return {"success": False, "error": "Task not found"}



