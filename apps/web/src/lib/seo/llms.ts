import { CONTACT_EMAIL } from '$lib/contact';
import { localizeHref } from '$lib/paraglide/runtime';
import { absoluteUrl } from '$lib/seo/schema';
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
 * names a price or a date, since those change without a deploy.
 */
export function buildLlmsTxt(cities: CityEntry[]): string {
  const cityLines = cities.map((city) =>
    link(
      `/wedding-venue/${city.slug}`,
      city.name,
      `${city.count} wedding ${city.count === 1 ? 'venue' : 'venues'} with starting package prices, grouped by hotel star rating`
    )
  );

  return [
    '# 7Magic Wedding',
    '',
    '> Wedding venue packages and planning support in Jakarta, Bali, Batam and Singapore, from an Indonesian wedding organizer with 18 years in the business. Venues are listed with starting package prices, and couples can book a free accompanied venue tour before deciding.',
    '',
    'The site is in Indonesian at the root URLs, with an English edition under /en/. Both editions describe the same venues and prices; the Indonesian pages are canonical.',
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
    '## Services',
    '',
    link('/free-venue-tour', 'Free venue tour', 'a free accompanied visit to any venue on the site'),
    link('/tour', 'Book a venue tour', 'pick a venue and a date'),
    link(
      '/perjanjian-pranikah',
      'Prenuptial agreement',
      'prenuptial agreement service for Indonesian and mixed-nationality couples in Jakarta'
    ),
    link(
      '/paket-sangjit',
      'Sangjit package',
      'the Chinese-Indonesian engagement ceremony, organised end to end'
    ),
    link('/bali-wedding-planning', 'Bali wedding planning', 'destination weddings in Bali'),
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
    link('/wedding-showcases', 'Wedding showcases', 'real weddings we have organised'),
    link('/contact', 'Contact', `WhatsApp ${whatsappDisplay}, email ${CONTACT_EMAIL}`),
    '',
    '## Articles',
    '',
    link(
      '/artikel',
      'Wedding articles',
      'guides on venue prices, Indonesian wedding traditions, preparation and paperwork'
    ),
    '',
    '## Optional',
    '',
    `- [Sitemap](${absoluteUrl('/sitemap.xml')}): every page in both languages`,
    ''
  ].join('\n');
}
