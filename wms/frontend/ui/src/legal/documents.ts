import { site } from '@/config/site'

export interface LegalDoc { title: string; intro: string; sections: { h: string; p: string[] }[] }

const who = (lang: 'el' | 'en') => [
  site.legalName,
  site.vatNumber && (lang === 'el' ? `ΑΦΜ ${site.vatNumber}` : `VAT ${site.vatNumber}`),
  site.address,
  site.contactEmail,
].filter(Boolean).join(' · ')

export function privacy(lang: 'el' | 'en'): LegalDoc {
  if (lang === 'el') return {
    title: 'Πολιτική απορρήτου',
    intro: `Η πολιτική αυτή εξηγεί ποια προσωπικά δεδομένα επεξεργάζεται το ${site.productName}, γιατί, και ποια δικαιώματα έχεις σύμφωνα με τον Γενικό Κανονισμό Προστασίας Δεδομένων (ΓΚΠΔ / GDPR).`,
    sections: [
      { h: 'Ποιοι είμαστε', p: [
        `Υπεύθυνος επεξεργασίας για τα δεδομένα του λογαριασμού σου είναι: ${who('el')}.`,
        'Για τα δεδομένα που καταχωρεί η επιχείρησή σου (π.χ. ονόματα πελατών και προμηθευτών, παραγγελίες), υπεύθυνος επεξεργασίας είναι η επιχείρησή σου και εμείς ενεργούμε ως εκτελών την επεξεργασία για λογαριασμό της, μόνο για να παρέχουμε την υπηρεσία.',
      ] },
      { h: 'Ποια δεδομένα συλλέγουμε', p: [
        'Λογαριασμός: ονοματεπώνυμο, email, κωδικός (αποθηκεύεται μόνο κρυπτογραφημένος), προτιμήσεις γλώσσας.',
        'Δεδομένα επιχείρησης: προϊόντα, απόθεμα, κινήσεις, παραγγελίες, ονόματα πελατών και προμηθευτών, αρχεία που ανεβάζεις (CSV, φωτογραφίες ή PDF τιμολογίων).',
        'Τεχνικά δεδομένα: διεύθυνση IP και αρχεία καταγραφής του server για λόγους ασφαλείας, cookies σύνδεσης.',
      ] },
      { h: 'Γιατί τα χρησιμοποιούμε και με ποια νομική βάση', p: [
        'Για να παρέχουμε την υπηρεσία που ζήτησες, όπως σύνδεση, διαχείριση αποθήκης, ειδοποιήσεις και προβλέψεις (εκτέλεση σύμβασης, άρθρο 6 παρ. 1 β ΓΚΠΔ).',
        'Για την ασφάλεια και την αποτροπή κατάχρησης (έννομο συμφέρον, άρθρο 6 παρ. 1 στ).',
        'Για τήρηση νομικών υποχρεώσεων, όπου υπάρχουν (άρθρο 6 παρ. 1 γ).',
        'Δεν πουλάμε δεδομένα και δεν τα χρησιμοποιούμε για διαφήμιση.',
      ] },
      { h: 'Με ποιους τα μοιραζόμαστε', p: [
        'Supabase Inc.: βάση δεδομένων, σύνδεση χρηστών και αποθήκευση αρχείων.',
        'Hetzner Online GmbH (Γερμανία): φιλοξενία του server της εφαρμογής.',
        'Anthropic PBC: μόνο όταν χρησιμοποιείς λειτουργίες AI (σκανάρισμα τιμολογίων, βοηθός, προσχέδια μηνυμάτων), λαμβάνει το περιεχόμενο του συγκεκριμένου αιτήματος για να παράγει την απάντηση.',
        'Πάροχος αποστολής email: για τα email σύνδεσης, επαναφοράς κωδικού και ειδοποιήσεων.',
        'Όπου η μεταφορά γίνεται εκτός ΕΟΧ, βασίζεται σε Τυποποιημένες Συμβατικές Ρήτρες της Ευρωπαϊκής Επιτροπής ή σε απόφαση επάρκειας.',
      ] },
      { h: 'Πόσο καιρό τα κρατάμε', p: [
        'Όσο υπάρχει ο λογαριασμός σου. Όταν τον διαγράψεις, σβήνονται αμέσως ο λογαριασμός και οι επιχειρήσεις που σου ανήκουν. Τα αντίγραφα ασφαλείας ανανεώνονται κυκλικά και τα παλιά διαγράφονται μέσα σε 14 ημέρες.',
      ] },
      { h: 'Τα δικαιώματά σου', p: [
        'Έχεις δικαίωμα πρόσβασης, διόρθωσης, διαγραφής, περιορισμού, φορητότητας και εναντίωσης. Από τις Ρυθμίσεις μπορείς να κατεβάσεις όλα σου τα δεδομένα και να διαγράψεις τον λογαριασμό σου.',
        `Για οποιοδήποτε αίτημα επικοινώνησε μαζί μας${site.contactEmail ? ` στο ${site.contactEmail}` : ''}. Έχεις επίσης δικαίωμα καταγγελίας στην Αρχή Προστασίας Δεδομένων Προσωπικού Χαρακτήρα (www.dpa.gr).`,
      ] },
      { h: 'Cookies και τοπική αποθήκευση', p: [
        'Χρησιμοποιούμε μόνο απολύτως απαραίτητα cookies, για να παραμένεις συνδεδεμένος (access_token, refresh_token). Ο browser σου κρατά επίσης τοπικά τις προτιμήσεις σου (γλώσσα, θέμα).',
        'Δεν χρησιμοποιούμε cookies ανάλυσης ή διαφήμισης, και οι γραμματοσειρές φορτώνονται από τον δικό μας server.',
      ] },
      { h: 'Ασφάλεια', p: [
        'Η επικοινωνία γίνεται πάντα κρυπτογραφημένα (HTTPS). Τα cookies σύνδεσης δεν είναι προσβάσιμα από scripts, και κάθε επιχείρηση βλέπει μόνο τα δικά της δεδομένα. Κρατάμε τακτικά αντίγραφα ασφαλείας.',
      ] },
      { h: 'Αλλαγές', p: ['Αν αλλάξουμε ουσιαστικά αυτή την πολιτική, θα σε ενημερώσουμε μέσα από την εφαρμογή ή με email.'] },
    ],
  }
  return {
    title: 'Privacy policy',
    intro: `This policy explains what personal data ${site.productName} processes, why, and your rights under the General Data Protection Regulation (GDPR).`,
    sections: [
      { h: 'Who we are', p: [
        `The controller for your account data is: ${who('en')}.`,
        'For data your business enters (e.g. customer and supplier names, orders), your business is the controller and we act as a processor on its behalf, only to provide the service.',
      ] },
      { h: 'What we collect', p: [
        'Account: name, email, password (stored only as a hash), language preference.',
        'Business data: products, stock, movements, orders, customer and supplier names, files you upload (CSV files, photos or PDFs of invoices).',
        'Technical data: IP address and server logs for security, sign-in cookies.',
      ] },
      { h: 'Why we use it and on what legal basis', p: [
        'To provide the service you asked for: sign-in, warehouse management, alerts and forecasts (performance of a contract, Art. 6(1)(b) GDPR).',
        'To keep the service secure and prevent abuse (legitimate interest, Art. 6(1)(f)).',
        'To meet legal obligations where they apply (Art. 6(1)(c)).',
        'We do not sell data or use it for advertising.',
      ] },
      { h: 'Who we share it with', p: [
        'Supabase Inc.: database, authentication and file storage.',
        'Hetzner Online GmbH (Germany): hosting of the application server.',
        'Anthropic PBC: only when you use AI features (invoice scanning, the assistant, message drafts), it receives the content of that request to produce the answer.',
        'Our email delivery provider: for sign-in, password reset and alert emails.',
        'Transfers outside the EEA rely on the European Commission\'s Standard Contractual Clauses or an adequacy decision.',
      ] },
      { h: 'How long we keep it', p: [
        'For as long as your account exists. When you delete it, the account and the businesses you own are removed immediately. Backups rotate, and old ones are deleted within 14 days.',
      ] },
      { h: 'Your rights', p: [
        'You can access, correct, delete, restrict, port and object to the processing of your data. In Settings you can download all your data and delete your account.',
        `For any request, contact us${site.contactEmail ? ` at ${site.contactEmail}` : ''}. You can also lodge a complaint with the Hellenic Data Protection Authority (www.dpa.gr) or your local authority.`,
      ] },
      { h: 'Cookies and local storage', p: [
        'We only use strictly necessary cookies to keep you signed in (access_token, refresh_token). Your browser also stores your preferences (language, theme) locally.',
        'We use no analytics or advertising cookies, and fonts are served from our own server.',
      ] },
      { h: 'Security', p: [
        'All traffic is encrypted (HTTPS). Sign-in cookies can\'t be read by scripts, and each business sees only its own data. We keep regular backups.',
      ] },
      { h: 'Changes', p: ['If we change this policy in a meaningful way, we\'ll let you know in the app or by email.'] },
    ],
  }
}

export function terms(lang: 'el' | 'en'): LegalDoc {
  if (lang === 'el') return {
    title: 'Όροι χρήσης',
    intro: `Οι όροι αυτοί ισχύουν για τη χρήση του ${site.productName}, που παρέχεται από: ${who('el')}. Με τη δημιουργία λογαριασμού τους αποδέχεσαι.`,
    sections: [
      { h: 'Η υπηρεσία', p: ['Το WMS είναι εφαρμογή διαχείρισης αποθήκης, παραγγελιών και προβλέψεων πωλήσεων, προσβάσιμη μέσω browser. Μπορεί να εξελίσσεται και να αλλάζουν λειτουργίες της.'] },
      { h: 'Λογαριασμός', p: [
        'Είσαι υπεύθυνος για την ακρίβεια των στοιχείων σου και για τη φύλαξη του κωδικού σου. Οι διαχειριστές μιας επιχείρησης αποφασίζουν ποιοι έχουν πρόσβαση στα δεδομένα της.',
      ] },
      { h: 'Αποδεκτή χρήση', p: [
        'Δεν επιτρέπεται η χρήση για παράνομους σκοπούς, η απόπειρα πρόσβασης σε δεδομένα άλλων, η υπερφόρτωση ή παρεμβολή στην υπηρεσία, ή η αποστολή υλικού που παραβιάζει δικαιώματα τρίτων.',
      ] },
      { h: 'Τα δεδομένα σου', p: [
        'Τα δεδομένα που καταχωρείς ανήκουν σε εσένα ή στην επιχείρησή σου. Τα επεξεργαζόμαστε μόνο για να σου παρέχουμε την υπηρεσία, όπως περιγράφει η Πολιτική απορρήτου, η οποία αποτελεί και τη συμφωνία επεξεργασίας δεδομένων μεταξύ μας. Μπορείς να τα εξαγάγεις ή να τα διαγράψεις οποιαδήποτε στιγμή.',
      ] },
      { h: 'Προβλέψεις και λειτουργίες AI', p: [
        'Οι προβλέψεις, οι προτάσεις αναπαραγγελίας, η ανάγνωση τιμολογίων και οι απαντήσεις του βοηθού παράγονται αυτόματα και μπορεί να περιέχουν λάθη. Είναι βοηθήματα και όχι εγγυήσεις. Έλεγξέ τα πριν βασίσεις σε αυτά αποφάσεις.',
      ] },
      { h: 'Διαθεσιμότητα', p: ['Καταβάλλουμε κάθε εύλογη προσπάθεια για συνεχή λειτουργία, αλλά δεν εγγυόμαστε αδιάλειπτη διαθεσιμότητα. Μπορεί να υπάρξουν διακοπές για συντήρηση.'] },
      { h: 'Χρεώσεις', p: ['Αν η υπηρεσία ή κάποιο πακέτο της χρεώνεται, οι τιμές θα σου γνωστοποιούνται πριν ισχύσουν και θα μπορείς να τις αποδεχτείς ή να διακόψεις τη χρήση.'] },
      { h: 'Ευθύνη', p: ['Στο μέτρο που επιτρέπει ο νόμος, δεν ευθυνόμαστε για έμμεσες ζημίες ή απώλεια κερδών από τη χρήση της υπηρεσίας. Τίποτα σε αυτούς τους όρους δεν περιορίζει ευθύνη που δεν μπορεί να περιοριστεί κατά τον νόμο.'] },
      { h: 'Λήξη', p: ['Μπορείς να διαγράψεις τον λογαριασμό σου οποιαδήποτε στιγμή από τις Ρυθμίσεις. Μπορούμε να αναστείλουμε λογαριασμούς που παραβιάζουν αυτούς τους όρους, αφού σε ειδοποιήσουμε όπου είναι εφικτό.'] },
      { h: 'Εφαρμοστέο δίκαιο', p: [`Οι όροι διέπονται από το ελληνικό δίκαιο. Αρμόδια είναι τα δικαστήρια ${site.jurisdiction.el}, με την επιφύλαξη των δικαιωμάτων που σου δίνει η νομοθεσία για την προστασία των καταναλωτών.`] },
    ],
  }
  return {
    title: 'Terms of service',
    intro: `These terms govern your use of ${site.productName}, provided by: ${who('en')}. By creating an account you accept them.`,
    sections: [
      { h: 'The service', p: ['WMS is a browser-based app for managing stock, orders and sales forecasts. It may evolve and its features may change.'] },
      { h: 'Your account', p: ['You\'re responsible for keeping your details accurate and your password safe. A business\'s admins decide who can access its data.'] },
      { h: 'Acceptable use', p: ['Don\'t use the service for unlawful purposes, try to access others\' data, overload or interfere with the service, or upload material that infringes others\' rights.'] },
      { h: 'Your data', p: ['Data you enter belongs to you or your business. We process it only to provide the service, as described in the Privacy policy, which also serves as our data processing agreement. You can export or delete it at any time.'] },
      { h: 'Forecasts and AI features', p: ['Forecasts, reorder suggestions, invoice reading and assistant answers are generated automatically and may contain mistakes. They are aids, not guarantees. Check them before relying on them for decisions.'] },
      { h: 'Availability', p: ['We make every reasonable effort to keep the service running, but we don\'t guarantee uninterrupted availability. There may be downtime for maintenance.'] },
      { h: 'Fees', p: ['If the service or a plan is paid, prices will be communicated before they apply, and you can accept them or stop using the service.'] },
      { h: 'Liability', p: ['To the extent permitted by law, we aren\'t liable for indirect damages or lost profits arising from use of the service. Nothing in these terms limits liability that can\'t be limited by law.'] },
      { h: 'Termination', p: ['You can delete your account at any time in Settings. We may suspend accounts that breach these terms, with notice where practical.'] },
      { h: 'Governing law', p: [`These terms are governed by Greek law. The courts of ${site.jurisdiction.en} have jurisdiction, without prejudice to your rights under consumer protection law.`] },
    ],
  }
}
