/**
 * Article categories, shared by the form UI and the server-side validators.
 *
 * These live outside $lib/server because the form components need them in the
 * browser, and SvelteKit refuses to bundle $lib/server/* into client code.
 */
export const ARTICLE_CATEGORIES = [
  { value: 'wedding-venue', label: 'Wedding Venue' },
  { value: 'wedding-preparation', label: 'Wedding Preparation' },
  { value: 'tradisi-wedding', label: 'Tradisi Wedding' },
  { value: 'photography', label: 'Photography' },
  { value: 'videography', label: 'Videography' }
];
