/**
 * Schema.org JSON-LD builders.
 *
 * Two things are easy to get wrong here, which is why every page goes through
 * this module rather than hand-rolling its own block:
 *
 * 1. Svelte parses the contents of a `<script>` element as raw text. An
 *    expression inside `<script type="application/ld+json">{jsonLd}</script>`
 *    is emitted as the literal characters `{jsonLd}`, not the JSON — the venue
 *    detail page shipped exactly that for months. The tag has to be built as a
 *    string and injected with `{@html}`; see `jsonLdScript`.
 * 2. Crawlers have nothing to resolve a relative path against, so `@id`, `url`,
 *    `item` and `image` must all be absolute. Everything that leaves this
 *    module already is.
 */

import type { ArticleDetail, VenueCard, VenueDetail } from '$lib/api';
import { titleCase } from '$lib/utils';
import { whatsappDisplay, whatsappNumber } from '$lib/whatsapp';

/**
 * The public origin, hardcoded rather than read from `page.url.origin`: a
 * preview host or a localhost render would otherwise emit `@id` values that no
 * crawler can resolve, and `@id` has to stay stable to be worth anything.
 * Matches the canonical links on the standalone landing pages.
 */
export const SITE_URL = 'https://7magicwedding.com';

/** Stable node identities, so pages can reference the org instead of restating it. */
export const ORGANIZATION_ID = `${SITE_URL}/#organization`;
export const WEBSITE_ID = `${SITE_URL}/#website`;

const CURRENCY = 'IDR';

/** Absolute URL for a site path. Already-absolute URLs (CDN photos) pass through. */
export function absoluteUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  return `${SITE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}

/** As `absoluteUrl`, but blank input yields no property rather than a bare origin. */
export function optionalUrl(path: string | null | undefined): string | undefined {
  return path ? absoluteUrl(path) : undefined;
}

/**
 * Renders a JSON-LD block ready for `{@html}`.
 *
 * Every `<` is rewritten to its JSON unicode escape. The parsed string is
 * unchanged, but a closing script tag inside a CMS-authored field (an article
 * summary, a venue description) can no longer end the block early and spill
 * markup into the page.
 */
export function jsonLdScript(data: unknown): string {
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  return `<script type="application/ld+json">${json}</script>`;
}

/** Wraps nodes in the envelope every page shares. */
export function graph(...nodes: unknown[]) {
  return { '@context': 'https://schema.org', '@graph': nodes.filter(Boolean) };
}

export function organization() {
  return {
    '@type': 'Organization',
    '@id': ORGANIZATION_ID,
    name: '7Magic Wedding',
    url: SITE_URL,
    logo: {
      '@type': 'ImageObject',
      url: absoluteUrl('/img/7magic-logo.png'),
      width: 129,
      height: 48
    },
    email: 'hello@7magic.id',
    telephone: whatsappDisplay,
    // Text is a valid areaServed value, and avoids asserting that Bali is a
    // city or that Singapore is one of ours to administer.
    areaServed: ['Jakarta', 'Bali', 'Singapore'],
    sameAs: ['https://www.instagram.com/7magicwedding', `https://wa.me/${whatsappNumber}`]
  };
}

export function website() {
  return {
    '@type': 'WebSite',
    '@id': WEBSITE_ID,
    url: SITE_URL,
    name: '7Magic Wedding',
    publisher: { '@id': ORGANIZATION_ID },
    inLanguage: ['id', 'en'],
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${SITE_URL}/wedding-venue/search?q={search_term_string}`
      },
      'query-input': 'required name=search_term_string'
    }
  };
}

/**
 * The page itself, and the only place the locale belongs: `inLanguage` is
 * defined on CreativeWork, so it is valid here and on BlogPosting but not on
 * EventVenue (a Place) or ItemList (an Intangible). Declaring it here is what
 * tells a crawler that /en and / are the same page in two languages.
 */
export function webPageNode(options: {
  url: string;
  name: string;
  locale: string;
  type?: 'WebPage' | 'CollectionPage';
  description?: string;
  about?: string;
  image?: string | null;
  mainEntity?: unknown;
}) {
  const url = absoluteUrl(options.url);
  return {
    '@type': options.type ?? 'WebPage',
    '@id': `${url}#webpage`,
    url,
    name: options.name,
    description: options.description || undefined,
    isPartOf: { '@id': WEBSITE_ID },
    about: options.about ? { '@id': options.about } : undefined,
    primaryImageOfPage: options.image
      ? { '@type': 'ImageObject', url: absoluteUrl(options.image) }
      : undefined,
    mainEntity: options.mainEntity ?? undefined,
    inLanguage: options.locale
  };
}

export type Crumb = { name: string; path?: string };

/**
 * The trailing crumb is the current page. Google's spec allows its `item` to be
 * omitted, and leaving it off keeps the page out of its own breadcrumb links.
 */
export function breadcrumbList(trail: Crumb[]) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: trail.map((crumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: crumb.name,
      item: crumb.path ? absoluteUrl(crumb.path) : undefined
    }))
  };
}

/** ISO 3166-1 alpha-2, since not every city in the catalogue is Indonesian. */
export function countryCodeFor(city: string): string {
  return city.trim().toLowerCase() === 'singapore' ? 'SG' : 'ID';
}

type VenueLike = VenueCard & Partial<Pick<VenueDetail, 'address' | 'description'>>;

/**
 * One venue, usable both as the primary entity of its detail page and as an
 * entry in a listing. `@id` is derived from the venue URL so the two forms
 * describe the same node rather than competing duplicates.
 */
export function venueNode(venue: VenueLike, options: { image?: string | null } = {}) {
  const url = absoluteUrl(venue.path_url);
  // starRating is defined only on LodgingBusiness and FoodEstablishment, so a
  // plain EventVenue cannot carry one. The star count comes from the hotel
  // rating, so venues that have it are typed as both and the rest stay venues.
  const rated = venue.stars > 0;

  return {
    '@type': rated ? ['EventVenue', 'Hotel'] : 'EventVenue',
    '@id': `${url}#venue`,
    name: venue.name,
    url,
    description: venue.description || undefined,
    image: optionalUrl(options.image ?? venue.cover_photo?.small_url),
    address: {
      '@type': 'PostalAddress',
      streetAddress: venue.address || undefined,
      addressLocality: venue.district || undefined,
      addressRegion: titleCase(venue.city),
      addressCountry: countryCodeFor(venue.city)
    },
    maximumAttendeeCapacity: venue.price_for_total_pax || undefined,
    starRating: rated
      ? { '@type': 'Rating', ratingValue: venue.stars, bestRating: 5 }
      : undefined
  };
}

/**
 * The bookable package for a venue.
 *
 * Returns nothing when the venue has no price: a Product with no offer is
 * invalid for every rich result that consumes it, so an omitted node beats a
 * broken one. Venues priced on request fall into this case by design.
 */
export function venuePackageNode(venue: VenueDetail) {
  const packages = venue.packages ?? [];
  const prices = packages.map((item) => item.price).filter((price) => price > 0);
  const low = venue.price_start_from || (prices.length ? Math.min(...prices) : 0);
  if (!low) return undefined;

  const url = absoluteUrl(venue.path_url);
  const high = prices.length ? Math.max(...prices) : low;

  return {
    '@type': 'Product',
    '@id': `${url}#package`,
    name: `Wedding Package at ${venue.name}`,
    description: venue.description || undefined,
    image: optionalUrl(venue.cover_photo?.small_url),
    url,
    brand: { '@id': ORGANIZATION_ID },
    // The venue is where the package is delivered, not the product itself.
    areaServed: titleCase(venue.city),
    offers: {
      '@type': 'AggregateOffer',
      priceCurrency: CURRENCY,
      lowPrice: low,
      highPrice: high,
      offerCount: packages.length || 1,
      seller: { '@id': ORGANIZATION_ID },
      offers: packages
        .filter((item) => item.price > 0)
        .map((item) => ({
          '@type': 'Offer',
          name: item.name,
          price: item.price,
          priceCurrency: CURRENCY,
          url,
          availability: 'https://schema.org/InStock',
          eligibleQuantity: {
            '@type': 'QuantitativeValue',
            value: item.pax,
            unitText: 'pax'
          }
        }))
    }
  };
}

/**
 * A listing of venues. Positions are 1-based across the whole result set, so
 * page 2 continues from where page 1 stopped rather than restarting at 1.
 */
export function venueItemList(
  venues: VenueCard[],
  options: { name: string; url: string; startPosition?: number }
) {
  const start = options.startPosition ?? 1;
  return {
    '@type': 'ItemList',
    name: options.name,
    url: absoluteUrl(options.url),
    numberOfItems: venues.length,
    itemListElement: venues.map((venue, index) => ({
      '@type': 'ListItem',
      position: start + index,
      item: venueNode(venue)
    }))
  };
}

/** Google truncates headlines past 110 characters, so do not send more. */
function headline(title: string): string {
  return title.length <= 110 ? title : `${title.slice(0, 109).trimEnd()}…`;
}

export function articleNode(article: ArticleDetail, path: string, locale: string) {
  const url = absoluteUrl(path);
  return {
    '@type': 'BlogPosting',
    '@id': `${url}#article`,
    headline: headline(article.title),
    description: article.summary || undefined,
    image: optionalUrl(article.image_url),
    datePublished: article.published_at || undefined,
    // Falls back to the publish date: an article that has never been edited is
    // still modified as of the day it went out, and Google wants both.
    dateModified: article.updated_at || article.published_at || undefined,
    author: { '@type': 'Person', name: article.author },
    publisher: { '@id': ORGANIZATION_ID },
    mainEntityOfPage: { '@type': 'WebPage', '@id': url },
    articleSection: article.category || undefined,
    keywords: article.topic?.length ? article.topic : undefined,
    wordCount: article.word_count || undefined,
    inLanguage: locale
  };
}
