import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import jwt
from datetime import datetime, timezone, timedelta
import os

os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["SUPABASE_JWT_SECRET"] = "test-secret-key-for-jwt-testing-purposes"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"

from main import app, get_current_user, require_admin, TokenData

client = TestClient(app)


def create_test_token(user_id: str, email: str, role: str = "user", expired: bool = False):
    payload = {
        "sub": user_id,
        "email": email,
        "user_role": role,
        "aud": "authenticated",
        "role": "authenticated",
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": (datetime.now(timezone.utc) + timedelta(hours=-1 if expired else 1)).timestamp()
    }
    return jwt.encode(payload, os.environ["SUPABASE_JWT_SECRET"], algorithm="HS256")


USER_TOKEN = create_test_token("user-123", "user@example.com", "user")
ADMIN_TOKEN = create_test_token("admin-456", "admin@example.com", "admin")
EXPIRED_TOKEN = create_test_token("user-123", "user@example.com", "user", expired=True)


class TestAuthRegister:

    @patch('main.httpx.AsyncClient')
    def test_register_success(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "test@example.com",
                "created_at": "2025-01-15T10:30:00Z"
            }
        }
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["role"] == "user"

    @patch('main.httpx.AsyncClient')
    def test_register_user_already_exists(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"msg": "User already registered"}
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.post("/auth/register", json={
            "email": "existing@example.com",
            "password": "Test123!"
        })
        
        assert response.status_code == 400
        assert "User already exists" in str(response.json())

    def test_register_invalid_email(self):
        response = client.post("/auth/register", json={
            "email": "invalid-email",
            "password": "Test123!"
        })
        
        assert response.status_code == 422

    def test_register_missing_email(self):
        response = client.post("/auth/register", json={
            "password": "Test123!"
        })
        
        assert response.status_code == 422

    def test_register_missing_password(self):
        response = client.post("/auth/register", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 422

    def test_register_short_password(self):
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "123"
        })
        
        assert response.status_code == 422


class TestAuthLogin:

    @patch('main.httpx.AsyncClient')
    def test_login_success(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": USER_TOKEN,
            "user": {
                "id": "user-123",
                "email": "user@example.com"
            }
        }
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "Test123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == "user@example.com"

    @patch('main.httpx.AsyncClient')
    def test_login_invalid_credentials(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid login credentials"}
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.post("/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert response.json()["detail"]["error"] == "Invalid credentials"

    def test_login_missing_email(self):
        response = client.post("/auth/login", json={
            "password": "Test123!"
        })
        
        assert response.status_code == 422

    def test_login_missing_password(self):
        response = client.post("/auth/login", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 422


class TestTasksAuthorization:

    def test_get_tasks_no_token(self):
        response = client.get("/tasks")
        
        assert response.status_code == 401
        assert response.json()["detail"]["error"] == "No token provided"

    def test_get_tasks_invalid_token_format(self):
        response = client.get("/tasks", headers={"Authorization": "InvalidFormat"})
        
        assert response.status_code == 401
        assert response.json()["detail"]["error"] == "Invalid token format"

    def test_get_tasks_invalid_token(self):
        response = client.get("/tasks", headers={"Authorization": "Bearer invalid-token"})
        
        assert response.status_code == 401
        assert response.json()["detail"]["error"] == "Invalid token"

    def test_get_tasks_expired_token(self):
        response = client.get("/tasks", headers={"Authorization": f"Bearer {EXPIRED_TOKEN}"})
        
        assert response.status_code == 401
        assert response.json()["detail"]["error"] == "Token expired"

    @patch('main.httpx.AsyncClient')
    def test_get_tasks_success(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "task-1",
                "title": "Test task",
                "completed": False,
                "user_id": "user-123",
                "created_at": "2025-01-15T10:00:00Z"
            }
        ]
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.get("/tasks", headers={"Authorization": f"Bearer {USER_TOKEN}"})
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Test task"


class TestCreateTask:

    def test_create_task_no_token(self):
        response = client.post("/tasks", json={"title": "New task"})
        
        assert response.status_code == 401

    @patch('main.httpx.AsyncClient')
    def test_create_task_success(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = [{
            "id": "new-task-id",
            "title": "New task",
            "completed": False,
            "user_id": "user-123",
            "created_at": "2025-01-15T14:00:00Z"
        }]
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.post(
            "/tasks",
            json={"title": "New task"},
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New task"
        assert data["completed"] == False

    def test_create_task_empty_title(self):
        response = client.post(
            "/tasks",
            json={"title": ""},
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 422

    def test_create_task_missing_title(self):
        response = client.post(
            "/tasks",
            json={},
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 422

    def test_create_task_whitespace_title(self):
        response = client.post(
            "/tasks",
            json={"title": "   "},
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 422


class TestUpdateTask:

    def test_update_task_no_token(self):
        response = client.patch("/tasks/task-123", json={"completed": True})
        
        assert response.status_code == 401

    @patch('main.httpx.AsyncClient')
    def test_update_task_not_found(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = []
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.patch(
            "/tasks/nonexistent-task",
            json={"completed": True},
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"]["error"] == "Task not found"

    @patch('main.httpx.AsyncClient')
    def test_update_task_access_denied(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{
            "id": "task-123",
            "title": "Other user task",
            "completed": False,
            "user_id": "other-user-999",
            "created_at": "2025-01-15T10:00:00Z"
        }]
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.patch(
            "/tasks/task-123",
            json={"completed": True},
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 403
        assert response.json()["detail"]["error"] == "Access denied"

    @patch('main.httpx.AsyncClient')
    def test_update_task_admin_can_update_any(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{
            "id": "task-123",
            "title": "Other user task",
            "completed": False,
            "user_id": "other-user-999",
            "created_at": "2025-01-15T10:00:00Z"
        }]
        
        mock_patch_response = MagicMock()
        mock_patch_response.status_code = 200
        mock_patch_response.json.return_value = [{
            "id": "task-123",
            "title": "Other user task",
            "completed": True,
            "user_id": "other-user-999",
            "created_at": "2025-01-15T10:00:00Z"
        }]
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.patch = AsyncMock(return_value=mock_patch_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.patch(
            "/tasks/task-123",
            json={"completed": True},
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        
        assert response.status_code == 200
        assert response.json()["completed"] == True

    @patch('main.httpx.AsyncClient')
    def test_update_own_task_success(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{
            "id": "task-123",
            "title": "My task",
            "completed": False,
            "user_id": "user-123",
            "created_at": "2025-01-15T10:00:00Z"
        }]
        
        mock_patch_response = MagicMock()
        mock_patch_response.status_code = 200
        mock_patch_response.json.return_value = [{
            "id": "task-123",
            "title": "My task",
            "completed": True,
            "user_id": "user-123",
            "created_at": "2025-01-15T10:00:00Z"
        }]
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.patch = AsyncMock(return_value=mock_patch_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.patch(
            "/tasks/task-123",
            json={"completed": True},
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 200
        assert response.json()["completed"] == True


class TestDeleteTask:

    def test_delete_task_no_token(self):
        response = client.delete("/tasks/task-123")
        
        assert response.status_code == 401

    @patch('main.httpx.AsyncClient')
    def test_delete_task_not_found(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = []
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.delete(
            "/tasks/nonexistent-task",
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"]["error"] == "Task not found"

    @patch('main.httpx.AsyncClient')
    def test_delete_task_access_denied(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{
            "id": "task-123",
            "title": "Other user task",
            "completed": False,
            "user_id": "other-user-999",
            "created_at": "2025-01-15T10:00:00Z"
        }]
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.delete(
            "/tasks/task-123",
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 403
        assert response.json()["detail"]["error"] == "Access denied"

    @patch('main.httpx.AsyncClient')
    def test_delete_own_task_success(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{
            "id": "task-123",
            "title": "My task",
            "completed": False,
            "user_id": "user-123",
            "created_at": "2025-01-15T10:00:00Z"
        }]
        
        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 204
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.delete = AsyncMock(return_value=mock_delete_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.delete(
            "/tasks/task-123",
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 204

    @patch('main.httpx.AsyncClient')
    def test_delete_task_admin_can_delete_any(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{
            "id": "task-123",
            "title": "Other user task",
            "completed": False,
            "user_id": "other-user-999",
            "created_at": "2025-01-15T10:00:00Z"
        }]
        
        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 204
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.delete = AsyncMock(return_value=mock_delete_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.delete(
            "/tasks/task-123",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        
        assert response.status_code == 204


class TestAdminEndpoints:

    def test_get_users_no_token(self):
        response = client.get("/admin/users")
        
        assert response.status_code == 401

    def test_get_users_user_role_forbidden(self):
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 403
        assert response.json()["detail"]["error"] == "Admin access required"

    @patch('main.httpx.AsyncClient')
    def test_get_users_admin_success(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "user-123",
                "email": "user@example.com",
                "role": "user",
                "created_at": "2025-01-15T10:30:00Z"
            },
            {
                "id": "admin-456",
                "email": "admin@example.com",
                "role": "admin",
                "created_at": "2025-01-10T08:00:00Z"
            }
        ]
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2

    def test_delete_user_no_token(self):
        response = client.delete("/admin/users/user-123")
        
        assert response.status_code == 401

    def test_delete_user_user_role_forbidden(self):
        response = client.delete(
            "/admin/users/user-123",
            headers={"Authorization": f"Bearer {USER_TOKEN}"}
        )
        
        assert response.status_code == 403
        assert response.json()["detail"]["error"] == "Admin access required"

    @patch('main.httpx.AsyncClient')
    def test_delete_user_not_found(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = []
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.delete(
            "/admin/users/nonexistent-user",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"]["error"] == "User not found"

    @patch('main.httpx.AsyncClient')
    def test_delete_user_admin_success(self, mock_client):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{
            "id": "user-to-delete",
            "email": "delete@example.com",
            "role": "user"
        }]
        
        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 204
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_get_response)
        mock_client_instance.delete = AsyncMock(return_value=mock_delete_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        response = client.delete(
            "/admin/users/user-to-delete",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        
        assert response.status_code == 204


class TestHealthEndpoint:

    def test_health_check(self):
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OK"
        assert "timestamp" in data


class TestInvalidEndpoints:

    def test_nonexistent_endpoint(self):
        response = client.get("/nonexistent")
        
        assert response.status_code == 404

    def test_wrong_method_on_tasks(self):
        response = client.put("/tasks")
        
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
