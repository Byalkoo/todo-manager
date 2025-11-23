<script setup>
import { ref, onMounted, computed } from "vue";
import TaskList from "./components/TaskList.vue";
import TaskForm from "./components/TaskForm.vue";
import EditTaskModal from "./components/EditTaskModal.vue";
import Notification from "./components/Notification.vue";

const API_URL = "http://localhost:8000";
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

const showNotification = (message, type = "error") => {
  console.log("showNotification wywołane:", { message, type });
  notification.value = {
    show: true,
    message,
    type,
  };
  console.log("notification.value ustawione na:", notification.value);
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

const loadTasks = async () => {
  try {
    // Zawsze ładuj wszystkie zadania do statystyk
    const allResponse = await fetch(`${API_URL}/tasks?limit=1000`);
    const allData = await allResponse.json();
    allTasks.value = allData.tasks || allData;

    // Ładuj przefiltrowane zadania do wyświetlenia
    let url = `${API_URL}/tasks?sort=${sortBy.value}`;
    if (filterCompleted.value !== "all") {
      url += `&completed=${filterCompleted.value}`;
    }

    const response = await fetch(url);
    const data = await response.json();
    tasks.value = data.tasks || data;
  } catch (error) {
    console.error("Błąd ładowania zadań:", error);
    showNotification("Nie udało się załadować zadań", "error");
  }
};

const addTask = async (taskData) => {
  try {
    console.log("Wysyłam zadanie:", taskData);
    const response = await fetch(`${API_URL}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(taskData),
    });

    console.log("Response status:", response.status);

    if (!response.ok) {
      const error = await response.json();
      console.log("Otrzymany błąd:", error);
      const errorMsg = error.detail || "Błąd dodawania zadania";
      console.log("Wyświetlam powiadomienie:", errorMsg);
      showNotification(errorMsg, "error");
      return;
    }

    await loadTasks();
    showNotification("Zadanie dodane pomyślnie!", "success");
  } catch (error) {
    console.error("Błąd dodawania zadania:", error);
    showNotification("Nie udało się dodać zadania", "error");
  }
};

const toggleTask = async (task) => {
  try {
    const response = await fetch(`${API_URL}/tasks/${task.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !task.completed }),
    });
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
    });
    if (response.ok) {
      await loadTasks();
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
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedData),
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMsg = error.detail || "Błąd edycji zadania";
      showNotification(errorMsg, "error");
      return;
    }

    await loadTasks();
    closeEditModal();
    showNotification("Zadanie zaktualizowane!", "success");
  } catch (error) {
    console.error("Błąd edycji zadania:", error);
    showNotification("Nie udało się edytować zadania", "error");
  }
};

onMounted(() => {
  checkHealth();
  loadTasks();
});

const completedCount = computed(
  () => allTasks.value.filter((t) => t.completed).length
);
const pendingCount = computed(
  () => allTasks.value.filter((t) => !t.completed).length
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

          <div>
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
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 py-8">
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
                  <svg
                    class="w-4 h-4 inline mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                    ></path>
                  </svg>
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
                  <svg
                    class="w-4 h-4 inline mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
                    ></path>
                  </svg>
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
