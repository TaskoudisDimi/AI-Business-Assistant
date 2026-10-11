<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps<{ id: string; autocomplete: string; invalid?: boolean; placeholder?: string }>()
const model = defineModel<string>({ required: true })

const { t } = useI18n()
const visible = ref(false)
</script>

<template>
  <div class="ui-input-wrap">
    <input
      :id="id"
      v-model="model"
      class="ui-input"
      :type="visible ? 'text' : 'password'"
      :autocomplete="autocomplete"
      :placeholder="placeholder"
      :aria-invalid="invalid || undefined"
      required
    />
    <button
      type="button"
      class="ui-input-action"
      :aria-label="visible ? t('auth.hidePassword') : t('auth.showPassword')"
      :aria-pressed="visible"
      @click="visible = !visible"
    >
      <svg v-if="!visible" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10.6 5.1A9.8 9.8 0 0 1 12 5c6.4 0 10 7 10 7a17 17 0 0 1-2.3 3.2M6.6 6.6C3.8 8.4 2 12 2 12s3.6 7 10 7a9.6 9.6 0 0 0 5.4-1.6M9.9 9.9a3 3 0 0 0 4.2 4.2M3 3l18 18"/></svg>
    </button>
  </div>
</template>
