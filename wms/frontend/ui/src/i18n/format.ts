import { i18n } from '@/i18n'

/** BCP-47 tag for Intl formatting, following the UI language (reactive in templates). */
export function intlLocale(): string {
  const l = (i18n.global.locale as unknown as { value: string }).value
  return l === 'en' ? 'en-GB' : 'el-GR'
}
