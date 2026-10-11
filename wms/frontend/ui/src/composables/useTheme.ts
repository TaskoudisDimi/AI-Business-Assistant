import { ref } from 'vue'

export type ThemePref = 'system' | 'light' | 'dark'

const STORAGE_KEY = 'theme'
const media = window.matchMedia('(prefers-color-scheme: dark)')

function readPref(): ThemePref {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    if (v === 'light' || v === 'dark') return v
  } catch { /* storage unavailable */ }
  return 'system'
}

const pref = ref<ThemePref>(readPref())

function apply() {
  const dark = pref.value === 'dark' || (pref.value === 'system' && media.matches)
  document.documentElement.dataset.theme = dark ? 'dark' : 'light'
}

media.addEventListener('change', apply)
apply()

export function useTheme() {
  const setTheme = (next: ThemePref) => {
    pref.value = next
    try {
      if (next === 'system') localStorage.removeItem(STORAGE_KEY)
      else localStorage.setItem(STORAGE_KEY, next)
    } catch { /* storage unavailable */ }
    apply()
  }
  // Cycles system → light → dark → system
  const cycleTheme = () =>
    setTheme(pref.value === 'system' ? 'light' : pref.value === 'light' ? 'dark' : 'system')

  return { theme: pref, setTheme, cycleTheme }
}
