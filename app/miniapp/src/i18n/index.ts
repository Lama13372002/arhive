import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

// Import translation files
import ru from './locales/ru.json'
import kz from './locales/kz.json'
import en from './locales/en.json'

const resources = {
  ru: { translation: ru },
  kz: { translation: kz },
  en: { translation: en },
}

// Detect language from Telegram WebApp or browser
const detectLanguage = (): string => {
  // Try to get language from Telegram WebApp
  if (window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code) {
    const tgLang = window.Telegram.WebApp.initDataUnsafe.user.language_code
    if (tgLang.startsWith('ru')) return 'ru'
    if (tgLang.startsWith('kk') || tgLang.startsWith('kz')) return 'kz'
    if (tgLang.startsWith('en')) return 'en'
  }
  
  // Fallback to browser language
  const browserLang = navigator.language
  if (browserLang.startsWith('ru')) return 'ru'
  if (browserLang.startsWith('kk') || browserLang.startsWith('kz')) return 'kz'
  if (browserLang.startsWith('en')) return 'en'
  
  // Default to Russian
  return 'ru'
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: detectLanguage(),
    fallbackLng: 'ru',
    debug: import.meta.env.DEV,
    
    interpolation: {
      escapeValue: false,
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
  })

export default i18n

