/**
 * The office addresses, as printed in the footer and named on the privacy and
 * terms pages.
 *
 * One place, for the reason `CONTACT_EMAIL` is: the legal pages identify who
 * runs the site by these addresses, and a footer edit that left them behind
 * would have the policy pointing at an office that no longer exists. Street
 * lines are not translated; they are what the post and a map search expect.
 *
 * Jakarta is listed first because it is the operator's address in the legal
 * pages, under Indonesian law.
 */
export const OFFICES = {
  jakarta: ['Jalan Gajah Mada No. 10', 'Jakarta, Indonesia 10130'],
  bali: ['Sunday Arshika Hotel - Lobby, Sunset Road Kuta - Bali', 'Bali, 80612, Indonesia'],
  singapore: ['110 Pasir Ris Street 11', 'Singapore 510110']
} as const;
