<script setup>
import { ref, onMounted, computed } from "vue";
import TaskList from "./components/TaskList.vue";
import TaskForm from "./components/TaskForm.vue";
import EditTaskModal from "./components/EditTaskModal.vue";
import Notification from "./components/Notification.vue";

const API_URL = "http://localhost:3000";
const apiStatus = ref(false);
const tasks = ref([]);
const allTasks = ref([]);
const editingTask = ref(null);
const showEditModal = ref(false);
const notification = ref({
  show: false,
  message: "",
  type: "error",
});
const filterCompleted = ref("all");
const sortBy = ref("createdAt");

const isLoggedIn = ref(false);
const showLoginForm = ref(true);
const currentUser = ref(null);
const authForm = ref({
  email: "",
  password: "",
});
const authLoading = ref(false);

const getToken = () => localStorage.getItem("token");
const setToken = (token) => localStorage.setItem("token", token);
const removeToken = () => localStorage.removeItem("token");

const getAuthHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${getToken()}`,
});

const showNotification = (message, type = "error") => {
  notification.value = {
    show: true,
    message,
    type,
  };
};

const closeNotification = () => {
  notification.value.show = false;
};

const checkHealth = async () => {
  try {
    const response = await fetch(`${API_URL}/health`);
    apiStatus.value = response.ok;
  } catch (error) {
    apiStatus.value = false;
  }
};

const login = async () => {
  authLoading.value = true;
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: authForm.value.email,
        password: authForm.value.password,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      showNotification(error.detail?.error || "Błąd logowania", "error");
      return;
    }

    const data = await response.json();
    setToken(data.token);
    currentUser.value = data.user;
    isLoggedIn.value = true;
    authForm.value = { email: "", password: "" };
    showNotification("Zalogowano pomyślnie!", "success");
    await loadTasks();
  } catch (error) {
    showNotification("Nie udało się zalogować", "error");
  } finally {
    authLoading.value = false;
  }
};

const register = async () => {
  authLoading.value = true;
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: authForm.value.email,
        password: authForm.value.password,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      showNotification(error.detail?.error || "Błąd rejestracji", "error");
      return;
    }

    showNotification("Konto utworzone! Możesz się teraz zalogować.", "success");
    showLoginForm.value = true;
  } catch (error) {
    showNotification("Nie udało się zarejestrować", "error");
  } finally {
    authLoading.value = false;
  }
};

const logout = () => {
  removeToken();
  isLoggedIn.value = false;
  currentUser.value = null;
  tasks.value = [];
  allTasks.value = [];
  showNotification("Wylogowano", "success");
};

const loadTasks = async () => {
  if (!isLoggedIn.value) return;

  try {
    const response = await fetch(`${API_URL}/tasks`, {
      headers: getAuthHeaders(),
    });

    if (response.status === 401) {
      logout();
      showNotification("Sesja wygasła, zaloguj się ponownie", "error");
      return;
    }

    if (!response.ok) {
      throw new Error("Failed to load tasks");
    }

    const data = await response.json();
    allTasks.value = data;

    if (filterCompleted.value === "all") {
      tasks.value = data;
    } else {
      const filterBool = filterCompleted.value === "true";
      tasks.value = data.filter((t) => t.completed === filterBool);
    }

    if (sortBy.value === "title") {
      tasks.value.sort((a, b) => a.title.localeCompare(b.title));
    } else {
      tasks.value.sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at),
      );
    }
  } catch (error) {
    console.error("Błąd ładowania zadań:", error);
    showNotification("Nie udało się załadować zadań", "error");
  }
};

const addTask = async (taskData) => {
  try {
    const response = await fetch(`${API_URL}/tasks`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ title: taskData.title }),
    });

    if (response.status === 401) {
      logout();
      return;
    }

    if (!response.ok) {
      const error = await response.json();
      showNotification(
        error.detail?.error || "Błąd dodawania zadania",
        "error",
      );
      return;
    }

    await loadTasks();
    showNotification("Zadanie dodane pomyślnie!", "success");
  } catch (error) {
    showNotification("Nie udało się dodać zadania", "error");
  }
};

const toggleTask = async (task) => {
  try {
    const response = await fetch(`${API_URL}/tasks/${task.id}`, {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify({ completed: !task.completed }),
    });

    if (response.status === 401) {
      logout();
      return;
    }

    if (response.ok) {
      await loadTasks();
    }
  } catch (error) {
    console.error("Błąd aktualizacji zadania:", error);
  }
};

const deleteTask = async (id) => {
  if (!confirm("Czy na pewno usunąć to zadanie?")) return;

  try {
    const response = await fetch(`${API_URL}/tasks/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    if (response.status === 401) {
      logout();
      return;
    }

    if (response.ok || response.status === 204) {
      await loadTasks();
      showNotification("Zadanie usunięte", "success");
    }
  } catch (error) {
    console.error("Błąd usuwania zadania:", error);
  }
};

const openEditModal = (task) => {
  editingTask.value = task;
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingTask.value = null;
};

const saveEditedTask = async (updatedData) => {
  try {
    const response = await fetch(`${API_URL}/tasks/${editingTask.value.id}`, {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify(updatedData),
    });

    if (response.status === 401) {
      logout();
      return;
    }

    if (!response.ok) {
      const error = await response.json();
      showNotification(error.detail?.error || "Błąd edycji zadania", "error");
      return;
    }

    await loadTasks();
    closeEditModal();
    showNotification("Zadanie zaktualizowane!", "success");
  } catch (error) {
    showNotification("Nie udało się edytować zadania", "error");
  }
};

const checkExistingSession = () => {
  const token = getToken();
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const exp = payload.exp * 1000;
      if (Date.now() < exp) {
        isLoggedIn.value = true;
        currentUser.value = {
          id: payload.sub,
          email: payload.email,
          role: payload.user_role || "user",
        };
        return true;
      }
    } catch (e) {
      removeToken();
    }
  }
  return false;
};

onMounted(async () => {
  checkHealth();
  if (checkExistingSession()) {
    await loadTasks();
  }
});

const completedCount = computed(
  () => allTasks.value.filter((t) => t.completed).length,
);
const pendingCount = computed(
  () => allTasks.value.filter((t) => !t.completed).length,
);
const progressPercentage = computed(() => {
  if (allTasks.value.length === 0) return 0;
  return Math.round((completedCount.value / allTasks.value.length) * 100);
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                ></path>
              </svg>
            </div>
            <h1 class="text-2xl font-bold text-gray-900">TODO Manager</h1>
          </div>

          <div class="flex items-center gap-4">
            <span
              class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium"
              :class="
                apiStatus
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              "
            >
              <span
                class="w-2 h-2 rounded-full mr-2"
                :class="apiStatus ? 'bg-green-500' : 'bg-red-500'"
              ></span>
              {{ apiStatus ? "API Connected" : "API Disconnected" }}
            </span>

            <div v-if="isLoggedIn" class="flex items-center gap-3">
              <span class="text-sm text-gray-600">
                {{ currentUser?.email }}
                <span
                  v-if="currentUser?.role === 'admin'"
                  class="ml-1 px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs font-medium"
                >
                  Admin
                </span>
              </span>
              <button
                @click="logout"
                class="px-3 py-1.5 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
              >
                Wyloguj
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <div v-if="!isLoggedIn" class="max-w-md mx-auto px-4 py-16">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <h2 class="text-2xl font-bold text-center text-gray-900 mb-6">
          {{ showLoginForm ? "Logowanie" : "Rejestracja" }}
        </h2>

        <form
          @submit.prevent="showLoginForm ? login() : register()"
          class="space-y-4"
        >
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Email</label
            >
            <input
              v-model="authForm.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="twoj@email.com"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Hasło</label
            >
            <input
              v-model="authForm.password"
              type="password"
              required
              minlength="6"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Minimum 6 znaków"
            />
          </div>

          <button
            type="submit"
            :disabled="authLoading"
            class="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium rounded-lg transition-colors"
          >
            {{
              authLoading
                ? "Proszę czekać..."
                : showLoginForm
                  ? "Zaloguj się"
                  : "Zarejestruj się"
            }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <button
            @click="showLoginForm = !showLoginForm"
            class="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
          >
            {{
              showLoginForm
                ? "Nie masz konta? Zarejestruj się"
                : "Masz już konto? Zaloguj się"
            }}
          </button>
        </div>
      </div>
    </div>

    <div v-else class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1">
          <TaskForm @add-task="addTask" />

          <div class="mt-6 bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Statystyki</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-gray-600">Wszystkie zadania</span>
                <span class="font-bold text-indigo-600 text-lg">{{
                  allTasks.length
                }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-gray-600">Zakończone</span>
                <span class="font-bold text-green-600 text-lg">{{
                  completedCount
                }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-gray-600">Do zrobienia</span>
                <span class="font-bold text-orange-600 text-lg">{{
                  pendingCount
                }}</span>
              </div>
              <div class="mt-4 pt-4 border-t">
                <div class="flex justify-between text-sm mb-2">
                  <span class="font-medium text-gray-700">Postęp</span>
                  <span class="font-bold text-indigo-600"
                    >{{ progressPercentage }}%</span
                  >
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div
                    class="bg-indigo-600 h-3 rounded-full transition-all duration-500"
                    :style="{ width: progressPercentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow p-4 mb-6">
            <div class="flex flex-wrap gap-4 items-end">
              <div class="flex-1 min-w-[200px]">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Filtruj po statusie
                </label>
                <select
                  v-model="filterCompleted"
                  @change="loadTasks"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm bg-white"
                >
                  <option value="all">Wszystkie zadania</option>
                  <option value="false">Do zrobienia</option>
                  <option value="true">Zakończone</option>
                </select>
              </div>

              <div class="flex-1 min-w-[200px]">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Sortuj
                </label>
                <select
                  v-model="sortBy"
                  @change="loadTasks"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm bg-white"
                >
                  <option value="createdAt">Najnowsze</option>
                  <option value="title">Alfabetycznie</option>
                </select>
              </div>

              <div>
                <button
                  @click="
                    filterCompleted = 'all';
                    sortBy = 'createdAt';
                    loadTasks();
                  "
                  class="px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Resetuj
                </button>
              </div>
            </div>
          </div>

          <TaskList
            :tasks="tasks"
            @toggle-task="toggleTask"
            @delete-task="deleteTask"
            @edit-task="openEditModal"
          />
        </div>
      </div>
    </div>

    <EditTaskModal
      :task="editingTask"
      :show="showEditModal"
      @close="closeEditModal"
      @save="saveEditedTask"
    />

    <Notification
      :show="notification.show"
      :message="notification.message"
      :type="notification.type"
      @close="closeNotification"
    />
  </div>
</template>
