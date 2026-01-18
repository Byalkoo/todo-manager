from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, timezone
import logging
import os
import httpx
from dotenv import load_dotenv
import jwt

load_dotenv()

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")


class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TaskCreate(BaseModel):
    title: str

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required')
        return v.strip()


class TaskUpdate(BaseModel):
    completed: Optional[bool] = None
    title: Optional[str] = None


class TokenData(BaseModel):
    user_id: str
    email: str
    role: str


def get_supabase_headers(token: str = None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["Authorization"] = f"Bearer {SUPABASE_KEY}"
    return headers


async def get_current_user(authorization: str = Header(None)) -> TokenData:
    if not authorization:
        raise HTTPException(status_code=401, detail={"error": "No token provided"})
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": "Invalid token format"})
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("user_role", "user")
        exp = payload.get("exp", 0)
        
        import time
        if exp < time.time():
            raise HTTPException(status_code=401, detail={"error": "Token expired"})
        
        if not user_id:
            raise HTTPException(status_code=401, detail={"error": "Invalid token"})
        
        return TokenData(user_id=user_id, email=email, role=role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"error": "Token expired"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token"})


async def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"error": "Admin access required"})
    return current_user


@app.get("/health")
def health():
    logger.info("Health check")
    return {
        "status": "OK",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/auth/register", status_code=201)
async def register(user: UserRegister):
    logger.info(f"POST /auth/register - email={user.email}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers=get_supabase_headers(),
            json={
                "email": user.email,
                "password": user.password
            }
        )
        
        if response.status_code == 400:
            error_data = response.json()
            if "already registered" in str(error_data).lower():
                raise HTTPException(status_code=400, detail={"error": "User already exists"})
            raise HTTPException(status_code=400, detail={"error": error_data.get("msg", "Registration failed")})
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail={"error": "Registration failed"})
        
        data = response.json()
        user_data = data.get("user", {})
        
        return {
            "message": "User created",
            "user": {
                "id": user_data.get("id"),
                "email": user_data.get("email"),
                "role": "user",
                "created_at": user_data.get("created_at")
            }
        }


@app.post("/auth/login")
async def login(user: UserLogin):
    logger.info(f"POST /auth/login - email={user.email}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers=get_supabase_headers(),
            json={
                "email": user.email,
                "password": user.password
            }
        )
        
        if response.status_code == 400:
            raise HTTPException(status_code=401, detail={"error": "Invalid credentials"})
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail={"error": "Invalid credentials"})
        
        data = response.json()
        access_token = data.get("access_token")
        user_data = data.get("user", {})
        
        try:
            payload = jwt.decode(access_token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
            role = payload.get("user_role", "user")
        except:
            role = "user"
        
        return {
            "token": access_token,
            "user": {
                "id": user_data.get("id"),
                "email": user_data.get("email"),
                "role": role
            }
        }


@app.get("/tasks")
async def get_tasks(
    current_user: TokenData = Depends(get_current_user),
    authorization: str = Header(None)
):
    logger.info(f"GET /tasks - user={current_user.email}, role={current_user.role}")
    token = authorization.replace("Bearer ", "")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/tasks?select=*&order=created_at.desc",
            headers=get_supabase_headers(token)
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail={"error": "Failed to fetch tasks"})
        
        tasks = response.json()
        return tasks


@app.post("/tasks", status_code=201)
async def create_task(
    task: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    authorization: str = Header(None)
):
    logger.info(f"POST /tasks - user={current_user.email}, title={task.title}")
    token = authorization.replace("Bearer ", "")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/tasks",
            headers={
                **get_supabase_headers(token),
                "Prefer": "return=representation"
            },
            json={
                "title": task.title,
                "completed": False,
                "user_id": current_user.user_id
            }
        )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(status_code=400, detail={"error": "Failed to create task"})
        
        tasks = response.json()
        if isinstance(tasks, list) and len(tasks) > 0:
            return tasks[0]
        return tasks


@app.patch("/tasks/{task_id}")
async def update_task(
    task_id: str,
    task: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    authorization: str = Header(None)
):
    logger.info(f"PATCH /tasks/{task_id} - user={current_user.email}")
    token = authorization.replace("Bearer ", "")
    
    async with httpx.AsyncClient() as client:
        check_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}&select=*",
            headers=get_supabase_headers(token)
        )
        
        if check_response.status_code != 200:
            raise HTTPException(status_code=500, detail={"error": "Failed to check task"})
        
        tasks = check_response.json()
        if not tasks:
            raise HTTPException(status_code=404, detail={"error": "Task not found"})
        
        existing_task = tasks[0]
        
        if current_user.role != "admin" and existing_task.get("user_id") != current_user.user_id:
            raise HTTPException(status_code=403, detail={"error": "Access denied"})
        
        update_data = {}
        if task.completed is not None:
            update_data["completed"] = task.completed
        if task.title is not None:
            update_data["title"] = task.title
        
        response = await client.patch(
            f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}",
            headers={
                **get_supabase_headers(token),
                "Prefer": "return=representation"
            },
            json=update_data
        )
        
        if response.status_code not in [200, 204]:
            raise HTTPException(status_code=400, detail={"error": "Failed to update task"})
        
        updated_tasks = response.json()
        if isinstance(updated_tasks, list) and len(updated_tasks) > 0:
            return updated_tasks[0]
        return updated_tasks


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    current_user: TokenData = Depends(get_current_user),
    authorization: str = Header(None)
):
    logger.info(f"DELETE /tasks/{task_id} - user={current_user.email}")
    token = authorization.replace("Bearer ", "")
    
    async with httpx.AsyncClient() as client:
        check_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}&select=*",
            headers=get_supabase_headers(token)
        )
        
        if check_response.status_code != 200:
            raise HTTPException(status_code=500, detail={"error": "Failed to check task"})
        
        tasks = check_response.json()
        if not tasks:
            raise HTTPException(status_code=404, detail={"error": "Task not found"})
        
        existing_task = tasks[0]
        
        if current_user.role != "admin" and existing_task.get("user_id") != current_user.user_id:
            raise HTTPException(status_code=403, detail={"error": "Access denied"})
        
        response = await client.delete(
            f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}",
            headers=get_supabase_headers(token)
        )
        
        if response.status_code not in [200, 204]:
            raise HTTPException(status_code=400, detail={"error": "Failed to delete task"})
        
        return None


@app.get("/admin/users")
async def get_users(current_user: TokenData = Depends(require_admin)):
    logger.info(f"GET /admin/users - admin={current_user.email}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/profiles?select=*",
            headers=get_supabase_headers()
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail={"error": "Failed to fetch users"})
        
        profiles = response.json()
        return profiles


@app.delete("/admin/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(require_admin)
):
    logger.info(f"DELETE /admin/users/{user_id} - admin={current_user.email}")
    
    async with httpx.AsyncClient() as client:
        check_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=*",
            headers=get_supabase_headers()
        )
        
        if check_response.status_code != 200:
            raise HTTPException(status_code=500, detail={"error": "Failed to check user"})
        
        profiles = check_response.json()
        if not profiles:
            raise HTTPException(status_code=404, detail={"error": "User not found"})
        
        response = await client.delete(
            f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY', SUPABASE_KEY)}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code not in [200, 204]:
            raise HTTPException(status_code=400, detail={"error": "Failed to delete user"})
        
        return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
