/**
 * Legal identity shown on /privacy and /terms and in the footer.
 * TODO before launch: fill in the real details (they're legally required in
 * the privacy policy) and have a lawyer review src/legal/*.ts.
 */
export const site = {
  productName: 'WMS',
  legalName: 'TaskCode',                    // e.g. "Δημήτρης Τασκούδης" or "TaskCode IKE"
  vatNumber: '',                            // ΑΦΜ
  address: '',                              // registered address
  contactEmail: '',                         // privacy / support email
  jurisdiction: { el: 'Θεσσαλονίκης', en: 'Thessaloniki' },  // courts for disputes
  policyUpdated: '2026-10-17',
}

export const missingLegalDetails = (): boolean =>
  !site.vatNumber || !site.address || !site.contactEmail
