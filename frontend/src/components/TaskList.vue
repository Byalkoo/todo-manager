<script setup>
import TaskItem from "./TaskItem.vue";

defineProps({
  tasks: Array,
});

defineEmits(["toggle-task", "delete-task", "edit-task"]);
</script>

<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <div
          class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center"
        >
          <svg
            class="w-5 h-5 text-indigo-600"
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
        <h2 class="text-xl font-bold text-gray-900">Twoje zadania</h2>
      </div>
      <span
        class="bg-indigo-100 text-indigo-800 text-sm font-medium px-3 py-1 rounded-full"
      >
        {{ tasks.length }}
      </span>
    </div>

    <div v-if="tasks.length === 0" class="text-center py-12">
      <div
        class="w-20 h-20 bg-gray-100 rounded-full mx-auto mb-4 flex items-center justify-center"
      >
        <svg
          class="w-10 h-10 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          ></path>
        </svg>
      </div>
      <p class="text-lg text-gray-500 font-medium">Brak zadań</p>
      <p class="text-gray-400 mt-1">Dodaj pierwsze zadanie aby zacząć!</p>
    </div>

    <div v-else class="space-y-3">
      <TaskItem
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @toggle="$emit('toggle-task', task)"
        @delete="$emit('delete-task', task.id)"
        @edit="$emit('edit-task', task)"
      />
    </div>
  </div>
</template>
