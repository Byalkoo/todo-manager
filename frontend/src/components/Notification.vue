<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  show: Boolean,
  message: String,
  type: {
    type: String,
    default: "error",
  },
});

const emit = defineEmits(["close"]);

watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      setTimeout(() => {
        emit("close");
      }, 5000);
    }
  }
);
</script>

<template>
  <transition
    enter-active-class="transition ease-out duration-300"
    enter-from-class="translate-y-2 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-2 opacity-0"
  >
    <div v-if="show" class="fixed top-4 right-4 z-50 max-w-sm w-full">
      <div
        class="rounded-lg shadow-lg p-4 flex items-start gap-3"
        :class="{
          'bg-red-50 border-l-4 border-red-500': type === 'error',
          'bg-green-50 border-l-4 border-green-500': type === 'success',
          'bg-blue-50 border-l-4 border-blue-500': type === 'info',
          'bg-yellow-50 border-l-4 border-yellow-500': type === 'warning',
        }"
      >
        <div class="flex-shrink-0">
          <svg
            v-if="type === 'error'"
            class="w-6 h-6 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <svg
            v-if="type === 'success'"
            class="w-6 h-6 text-green-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <svg
            v-if="type === 'info'"
            class="w-6 h-6 text-blue-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <svg
            v-if="type === 'warning'"
            class="w-6 h-6 text-yellow-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            ></path>
          </svg>
        </div>

        <div class="flex-1">
          <p
            class="text-sm font-medium"
            :class="{
              'text-red-800': type === 'error',
              'text-green-800': type === 'success',
              'text-blue-800': type === 'info',
              'text-yellow-800': type === 'warning',
            }"
          >
            {{ message }}
          </p>
        </div>

        <button
          @click="emit('close')"
          class="flex-shrink-0 text-gray-400 hover:text-gray-600"
        >
          <svg
            class="w-5 h-5"
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
    </div>
  </transition>
</template>
