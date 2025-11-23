<script setup>
import { ref } from "vue";

const emit = defineEmits(["add-task"]);

const title = ref("");
const description = ref("");

const handleSubmit = () => {
  emit("add-task", {
    title: title.value,
    description: description.value,
  });

  title.value = "";
  description.value = "";
};
</script>

<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center gap-2 mb-6">
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
            d="M12 6v6m0 0v6m0-6h6m-6 0H6"
          ></path>
        </svg>
      </div>
      <h2 class="text-xl font-bold text-gray-900">Dodaj zadanie</h2>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Tytuł zadania
        </label>
        <input
          v-model="title"
          type="text"
          placeholder="Co należy zrobić?"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Opis
        </label>
        <textarea
          v-model="description"
          placeholder="Dodatkowe szczegóły..."
          rows="3"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
        ></textarea>
      </div>

      <button
        type="submit"
        class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-colors"
      >
        Dodaj zadanie
      </button>
    </form>
  </div>
</template>
