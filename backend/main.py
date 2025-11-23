from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, ValidationError
from typing import Optional
import json
import os
from datetime import datetime, timezone
import logging
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Własny handler dla błędów walidacji
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = exc.errors()
    if errors:
        # Wyciągnij pierwszą wiadomość błędu
        first_error = errors[0]
        error_msg = first_error.get('msg', 'Błąd walidacji')
        
        # Jeśli to ValueError z naszego validatora, wyciągnij jego wiadomość
        if 'ctx' in first_error and 'error' in first_error['ctx']:
            error_msg = str(first_error['ctx']['error'])
        
        return JSONResponse(
            status_code=422,
            content={"detail": error_msg}
        )
    return JSONResponse(
        status_code=422,
        content={"detail": "Błąd walidacji danych"}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TASKS_FILE = "tasks.json"

class TaskCreate(BaseModel):
    title: str
    description: str
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Tytuł zadania nie może być pusty')
        if len(v.strip()) < 3:
            raise ValueError('Tytuł musi mieć co najmniej 3 znaki')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def description_clean(cls, v):
        return v.strip() if v else ""

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Tytuł zadania nie może być pusty')
            if len(v.strip()) < 3:
                raise ValueError('Tytuł musi mieć co najmniej 3 znaki')
            return v.strip()
        return v

def read_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

@app.get("/health")
def health():
    logger.info("Health check")
    return {
        "status": "OK",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/tasks")
def get_tasks(
    completed: Optional[str] = Query(None, description="Filtruj po statusie (true/false)"),
    sort: Optional[str] = Query("createdAt", description="Sortuj po polu (createdAt, title)"),
    page: Optional[int] = Query(1, ge=1, description="Numer strony"),
    limit: Optional[int] = Query(100, ge=1, le=10000, description="Limit na stronę")
):
    logger.info(f"GET /tasks - completed={completed}, sort={sort}, page={page}, limit={limit}")
    tasks = read_tasks()
    
    # Konwersja stringa na boolean
    if completed is not None:
        completed_bool = completed.lower() == 'true'
        tasks = [t for t in tasks if t["completed"] == completed_bool]
    
    if sort == "title":
        tasks = sorted(tasks, key=lambda x: x["title"].lower())
    elif sort == "createdAt":
        tasks = sorted(tasks, key=lambda x: x["createdAt"], reverse=True)
    
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "tasks": tasks[start:end],
        "total": len(tasks),
        "page": page,
        "limit": limit,
        "pages": (len(tasks) + limit - 1) // limit
    }

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    logger.info(f"GET /tasks/{task_id}")
    tasks = read_tasks()
    
    for task in tasks:
        if task["id"] == task_id:
            return task
    
    raise HTTPException(status_code=404, detail={"error": "Task not found", "id": task_id})

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    logger.info(f"POST /tasks - title={task.title}")
    tasks = read_tasks()
    new_id = max([t["id"] for t in tasks], default=0) + 1
    
    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "completed": False,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    
    tasks.append(new_task)
    write_tasks(tasks)
    logger.info(f"Created task {new_id}")
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    logger.info(f"PUT /tasks/{task_id}")
    tasks = read_tasks()
    
    for t in tasks:
        if t["id"] == task_id:
            if task.title is not None:
                t["title"] = task.title
            if task.description is not None:
                t["description"] = task.description
            if task.completed is not None:
                t["completed"] = task.completed
            t["updatedAt"] = datetime.now(timezone.utc).isoformat()
            write_tasks(tasks)
            logger.info(f"Updated task {task_id}")
            return t
    
    raise HTTPException(status_code=404, detail={"error": "Task not found", "id": task_id})

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    logger.info(f"DELETE /tasks/{task_id}")
    tasks = read_tasks()
    
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            deleted = tasks.pop(i)
            write_tasks(tasks)
            logger.info(f"Deleted task {task_id}")
            return deleted
    
    raise HTTPException(status_code=404, detail={"error": "Task not found", "id": task_id})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
