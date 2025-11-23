<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  task: Object,
  show: Boolean,
});

const emit = defineEmits(["close", "save"]);

const localTitle = ref("");
const localDescription = ref("");

watch(
  () => props.task,
  (newTask) => {
    if (newTask) {
      localTitle.value = newTask.title;
      localDescription.value = newTask.description;
    }
  },
  { immediate: true }
);

const handleSave = () => {
  emit("save", {
    title: localTitle.value,
    description: localDescription.value,
  });
};

const handleClose = () => {
  emit("close");
};
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    @click.self="handleClose"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-gray-900">Edytuj zadanie</h3>
        <button @click="handleClose" class="text-gray-400 hover:text-gray-600">
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Tytuł zadania
          </label>
          <input
            v-model="localTitle"
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
            v-model="localDescription"
            placeholder="Dodatkowe szczegóły..."
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          ></textarea>
        </div>

        <div class="flex gap-3">
          <button
            type="button"
            @click="handleClose"
            class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2.5 rounded-lg transition-colors"
          >
            Anuluj
          </button>
          <button
            type="submit"
            class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            Zapisz
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
