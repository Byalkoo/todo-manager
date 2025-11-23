# Dokumentacja Testów Błędów - Todo Manager API

## Przegląd

Plik `test_error_cases.py` zawiera kompleksowe testy dla różnych scenariuszy błędów w aplikacji Todo Manager API. Testy sprawdzają odporność aplikacji na:

- Uszkodzone pliki danych
- Nieprawidłowe URL-e i endpointy
- Nieprawidłowe filtry i parametry
- Nieprawidłowe dane wejściowe
- Próby ataków bezpieczeństwa

## Statystyki

- **Łączna liczba testów:** 46
- **Status:** ✅ Wszystkie testy przechodzą
- **Kategorie testów:** 7

## Kategorie Testów

### 1. TestCorruptedTasksFile (5 testów)

Testy sprawdzające zachowanie aplikacji przy uszkodzonym pliku `tasks.json`:

- ✅ `test_corrupted_json_file` - Uszkodzona składnia JSON
- ✅ `test_empty_corrupted_file` - Pusty plik
- ✅ `test_non_list_json_structure` - JSON nie jest listą
- ✅ `test_tasks_with_missing_fields` - Brakujące pola w zadaniach
- ✅ `test_file_permission_error` - Brak uprawnień do odczytu

**Cel:** Zapewnienie, że aplikacja nie crashuje przy problemach z plikiem danych.

### 2. TestInvalidURLs (6 testów)

Testy dla nieprawidłowych URL-i i endpointów:

- ✅ `test_nonexistent_endpoint` - Nieistniejący endpoint (404)
- ✅ `test_wrong_method_on_tasks` - Niewłaściwa metoda HTTP (405)
- ✅ `test_invalid_task_id_type` - ID nie jest liczbą (422)
- ✅ `test_invalid_task_id_negative` - Ujemne ID (404)
- ✅ `test_invalid_task_id_zero` - ID równe zero (404)
- ✅ `test_task_id_not_found` - Zadanie nie istnieje (404)

**Cel:** Weryfikacja poprawnej obsługi błędnych URL-i i metod HTTP.

### 3. TestInvalidFilters (10 testów)

Testy dla nieprawidłowych parametrów filtrowania i paginacji:

- ✅ `test_invalid_completed_filter_value` - Nieprawidłowa wartość filtru completed
- ✅ `test_invalid_sort_field` - Sortowanie po nieistniejącym polu
- ✅ `test_invalid_page_number_zero` - Strona = 0 (422)
- ✅ `test_invalid_page_number_negative` - Ujemny numer strony (422)
- ✅ `test_invalid_page_number_string` - Strona nie jest liczbą (422)
- ✅ `test_invalid_limit_zero` - Limit = 0 (422)
- ✅ `test_invalid_limit_negative` - Ujemny limit (422)
- ✅ `test_invalid_limit_too_large` - Limit > 10000 (422)
- ✅ `test_invalid_limit_string` - Limit nie jest liczbą (422)

**Cel:** Sprawdzenie walidacji parametrów zapytań.

### 4. TestInvalidDataCreation (9 testów)

Testy dla nieprawidłowych danych podczas tworzenia zadań:

- ✅ `test_create_task_empty_title` - Pusty tytuł (422)
- ✅ `test_create_task_whitespace_only_title` - Same spacje w tytule (422)
- ✅ `test_create_task_title_too_short` - Tytuł < 3 znaki (422)
- ✅ `test_create_task_missing_title` - Brak pola title (422)
- ✅ `test_create_task_missing_description` - Brak pola description (422)
- ✅ `test_create_task_null_title` - Tytuł = null (422)
- ✅ `test_create_task_wrong_data_type` - Liczba zamiast tekstu (422)
- ✅ `test_create_task_invalid_json` - Nieprawidłowy JSON (422)
- ✅ `test_create_task_extra_fields` - Dodatkowe pola (ignorowane)

**Cel:** Weryfikacja walidacji danych przy tworzeniu zadań.

### 5. TestInvalidDataUpdate (6 testów)

Testy dla nieprawidłowych danych podczas aktualizacji:

- ✅ `test_update_task_empty_title` - Pusty tytuł (422)
- ✅ `test_update_task_whitespace_only_title` - Same spacje (422)
- ✅ `test_update_task_title_too_short` - Tytuł < 3 znaki (422)
- ✅ `test_update_nonexistent_task` - Aktualizacja nieistniejącego zadania (404)
- ✅ `test_update_task_invalid_completed_type` - Nieprawidłowy typ completed
- ✅ `test_update_task_empty_body` - Puste ciało żądania (200 - OK)

**Cel:** Sprawdzenie walidacji przy aktualizacji zadań.

### 6. TestDeleteErrors (3 testy)

Testy błędów przy usuwaniu zadań:

- ✅ `test_delete_nonexistent_task` - Usuwanie nieistniejącego zadania (404)
- ✅ `test_delete_invalid_task_id_type` - Nieprawidłowy typ ID (422)
- ✅ `test_delete_negative_task_id` - Ujemne ID (404)

**Cel:** Weryfikacja obsługi błędów przy usuwaniu.

### 7. TestEdgeCases (4 testy)

Testy przypadków brzegowych:

- ✅ `test_very_long_title` - Bardzo długi tytuł (10000 znaków)
- ✅ `test_special_characters_in_title` - Znaki specjalne w tytule
- ✅ `test_unicode_characters_in_title` - Znaki Unicode (emoji, chiński, arabski)
- ✅ `test_pagination_beyond_available_pages` - Strona poza zakresem
- ✅ `test_concurrent_file_access` - Jednoczesny dostęp do pliku

**Cel:** Sprawdzenie zachowania w nietypowych sytuacjach.

### 8. TestSecurityCases (3 testy)

Testy bezpieczeństwa:

- ✅ `test_sql_injection_attempt_in_title` - Próba SQL injection
- ✅ `test_xss_attempt_in_description` - Próba XSS
- ✅ `test_path_traversal_in_filter` - Próba path traversal

**Cel:** Sprawdzenie odporności na podstawowe ataki.

## Uruchomienie Testów

### Instalacja zależności

```powershell
pip install pytest httpx
```

### Uruchomienie wszystkich testów

```powershell
pytest test_error_cases.py -v
```

### Uruchomienie konkretnej klasy testów

```powershell
pytest test_error_cases.py::TestInvalidDataCreation -v
```

### Uruchomienie konkretnego testu

```powershell
pytest test_error_cases.py::TestInvalidDataCreation::test_create_task_empty_title -v
```

### Uruchomienie z krótszym logowaniem

```powershell
pytest test_error_cases.py -v --tb=short
```

## Pokrycie Kodu

Testy sprawdzają następujące aspekty API:

- ✅ Walidacja danych wejściowych (Pydantic validators)
- ✅ Obsługa błędów HTTP (404, 405, 422)
- ✅ Walidacja parametrów zapytań
- ✅ Obsługa uszkodzonych plików JSON
- ✅ Obsługa problemów z uprawnieniami
- ✅ Bezpieczeństwo przed atakami
- ✅ Przypadki brzegowe (długie stringi, Unicode, etc.)
- ✅ Wielowątkowość

## Znane Ostrzeżenia

### Deprecation Warnings

- **Pydantic V1 validators** - Używane `@validator` zamiast `@field_validator`
- **datetime.utcnow()** - Powinno używać `datetime.now(datetime.UTC)`

Te ostrzeżenia nie wpływają na działanie testów, ale powinny być naprawione w przyszłości.

### Thread Warnings

Test `test_concurrent_file_access` generuje ostrzeżenia o wyjątkach w wątkach - jest to oczekiwane zachowanie testujące race conditions.

## Rekomendacje

### Dla Aplikacji

1. Dodać obsługę błędów JSON w `read_tasks()` z odpowiednimi komunikatami błędów
2. Dodać walidację parametru `sort` (tylko dozwolone wartości)
3. Rozważyć użycie bazy danych zamiast pliku JSON dla lepszej współbieżności
4. Migrować do Pydantic V2 validators

### Dla Testów

1. Dodać testy wydajnościowe (performance tests)
2. Dodać testy integracyjne z prawdziwą bazą danych
3. Dodać coverage report
4. Rozważyć użycie parametryzacji dla podobnych testów

## Podsumowanie

Zestaw testów zapewnia solidną ochronę przed najczęstszymi błędami i problemami:

- **46 testów** pokrywa różne scenariusze błędów
- **100% pass rate** - wszystkie testy przechodzą
- **7 kategorii** organizuje testy logicznie
- **Kompleksowe pokrycie** - od walidacji danych po bezpieczeństwo

Testy pomagają zapewnić, że API jest odporne na nieprawidłowe dane i nietypowe sytuacje.
