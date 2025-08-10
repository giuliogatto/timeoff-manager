<template>
  <div class="language-switcher">
    <select v-model="currentLocale" @change="changeLanguage" class="language-select">
      <option value="en">🇺🇸 English</option>
      <option value="it">🇮🇹 Italiano</option>
    </select>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const currentLocale = computed({
  get: () => locale.value,
  set: (value) => {
    locale.value = value
    localStorage.setItem('locale', value)
  }
})

const changeLanguage = () => {
  // The computed setter will handle the change
}
</script>

<style scoped>
.language-switcher {
  display: inline-block;
}

.language-select {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.language-select:hover {
  border-color: #42b983;
}

.language-select:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}
</style>
