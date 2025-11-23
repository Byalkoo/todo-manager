<script setup>
defineProps({
  task: Object,
});

defineEmits(["toggle", "delete", "edit"]);

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString("pl-PL");
};
</script>

<template>
  <div
    class="p-4 rounded-lg border-2 transition-all hover:shadow-md"
    :class="
      task.completed
        ? 'bg-gray-50 border-gray-300 opacity-75'
        : 'bg-white border-indigo-200 hover:border-indigo-400'
    "
  >
    <div class="flex items-start gap-3">
      <button
        @click="$emit('toggle')"
        class="flex-shrink-0 w-5 h-5 mt-0.5 rounded border-2 transition-all"
        :class="
          task.completed
            ? 'bg-green-500 border-green-500'
            : 'bg-white border-gray-300 hover:border-indigo-500'
        "
      >
        <svg
          v-if="task.completed"
          class="w-4 h-4 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="3"
            d="M5 13l4 4L19 7"
          ></path>
        </svg>
      </button>

      <div class="flex-1 min-w-0">
        <h3
          class="text-lg font-semibold mb-1"
          :class="
            task.completed ? 'line-through text-gray-500' : 'text-gray-900'
          "
        >
          {{ task.title }}
        </h3>

        <p
          class="text-sm mb-3"
          :class="task.completed ? 'text-gray-400' : 'text-gray-600'"
        >
          {{ task.description }}
        </p>

        <div class="flex items-center gap-3 text-xs text-gray-500">
          <div class="flex items-center gap-1">
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              ></path>
            </svg>
            {{ formatDate(task.createdAt) }}
          </div>

          <span
            class="px-2 py-0.5 rounded-full text-xs font-medium"
            :class="
              task.completed
                ? 'bg-green-100 text-green-800'
                : 'bg-orange-100 text-orange-800'
            "
          >
            {{ task.completed ? "Zakończone" : "Do zrobienia" }}
          </span>
        </div>
      </div>

      <div class="flex-shrink-0 flex flex-col gap-2">
        <button
          @click="$emit('toggle')"
          class="px-3 py-1.5 rounded-lg text-white text-sm font-medium transition-colors"
          :class="
            task.completed
              ? 'bg-yellow-500 hover:bg-yellow-600'
              : 'bg-green-500 hover:bg-green-600'
          "
        >
          {{ task.completed ? "Cofnij" : "Zrobione" }}
        </button>

        <button
          @click="$emit('edit')"
          class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Edytuj
        </button>

        <button
          @click="$emit('delete')"
          class="px-3 py-1.5 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Usuń
        </button>
      </div>
    </div>
  </div>
</template>
