# TODO API - Menadżer Zadań

**Autor:** Stanisław Potrykus
**Grupa:** ININ4_hybryda
**Data:** 23.11.2025

## Opis projektu

REST API dla menadżera zadań z zapisem do pliku JSON oraz frontend w Vue 3.

## Technologie

- Python 3.8+
- FastAPI
- Vue 3 (Composition API)
- Vite
- Tailwind CSS
- JSON (przechowywanie danych)

## Instalacja i uruchomienie

### Wymagania

- Python 3.8 lub nowszy
- Node.js 16+ i npm

### Krok po kroku

#### Backend:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend uruchomi się na `http://localhost:8000`

#### Frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend uruchomi się na `http://localhost:5173`

## Endpointy API

### 1. GET /health

Sprawdza status API

```bash
curl http://localhost:8000/health
```

Odpowiedź:

```json
{
  "status": "OK",
  "timestamp": "2024-11-15T10:30:00Z"
}
```

### 2. GET /tasks

Pobiera wszystkie zadania

```bash
curl http://localhost:8000/tasks
```

Odpowiedź:

```json
[
  {
    "id": 1,
    "title": "Zrobić zakupy",
    "description": "Mleko, chleb, masło",
    "completed": false,
    "createdAt": "2024-11-15T10:00:00Z"
  }
]
```

### 3. POST /tasks

Dodaje nowe zadanie

```bash
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Nowe zadanie\",\"description\":\"Opis\"}"
```

Odpowiedź (201):

```json
{
  "id": 2,
  "title": "Nowe zadanie",
  "description": "Opis",
  "completed": false,
  "createdAt": "2024-11-15T12:00:00Z"
}
```

### 4. PUT /tasks/:id

Modyfikuje istniejące zadanie

```bash
curl -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d "{\"title\":\"Zaktualizowany\",\"completed\":true}"
```

Odpowiedź (200):

```json
{
  "id": 1,
  "title": "Zaktualizowany",
  "description": "Opis",
  "completed": true,
  "createdAt": "2024-11-15T10:00:00Z",
  "updatedAt": "2024-11-15T13:00:00Z"
}
```

### 5. DELETE /tasks/:id

Usuwa zadanie

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

### 6. GET /tasks/:id

Pobiera pojedyncze zadanie

```bash
curl http://localhost:8000/tasks/1
```

### Dodatkowe funkcje API

**Filtrowanie po statusie:**

```bash
curl "http://localhost:8000/tasks?completed=true"
curl "http://localhost:8000/tasks?completed=false"
```

**Sortowanie:**

```bash
curl "http://localhost:8000/tasks?sort=title"
curl "http://localhost:8000/tasks?sort=createdAt"
```

**Paginacja:**

```bash
curl "http://localhost:8000/tasks?page=1&limit=10"
```

## Testowanie

Frontend posiada interfejs użytkownika dostępny po uruchomieniu `npm run dev`:

- Sprawdzenie statusu API
- Dodawanie zadań
- Oznaczanie jako zakończone
- Usuwanie zadań

Można też testować API bezpośrednio:

- Thunder Client (VS Code)
- Postman
- curl (linia komend)

## Struktura projektu

```
projekt/
├── backend/
│   ├── main.py
│   ├── tasks.json
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TaskForm.vue
│   │   │   ├── TaskList.vue
│   │   │   └── TaskItem.vue
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── README.md
└── .gitignore
```

## Funkcjonalności

### Backend:

- ✅ GET /health - status API
- ✅ GET /tasks - lista zadań z filtrowaniem i sortowaniem
- ✅ GET /tasks/:id - pojedyncze zadanie
- ✅ POST /tasks - dodawanie zadań
- ✅ PUT /tasks/:id - edycja zadań
- ✅ DELETE /tasks/:id - usuwanie zadań
- ✅ Zapis do pliku JSON
- ✅ Walidacja danych (tytuł min 3 znaki)
- ✅ Obsługa błędów (404, 400, 500, 422)
- ✅ CORS dla frontendu
- ✅ Logowanie requestów do api.log
- ✅ Filtrowanie po statusie (completed)
- ✅ Sortowanie (title, createdAt)
- ✅ Paginacja (page, limit)

### Frontend:

- ✅ Sprawdzanie statusu API
- ✅ Wyświetlanie listy zadań
- ✅ Dodawanie nowych zadań
- ✅ Edycja zadań (modal)
- ✅ Oznaczanie jako zakończone/niezakończone
- ✅ Usuwanie zadań
- ✅ Filtrowanie zadań (wszystkie/zakończone/do zrobienia)
- ✅ Sortowanie (najnowsze/alfabetycznie)
- ✅ System powiadomień (toast notifications)
- ✅ Walidacja z wyświetlaniem błędów
- ✅ Responsive design z Tailwind CSS
- ✅ Komponenty Vue 3 (Composition API)
- ✅ Ładny interfejs użytkownika z Flowbite

## Napotkane problemy i rozwiązania

1. **CORS** - Dodano middleware w FastAPI
2. **Encoding** - Użyto UTF-8 dla polskich znaków w JSON
3. **Brak pliku tasks.json** - Automatyczne tworzenie przy pierwszym zapisie
4. **Walidacja** - Pydantic validators dla backendowej walidacji danych
5. **Tailwind v4** - Przejście na stabilną wersję v3 z powodu problemów z konfiguracją
