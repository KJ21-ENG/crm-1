<template>
  <button
    class="flex h-7 cursor-pointer items-center rounded text-ink-gray-7 duration-300 ease-in-out focus:outline-none focus:transition-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-outline-gray-3"
    :class="isActive ? 'bg-surface-selected shadow-sm' : 'hover:bg-surface-gray-2'"
    @click="handleClick"
  >
    <div
      class="flex w-full items-center justify-between duration-300 ease-in-out"
      :class="isCollapsed ? 'ml-[3px] p-1' : 'px-2 py-1'"
    >
      <div class="flex items-center truncate">
        <Tooltip :text="label" placement="right" :disabled="!isCollapsed">
          <slot name="icon">
            <span class="relative grid flex-shrink-0 place-items-center">
              <template v-if="showBurst">
                <span class="celebration-burst celebration-burst--one" />
                <span class="celebration-burst celebration-burst--two" />
                <span class="celebration-burst celebration-burst--three" />
                <span class="celebration-burst celebration-burst--four" />
              </template>
              <FeatherIcon
                v-if="typeof icon == 'string'"
                :name="icon"
                class="size-4 text-ink-gray-7"
                :class="{ 'celebration-gift': showBurst }"
              />
              <component
                v-else
                :is="icon"
                class="size-4 text-ink-gray-7"
                :class="{ 'celebration-gift': showBurst }"
              />
            </span>
          </slot>
        </Tooltip>
        <Tooltip
          :text="label"
          placement="right"
          :disabled="isCollapsed"
          :hoverDelay="1.5"
        >
          <span
            class="flex-1 flex-shrink-0 truncate text-sm duration-300 ease-in-out"
            :class="
              [
                isCollapsed
                  ? 'ml-0 w-0 overflow-hidden opacity-0'
                  : 'ml-2 w-auto opacity-100',
                labelClass,
              ]
            "
          >
            {{ label }}
          </span>
        </Tooltip>
      </div>
      <slot name="right" />
    </div>
  </button>
</template>

<script setup>
import { Tooltip } from 'frappe-ui'
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { isMobileView, mobileSidebarOpened } from '@/composables/settings'

const router = useRouter()
const route = useRoute()

const props = defineProps({
  icon: {
    type: [Object, String, Function],
  },
  label: {
    type: String,
    default: '',
  },
  to: {
    type: [Object, String],
    default: '',
  },
  isCollapsed: {
    type: Boolean,
    default: false,
  },
  labelClass: {
    type: String,
    default: '',
  },
  showBurst: {
    type: Boolean,
    default: false,
  },
})

function handleClick() {
  if (!props.to) return
  if (typeof props.to === 'object') {
    router.push(props.to)
  } else {
    router.push({ name: props.to })
  }
  if (isMobileView.value) {
    mobileSidebarOpened.value = false
  }
}

let isActive = computed(() => {
  if (route.query.view) {
    return route.query.view == props.to?.query?.view
  }
  return route.name === props.to
})
</script>

<style scoped>
.celebration-gift {
  animation: celebrationGiftBounce 1.4s ease-in-out infinite;
}

.celebration-burst {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  opacity: 0;
  animation: celebrationBurst 1.4s ease-out infinite;
}

.celebration-burst--one {
  top: -2px;
  left: 8px;
  background: #f97316;
}

.celebration-burst--two {
  top: 8px;
  right: -2px;
  background: #14b8a6;
  animation-delay: 0.2s;
}

.celebration-burst--three {
  bottom: -2px;
  left: 4px;
  background: #ec4899;
  animation-delay: 0.4s;
}

.celebration-burst--four {
  top: 2px;
  left: -2px;
  background: #8b5cf6;
  animation-delay: 0.6s;
}

.sidebar-celebration-text {
  background: linear-gradient(90deg, #f97316, #facc15, #22c55e, #06b6d4, #6366f1, #ec4899, #f97316);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: celebrationRainbow 1.6s linear infinite;
}

@keyframes celebrationGiftBounce {
  0%, 100% { transform: rotate(0deg) scale(1); }
  25% { transform: rotate(-8deg) scale(1.05); }
  50% { transform: rotate(6deg) scale(1.1); }
  75% { transform: rotate(-4deg) scale(1.05); }
}

@keyframes celebrationBurst {
  0% { transform: translate(0, 0) scale(0.4); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translate(0, -12px) scale(1.2); opacity: 0; }
}

@keyframes celebrationRainbow {
  0% { background-position: 0% 50%; filter: hue-rotate(0deg); }
  100% { background-position: 200% 50%; filter: hue-rotate(360deg); }
}
</style>
