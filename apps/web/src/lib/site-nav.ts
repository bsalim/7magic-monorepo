/**
 * The public site's navigation, read by both the header and the footer.
 *
 * One list for both, because they had drifted: the footer's services column
 * carried a "mirrors the header" comment and still missed half the pages the
 * header linked, and the showcases and tour pages had no footer link at all.
 * A page added here now appears in both places or neither.
 *
 * Functions rather than constants: labels come from Paraglide and have to be
 * read in the active locale, at render time.
 */

import { m } from '$lib/paraglide/messages.js';

export type NavLink = { href: string; label: string; desc?: string };

export type VenueRegion = {
  key: 'jabodetabek' | 'bali' | 'batam' | 'singapore';
  label: string;
  /** The region's own landing pages: packages and planning, not search results. */
  packages: NavLink[];
  /** Its city venue hubs. */
  venues: NavLink[];
};

export const ALL_VENUES_HREF = '/wedding-venue/search';
export const VENDORS_HREF = '/our-vendors';
export const TOOLS_HREF = '/wedding-tools';

function cityVenues(slug: string, city: string): NavLink {
  return { href: `/wedding-venue/${slug}`, label: m.nav_city_venues({ city }) };
}

/**
 * The Wedding Venue menu, one column per region the business operates in.
 *
 * The city hubs are listed by hand even though the sitemap derives them from
 * the catalogue: a menu is an editorial choice, and a city that opens with one
 * venue should not push itself into the header unasked. The sitemap still
 * reaches such a city, so it is never orphaned for crawlers.
 *
 * Landing pages sit inside their region rather than as top-level links: the
 * Singapore, Jabodetabek and Bali pages are each "weddings in a place", which
 * is what this menu is organised by.
 */
export function venueRegions(): VenueRegion[] {
  const singapore = m.nav_region_singapore();
  return [
    {
      key: 'jabodetabek',
      label: 'Jabodetabek',
      packages: [{ href: '/jabodetabek-wedding', label: m.service_wedding_jabodetabek() }],
      venues: [
        cityVenues('jakarta', 'Jakarta'),
        cityVenues('tangerang', 'Tangerang'),
        cityVenues('bogor', 'Bogor'),
        cityVenues('bekasi', 'Bekasi')
      ]
    },
    {
      key: 'bali',
      label: 'Bali',
      packages: [
        { href: '/bali-wedding-planning', label: m.service_bali_wedding() },
        { href: '/bali-wedding-cost', label: m.service_bali_cost() },
        { href: '/legally-married-in-bali', label: m.service_bali_legal() }
      ],
      venues: [cityVenues('bali', 'Bali')]
    },
    {
      key: 'batam',
      label: 'Batam',
      // The Batam package page is still to be written; it goes here.
      packages: [],
      venues: [cityVenues('batam', 'Batam')]
    },
    {
      key: 'singapore',
      label: singapore,
      packages: [{ href: '/wedding-planning-singapore', label: m.service_wedding_singapore() }],
      venues: [cityVenues('singapore', singapore)]
    }
  ];
}

/** Packages and services that are not tied to one region. */
export function packageLinks(): NavLink[] {
  return [
    { href: '/paket-sangjit', label: m.service_sangjit(), desc: m.service_sangjit_desc() },
    { href: '/perjanjian-pranikah', label: m.service_prenup(), desc: m.service_prenup_desc() }
  ];
}

export function inspirationLinks(): NavLink[] {
  return [
    { href: '/wedding-showcases', label: m.nav_showcases(), desc: m.nav_showcases_desc() },
    { href: '/artikel', label: m.nav_articles(), desc: m.nav_articles_desc() },
    { href: TOOLS_HREF, label: m.nav_wedding_tools(), desc: m.nav_wedding_tools_desc() }
  ];
}

/**
 * The live wedding tools, each a page of its own under the hub. The header
 * stops at the hub, which is enough of a menu for a handful of calculators; the
 * footer lists these too, since it is the site map and every tool is in the
 * sitemap.
 */
export function toolLinks(): NavLink[] {
  return [
    { href: `${TOOLS_HREF}/mahar-tanggal-pernikahan`, label: m.tools_mahar_name() },
    { href: `${TOOLS_HREF}/generator-hashtag-pernikahan`, label: m.tools_hashtag_name() },
    { href: `${TOOLS_HREF}/kalkulator-bazi-pasangan`, label: m.tools_bazi_name() },
    { href: `${TOOLS_HREF}/bali-wedding-cost-calculator`, label: m.tools_bali_cost_name() },
    { href: `${TOOLS_HREF}/bali-wedding-date-planner`, label: m.tools_bali_dates_name() }
  ];
}

/** Event organizer pages, one per city, kept apart from weddings. */
export function eventLinks(): NavLink[] {
  return [
    { href: '/bali-event-organizer', label: m.service_bali_event(), desc: m.service_bali_event_desc() }
  ];
}

/** The landing page that pitches the tour, then the page that books one. */
export function tourLinks(): NavLink[] {
  return [
    { href: '/free-venue-tour', label: m.nav_free_venue_tour() },
    { href: '/tour', label: m.nav_book_tour() }
  ];
}

export function companyLinks(): NavLink[] {
  return [
    { href: '/about', label: m.nav_about() },
    { href: VENDORS_HREF, label: m.nav_vendors() },
    { href: '/contact', label: m.nav_contact() }
  ];
}

export function legalLinks(): NavLink[] {
  return [
    { href: '/privacy', label: m.footer_privacy() },
    { href: '/terms', label: m.footer_terms() }
  ];
}
