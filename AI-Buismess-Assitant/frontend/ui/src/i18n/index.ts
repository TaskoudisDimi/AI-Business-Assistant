import { createI18n } from 'vue-i18n'

const messages = {
  en: {
    settings: "Settings",
    account: "Account",
    business: "Business",
    fullName: "Full Name",
    language: "Language",
    theme: "Theme",
    save: "Save Changes",
    deleteAccount: "Delete Account",
    businessName: "Business Name",
    industry: "Industry"
  },
  el: {
    settings: "Ρυθμίσεις",
    account: "Λογαριασμός",
    business: "Επιχείρηση",
    fullName: "Ονοματεπώνυμο",
    language: "Γλώσσα",
    theme: "Θέμα",
    save: "Αποθήκευση",
    deleteAccount: "Διαγραφή Λογαριασμού",
    businessName: "Όνομα Επιχείρησης",
    industry: "Κλάδος"
  }
}

export const i18n = createI18n({
  legacy: false,
  locale: "en",
  fallbackLocale: "en",
  messages
})