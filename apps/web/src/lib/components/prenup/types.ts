/**
 * The shape of a prenuptial agreement landing page's copy. Shared by the
 * Jakarta and Bali pages, which sell the same service through different
 * notaries: one shape means one template, and a locale or a city that misses a
 * field fails the type check rather than rendering blank.
 */

export type ComparisonRow = { label: string; price: string; note: string; ours: boolean };
export type Segment = { title: string; copy: string; alt: string };
export type LawCard = { reference: string; title: string; copy: string };
export type Step = { when: string; title: string; copy: string };
export type Faq = { q: string; a: string };

export type PrenupCopy = {
  price: string;
  priceShort: string;
  meta: { title: string; description: string; keywords: string };
  hero: {
    eyebrow: string;
    title: string;
    lead: string;
    ctaConsult: string;
    ctaWhatsapp: string;
    note: string;
    imageAlt: string;
  };
  stats: { value: string; label: string }[];
  price_section: {
    eyebrow: string;
    title: string;
    lead: string;
    marketNote: string;
    once: string;
    badge: string;
    includedTitle: string;
    excludedTitle: string;
    cta: string;
  };
  comparison: ComparisonRow[];
  included: string[];
  excluded: string[];
  segmentsIntro: { eyebrow: string; title: string };
  segments: Segment[];
  law: {
    eyebrow: string;
    title: string;
    missedTitle: string;
    missedLead: string;
    missedEmphasis: string;
    missedTail: string;
    deedAlt: string;
    notaryLabel: string;
    notaryArea: string;
  };
  lawCards: LawCard[];
  process: { eyebrow: string; title: string; lead: string };
  steps: Step[];
  limits: {
    eyebrow: string;
    title: string;
    lead: string;
    canTitle: string;
    cannotTitle: string;
  };
  can: string[];
  cannot: string[];
  docs: { eyebrow: string; title: string; lead: string; imageAlt: string };
  docList: string[];
  faqTitle: string;
  faqs: Faq[];
  form: {
    title: string;
    lead: string;
    talkTitle: string;
    privacy: string;
    statusLabel: string;
    statusPlaceholder: string;
    statusOptions: string[];
    citizenshipLabel: string;
    citizenshipOptions: string[];
    dateLabel: string;
    dateHint: string;
    assetsLabel: string;
    assetsPlaceholder: string;
    assetsOptions: string[];
    nameLabel: string;
    phoneLabel: string;
    phonePlaceholder: string;
    emailLabel: string;
    emailHint: string;
    notesLabel: string;
    notesPlaceholder: string;
    submit: string;
    sending: string;
    dataNote: string;
    sendError: string;
    doneTitle: string;
    doneCopy: string;
    doneCta: string;
    optional: string;
  };
  whatsappPrefill: string;
  /** Lead body labels. English leads want an English reply. */
  lead: {
    heading: string;
    language: string;
    status: string;
    citizenship: string;
    assets: string;
    weddingDate: string;
    noNotes: string;
    none: string;
  };
  jsonLd: { serviceType: string; offerDescription: string };
};
