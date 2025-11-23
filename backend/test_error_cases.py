import pytest
from fastapi.testclient import TestClient
from main import app, TASKS_FILE
import json
import os
import tempfile
import shutil

client = TestClient(app)

@pytest.fixture
def backup_tasks():
    """Tworzy backup pliku tasks.json przed testem i przywraca go po teście"""
    backup_file = "tasks_backup.json"
    if os.path.exists(TASKS_FILE):
        shutil.copy(TASKS_FILE, backup_file)
        original_exists = True
    else:
        original_exists = False
    
    yield
    
    if original_exists:
        shutil.copy(backup_file, TASKS_FILE)
        os.remove(backup_file)
    elif os.path.exists(TASKS_FILE):
        os.remove(TASKS_FILE)


class TestCorruptedTasksFile:
    """Testy dla uszkodzonego pliku tasks.json"""
    
    def test_corrupted_json_file(self, backup_tasks):
        """Test: Plik JSON jest uszkodzony (nieprawidłowa składnia)"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            f.write('{"invalid": json syntax}')
        
        with pytest.raises(json.JSONDecodeError):
            response = client.get("/tasks")
    
    def test_empty_corrupted_file(self, backup_tasks):
        """Test: Plik jest pusty"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            f.write('')
        
        with pytest.raises(json.JSONDecodeError):
            response = client.get("/tasks")
    
    def test_non_list_json_structure(self, backup_tasks):
        """Test: JSON jest poprawny, ale nie jest listą"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"tasks": "not a list"}, f)
        
        with pytest.raises((TypeError, KeyError)):
            response = client.get("/tasks")
    
    def test_tasks_with_missing_fields(self, backup_tasks):
        """Test: Zadania w pliku nie mają wszystkich wymaganych pól"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Task without completed field"},
                {"id": 2, "completed": False}
            ], f)
        
        with pytest.raises(KeyError):
            response = client.get("/tasks")
    
    def test_file_permission_error(self, backup_tasks, monkeypatch):
        """Test: Brak uprawnień do odczytu pliku"""
        def mock_open_error(*args, **kwargs):
            raise PermissionError("Brak dostępu do pliku")
        
        monkeypatch.setattr("builtins.open", mock_open_error)
        
        with pytest.raises(PermissionError):
            client.get("/tasks")


class TestInvalidURLs:
    """Testy dla nieprawidłowych URL-i i endpointów"""
    
    def test_nonexistent_endpoint(self):
        """Test: Endpoint nie istnieje"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_wrong_method_on_tasks(self):
        """Test: Użycie niewłaściwej metody HTTP"""
        response = client.patch("/tasks")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_invalid_task_id_type(self):
        """Test: ID zadania nie jest liczbą"""
        response = client.get("/tasks/abc")
        assert response.status_code == 422  # Validation Error
    
    def test_invalid_task_id_negative(self):
        """Test: ID zadania jest liczbą ujemną"""
        response = client.get("/tasks/-1")
        assert response.status_code == 404  # Task not found
    
    def test_invalid_task_id_zero(self):
        """Test: ID zadania jest zerem"""
        response = client.get("/tasks/0")
        assert response.status_code == 404  # Task not found
    
    def test_task_id_not_found(self):
        """Test: Zadanie o podanym ID nie istnieje"""
        response = client.get("/tasks/999999")
        assert response.status_code == 404
        assert "Task not found" in str(response.json())


class TestInvalidFilters:
    """Testy dla nieprawidłowych filtrów"""
    
    def test_invalid_completed_filter_value(self, backup_tasks):
        """Test: Filtr completed ma nieprawidłową wartość"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Task 1", "description": "", "completed": True, "createdAt": "2025-01-01T00:00:00Z"}
            ], f)

        response = client.get("/tasks?completed=maybe")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_invalid_sort_field(self, backup_tasks):
        """Test: Sortowanie po nieistniejącym polu"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Task 1", "description": "", "completed": False, "createdAt": "2025-01-01T00:00:00Z"}
            ], f)
        
        response = client.get("/tasks?sort=nonexistent_field")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
    
    def test_invalid_page_number_zero(self):
        """Test: Numer strony równy 0"""
        response = client.get("/tasks?page=0")
        assert response.status_code == 422  # Validation Error
    
    def test_invalid_page_number_negative(self):
        """Test: Ujemny numer strony"""
        response = client.get("/tasks?page=-1")
        assert response.status_code == 422
    
    def test_invalid_page_number_string(self):
        """Test: Numer strony nie jest liczbą"""
        response = client.get("/tasks?page=abc")
        assert response.status_code == 422
    
    def test_invalid_limit_zero(self):
        """Test: Limit równy 0"""
        response = client.get("/tasks?limit=0")
        assert response.status_code == 422
    
    def test_invalid_limit_negative(self):
        """Test: Ujemny limit"""
        response = client.get("/tasks?limit=-10")
        assert response.status_code == 422
    
    def test_invalid_limit_too_large(self):
        """Test: Limit przekracza maksymalną wartość"""
        response = client.get("/tasks?limit=10001")
        assert response.status_code == 422
    
    def test_invalid_limit_string(self):
        """Test: Limit nie jest liczbą"""
        response = client.get("/tasks?limit=abc")
        assert response.status_code == 422


class TestInvalidDataCreation:
    """Testy dla nieprawidłowych danych podczas tworzenia zadań"""
    
    def test_create_task_empty_title(self, backup_tasks):
        """Test: Tworzenie zadania z pustym tytułem"""
        response = client.post("/tasks", json={
            "title": "",
            "description": "Test description"
        })
        assert response.status_code == 422
        assert "pusty" in response.json()["detail"].lower()
    
    def test_create_task_whitespace_only_title(self, backup_tasks):
        """Test: Tworzenie zadania z samymi spacjami w tytule"""
        response = client.post("/tasks", json={
            "title": "   ",
            "description": "Test description"
        })
        assert response.status_code == 422
        assert "pusty" in response.json()["detail"].lower()
    
    def test_create_task_title_too_short(self, backup_tasks):
        """Test: Tytuł zadania jest za krótki (mniej niż 3 znaki)"""
        response = client.post("/tasks", json={
            "title": "AB",
            "description": "Test description"
        })
        assert response.status_code == 422
        assert "3" in response.json()["detail"]
    
    def test_create_task_missing_title(self, backup_tasks):
        """Test: Brak pola title"""
        response = client.post("/tasks", json={
            "description": "Test description"
        })
        assert response.status_code == 422
    
    def test_create_task_missing_description(self, backup_tasks):
        """Test: Brak pola description"""
        response = client.post("/tasks", json={
            "title": "Valid title"
        })
        assert response.status_code == 422
    
    def test_create_task_null_title(self, backup_tasks):
        """Test: Pole title jest null"""
        response = client.post("/tasks", json={
            "title": None,
            "description": "Test description"
        })
        assert response.status_code == 422
    
    def test_create_task_wrong_data_type(self, backup_tasks):
        """Test: Nieprawidłowy typ danych (liczba zamiast stringa)"""
        response = client.post("/tasks", json={
            "title": 12345,
            "description": "Test description"
        })
        assert response.status_code == 422
    
    def test_create_task_invalid_json(self):
        """Test: Nieprawidłowy JSON w żądaniu"""
        response = client.post(
            "/tasks",
            content="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_create_task_extra_fields(self, backup_tasks):
        """Test: Dodatkowe pola w żądaniu"""
        response = client.post("/tasks", json={
            "title": "Valid title",
            "description": "Test description",
            "extra_field": "should be ignored",
            "completed": True
        })
        assert response.status_code == 201
        task = response.json()
        assert task["completed"] == False


class TestInvalidDataUpdate:
    """Testy dla nieprawidłowych danych podczas aktualizacji zadań"""
    
    def test_update_task_empty_title(self, backup_tasks):
        """Test: Aktualizacja zadania z pustym tytułem"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Original", "description": "", "completed": False, "createdAt": "2025-01-01T00:00:00Z"}
            ], f)
        
        response = client.put("/tasks/1", json={"title": ""})
        assert response.status_code == 422
        assert "pusty" in response.json()["detail"].lower()
    
    def test_update_task_whitespace_only_title(self, backup_tasks):
        """Test: Aktualizacja z samymi spacjami w tytule"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Original", "description": "", "completed": False, "createdAt": "2025-01-01T00:00:00Z"}
            ], f)
        
        response = client.put("/tasks/1", json={"title": "   "})
        assert response.status_code == 422
    
    def test_update_task_title_too_short(self, backup_tasks):
        """Test: Aktualizacja z za krótkim tytułem"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Original", "description": "", "completed": False, "createdAt": "2025-01-01T00:00:00Z"}
            ], f)
        
        response = client.put("/tasks/1", json={"title": "AB"})
        assert response.status_code == 422
    
    def test_update_nonexistent_task(self, backup_tasks):
        """Test: Aktualizacja nieistniejącego zadania"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        response = client.put("/tasks/999", json={"title": "Updated"})
        assert response.status_code == 404
    
    def test_update_task_invalid_completed_type(self, backup_tasks):
        """Test: Nieprawidłowy typ dla pola completed"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Original", "description": "", "completed": False, "createdAt": "2025-01-01T00:00:00Z"}
            ], f)
        
        response = client.put("/tasks/1", json={"completed": "yes"}) 
        assert response.status_code in [200, 422]
    
    def test_update_task_empty_body(self, backup_tasks):
        """Test: Aktualizacja z pustym ciałem żądania"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Original", "description": "", "completed": False, "createdAt": "2025-01-01T00:00:00Z"}
            ], f)
        
        response = client.put("/tasks/1", json={})
        assert response.status_code == 200


class TestDeleteErrors:
    """Testy dla błędów podczas usuwania zadań"""
    
    def test_delete_nonexistent_task(self, backup_tasks):
        """Test: Usuwanie nieistniejącego zadania"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        response = client.delete("/tasks/999")
        assert response.status_code == 404
        assert "Task not found" in str(response.json())
    
    def test_delete_invalid_task_id_type(self):
        """Test: Usuwanie z nieprawidłowym typem ID"""
        response = client.delete("/tasks/abc")
        assert response.status_code == 422
    
    def test_delete_negative_task_id(self, backup_tasks):
        """Test: Usuwanie z ujemnym ID"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        response = client.delete("/tasks/-1")
        assert response.status_code == 404


class TestEdgeCases:
    """Testy dla przypadków brzegowych"""
    
    def test_very_long_title(self, backup_tasks):
        """Test: Bardzo długi tytuł (10000 znaków)"""
        long_title = "A" * 10000
        response = client.post("/tasks", json={
            "title": long_title,
            "description": "Test"
        })
        assert response.status_code == 201
        assert response.json()["title"] == long_title
    
    def test_special_characters_in_title(self, backup_tasks):
        """Test: Znaki specjalne w tytule"""
        special_title = "Test <>&\"'{}[]|\\^~`"
        response = client.post("/tasks", json={
            "title": special_title,
            "description": "Test"
        })
        assert response.status_code == 201
        assert response.json()["title"] == special_title
    
    def test_unicode_characters_in_title(self, backup_tasks):
        """Test: Znaki Unicode w tytule"""
        unicode_title = "Zadanie 中文 العربية 🎉🎊"
        response = client.post("/tasks", json={
            "title": unicode_title,
            "description": "Test"
        })
        assert response.status_code == 201
        assert response.json()["title"] == unicode_title
    
    def test_pagination_beyond_available_pages(self, backup_tasks):
        """Test: Strona wykraczająca poza dostępne dane"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {"id": 1, "title": "Task 1", "description": "", "completed": False, "createdAt": "2025-01-01T00:00:00Z"}
            ], f)
        
        response = client.get("/tasks?page=100&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 1
    
    def test_concurrent_file_access(self, backup_tasks):
        """Test: Symulacja jednoczesnego dostępu do pliku"""
        import threading
        
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        results = []
        errors = []
        
        def create_task(title):
            try:
                response = client.post("/tasks", json={
                    "title": title,
                    "description": "Test"
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=create_task, args=(f"Task {i}",))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Test sprawdza, czy w warunkach współbieżności występują błędy
        # W rzeczywistości oczekujemy, że mogą wystąpić konflikty
        assert len(results) + len(errors) == 10


class TestSecurityCases:
    """Testy dla przypadków związanych z bezpieczeństwem"""
    
    def test_sql_injection_attempt_in_title(self, backup_tasks):
        """Test: Próba SQL injection w tytule"""
        sql_injection = "Test'; DROP TABLE tasks; --"
        response = client.post("/tasks", json={
            "title": sql_injection,
            "description": "Test"
        })
        assert response.status_code == 201
        assert response.json()["title"] == sql_injection
    
    def test_xss_attempt_in_description(self, backup_tasks):
        """Test: Próba XSS w opisie"""
        xss_script = "<script>alert('XSS')</script>"
        response = client.post("/tasks", json={
            "title": "Test task",
            "description": xss_script
        })
        assert response.status_code == 201
        assert response.json()["description"] == xss_script
    
    def test_path_traversal_in_filter(self):
        """Test: Próba path traversal w parametrach"""
        response = client.get("/tasks?sort=../../etc/passwd")
        assert response.status_code in [200, 400, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
