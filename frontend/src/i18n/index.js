import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import it from './locales/it.json'

const messages = {
  en,
  it
}

// Get browser language or default to English
const getDefaultLocale = () => {
  const savedLocale = localStorage.getItem('locale')
  if (savedLocale && messages[savedLocale]) {
    return savedLocale
  }
  
  const browserLocale = navigator.language.split('-')[0]
  return messages[browserLocale] ? browserLocale : 'en'
}

export default createI18n({
  legacy: false, // Use Composition API
  locale: getDefaultLocale(),
  fallbackLocale: 'en',
  messages
})
