import { CONTACT_EMAIL } from '$lib/contact';
import { OFFICES } from '$lib/offices';
import { localizeHref } from '$lib/paraglide/runtime';
import { FOUNDING_YEAR, absoluteUrl } from '$lib/seo/schema';
import type { CityEntry } from '$lib/venue-groups';
import { whatsappDisplay } from '$lib/whatsapp';

/**
 * One line of the llms.txt link list. Points at the Indonesian URL, which is
 * the canonical one Google indexes, with the English copy alongside so a model
 * answering in either language cites a page that exists in it.
 */
function link(path: string, label: string, note: string): string {
  const id = absoluteUrl(localizeHref(path, { locale: 'id' }));
  const en = absoluteUrl(localizeHref(path, { locale: 'en' }));
  return `- [${label}](${id}): ${note} ([English](${en}))`;
}

/**
 * The /llms.txt body, per llmstxt.org: an H1, a blockquote summary, then
 * H2 sections of links with one-line notes.
 *
 * Written in English because its reader is a model, not a visitor. The claims
 * in it are the ones the site already makes in its own copy -- nothing here
 * names a price, since prices change without a deploy, and the only date is
 * the founding year the footer already states. Offices come from the same
 * constants as the footer and the legal pages, so the address a model quotes
 * is the one a visitor sees.
 */
export function buildLlmsTxt(cities: CityEntry[]): string {
  const cityLines = cities.map((city) =>
    link(
      `/wedding-venue/${city.slug}`,
      city.name,
      `${city.count} wedding ${city.count === 1 ? 'venue' : 'venues'}, grouped by hotel star rating`
    )
  );
  const offices = [
    `Jakarta: ${OFFICES.jakarta.join(', ')}`,
    `Bali: ${OFFICES.bali.join(', ')}`,
    `Singapore: ${OFFICES.singapore.join(', ')}`
  ].join('; ');

  // Sections follow the site's own menu (Wedding Venue, Paket & Layanan,
  // Inspirasi, Events, then the company pages), so a model sees the site the
  // way a visitor does. The test holds this list to the sitemap's static pages.
  return [
    '# 7Magic Wedding',
    '',
    `> Wedding venues and planning support in Jakarta, Tangerang, Bogor, Bekasi, Bali, Batam and Singapore, from an Indonesian wedding organizer working since ${FOUNDING_YEAR}. Venues are listed by city and hotel star rating, and couples can book a free accompanied venue tour before deciding.`,
    '',
    'The site is in Indonesian at the root URLs, with an English edition under /en/. Both editions describe the same venues and services; the Indonesian pages are canonical.',
    '',
    `Offices — ${offices}.`,
    '',
    '## Wedding venues by city',
    '',
    ...cityLines,
    link(
      '/wedding-venue/search',
      'All venues',
      'searchable list of every venue, filterable by city, star rating and budget'
    ),
    '',
    '## Wedding planning by region',
    '',
    link(
      '/jabodetabek-wedding',
      'Jabodetabek weddings',
      'wedding venues across Jakarta, Tangerang, Bogor and Bekasi, with a free accompanied venue visit; office on Jalan Gajah Mada, Jakarta'
    ),
    link('/bali-wedding-planning', 'Bali wedding planning', 'full planning for destination weddings in Bali'),
    link(
      '/wedding-planning-singapore',
      'Wedding planning Singapore',
      'full planning from the Singapore office, with ALL Access running guest check-in and seating on the day'
    ),
    '',
    '## Packages and services',
    '',
    link(
      '/paket-sangjit',
      'Sangjit package',
      'the Chinese-Indonesian engagement ceremony, organised end to end'
    ),
    link(
      '/perjanjian-pranikah',
      'Prenuptial agreement',
      'prenuptial agreement service for Indonesian and mixed-nationality couples in Jakarta'
    ),
    link('/free-venue-tour', 'Free venue tour', 'a free accompanied visit to any venue on the site'),
    link('/tour', 'Book a venue tour', 'pick a venue and a date'),
    '',
    '## Inspiration',
    '',
    link('/wedding-showcases', 'Wedding showcases', 'real weddings we have planned and run'),
    link(
      '/artikel',
      'Wedding articles',
      'guides on venue prices, Indonesian wedding traditions, preparation and paperwork'
    ),
    '',
    '## Events',
    '',
    link(
      '/bali-event-organizer',
      'Bali event organizer',
      'company outings, gatherings, gala dinners and conferences in Bali'
    ),
    '',
    '## Company',
    '',
    link('/about', 'About 7Magic', 'who we are'),
    link(
      '/our-vendors',
      'Our vendors',
      'the photographers, decorators, cake makers, entertainers and bridal houses we work with'
    ),
    link('/contact', 'Contact', `WhatsApp ${whatsappDisplay}, email ${CONTACT_EMAIL}`),
    '',
    '## Optional',
    '',
    link('/privacy', 'Privacy policy', 'how enquiry and tour data is handled'),
    link('/terms', 'Terms and conditions', 'terms for using the site and our services'),
    `- [Sitemap](${absoluteUrl('/sitemap.xml')}): every page in both languages`,
    ''
  ].join('\n');
}
