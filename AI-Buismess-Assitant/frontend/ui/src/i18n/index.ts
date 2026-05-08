import { createI18n } from 'vue-i18n'
import el from './el.json'
import en from './en.json'

const savedLocale = localStorage.getItem('locale') ?? 'el'

export const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'el',
  messages: { el, en },
})

export const setLocale = (locale: 'el' | 'en') => {
  (i18n.global.locale as any).value = locale
  localStorage.setItem('locale', locale)
  document.documentElement.lang = locale
}
