<template>
  <div class="flex h-screen w-full bg-gray-50">
    <!-- Sidebar -->
    <div class="w-64 flex-shrink-0 border-r bg-white">
      <div class="p-4 border-b">
        <h2 class="text-lg font-bold text-gray-800">Documentation</h2>
        <p class="text-xs text-gray-500">Eshin Broking CRM</p>
      </div>
      <nav class="p-2 space-y-1 overflow-y-auto h-[calc(100vh-65px)]">
        <div v-for="(section, index) in docs" :key="index" class="mb-4">
          <h3 class="px-2 mb-1 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            {{ section.title }}
          </h3>
          <button
            v-for="page in section.pages"
            :key="page.id"
            @click="currentPage = page"
            class="w-full text-left px-2 py-1.5 text-sm rounded-md transition-colors"
            :class="currentPage.id === page.id ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700 hover:bg-gray-100'"
          >
            {{ page.title }}
          </button>
        </div>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-y-auto">
      <div class="max-w-4xl mx-auto p-8">
        <div v-if="currentPage">
          <h1 class="text-3xl font-bold text-gray-900 mb-6">{{ currentPage.title }}</h1>
          
          <div class="prose max-w-none">
            <div v-for="(block, bIndex) in currentPage.content" :key="bIndex" class="mb-8">
              
              <!-- Text Block -->
              <div v-if="block.type === 'text'" v-html="block.value" class="text-gray-700 leading-relaxed mb-4"></div>
              
              <!-- Image Block (Placeholder/Real) -->
              <div v-else-if="block.type === 'image'" class="my-6 border rounded-lg overflow-hidden shadow-sm bg-gray-100">
                <div class="bg-gray-200 py-8 text-center text-gray-500 italic" v-if="!block.src">
                  [Screenshot: {{ block.alt }}]
                </div>
                <img v-else :src="block.src" :alt="block.alt" class="w-full h-auto object-cover" />
                <div class="bg-gray-50 px-4 py-2 text-xs text-gray-500 border-t">
                  Fig {{ bIndex + 1 }}: {{ block.caption }}
                </div>
              </div>

              <!-- Note/Alert Block -->
              <div v-else-if="block.type === 'note'" class="bg-blue-50 border-l-4 border-blue-500 p-4 my-4">
                <p class="text-sm text-blue-700">{{ block.value }}</p>
              </div>

            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-full text-gray-400">
          <FeatherIcon name="book-open" class="w-16 h-16 mb-4 opacity-50" />
          <p>Select a topic from the sidebar to start reading.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { documentationData } from '../data/docs'

const docs = ref(documentationData)
const currentPage = ref(null)

onMounted(() => {
  // Open first page by default
  if (docs.value.length > 0 && docs.value[0].pages.length > 0) {
    currentPage.value = docs.value[0].pages[0]
  }
})
</script>
