import { describe, expect, it } from 'vitest';
import type { ArticleDetail, VenueCard, VenueDetail } from '$lib/api';
import {
  SITE_URL,
  absoluteUrl,
  articleNode,
  breadcrumbList,
  countryCodeFor,
  graph,
  jsonLdScript,
  optionalUrl,
  venueItemList,
  venueNode,
  venuePackageNode,
  webPageNode
} from './schema';

const card = (over: Partial<VenueCard> = {}): VenueCard => ({
  id: 1,
  name: 'Grand Ballroom',
  slug: 'grand-ballroom',
  city: 'jakarta',
  district: 'Kuningan',
  stars: 5,
  price_start_from: 120_000_000,
  price_for_total_pax: 300,
  path_url: '/wedding-venue/jakarta/grand-ballroom',
  cover_photo: { alt: '', small_url: 'https://cdn.example.com/a.jpg' },
  ...over
});

const detail = (over: Partial<VenueDetail> = {}): VenueDetail => ({
  ...card(),
  address: 'Jl. Sudirman 1',
  description: 'A ballroom.',
  status: 'published',
  gallery: [],
  packages: [
    { name: 'Silver', price: 120_000_000, pax: 300, note: '' },
    { name: 'Gold', price: 180_000_000, pax: 500, note: '' }
  ],
  ...over
});

// The parsed payload of a rendered block, which is what a crawler actually sees.
const parse = (script: string) =>
  JSON.parse(script.replace(/^<script type="application\/ld\+json">/, '').replace(/<\/script>$/, ''));

describe('absoluteUrl', () => {
  it('resolves a site path against the public origin', () => {
    expect(absoluteUrl('/articles')).toBe(`${SITE_URL}/articles`);
  });

  it('leaves an already-absolute CDN url alone', () => {
    expect(absoluteUrl('https://cdn.example.com/a.jpg')).toBe('https://cdn.example.com/a.jpg');
  });

  it('tolerates a path with no leading slash', () => {
    expect(absoluteUrl('articles')).toBe(`${SITE_URL}/articles`);
  });

  it('yields no url at all for a blank value', () => {
    expect(optionalUrl('')).toBeUndefined();
    expect(optionalUrl(null)).toBeUndefined();
  });
});

describe('jsonLdScript', () => {
  it('renders JSON a crawler can parse', () => {
    expect(parse(jsonLdScript(graph({ '@type': 'Thing', name: 'x' })))).toEqual({
      '@context': 'https://schema.org',
      '@graph': [{ '@type': 'Thing', name: 'x' }]
    });
  });

  // The whole block is injected with {@html}, so a closing tag inside CMS copy
  // would otherwise end the script and drop raw markup into the document.
  it('cannot be closed early by a script tag inside the data', () => {
    const script = jsonLdScript({ name: '</script><img src=x onerror=alert(1)>' });

    expect(script.match(/<\/script>/g)).toHaveLength(1);
    expect(script).not.toContain('<img');
    expect(parse(script).name).toBe('</script><img src=x onerror=alert(1)>');
  });
});

describe('breadcrumbList', () => {
  it('numbers the trail and makes every link absolute', () => {
    const crumbs = breadcrumbList([
      { name: 'Home', path: '/' },
      { name: 'Venues', path: '/wedding-venue/search' },
      { name: 'Grand Ballroom' }
    ]);

    expect(crumbs.itemListElement.map((c) => c.position)).toEqual([1, 2, 3]);
    expect(crumbs.itemListElement[1].item).toBe(`${SITE_URL}/wedding-venue/search`);
  });

  it('leaves the current page without a self-link', () => {
    const crumbs = breadcrumbList([{ name: 'Home', path: '/' }, { name: 'Here' }]);
    expect(crumbs.itemListElement[1].item).toBeUndefined();
  });
});

describe('webPageNode', () => {
  it('gives each locale of a page its own identity', () => {
    const id = webPageNode({ url: '/', name: 'Home', locale: 'id' });
    const en = webPageNode({ url: '/en', name: 'Home', locale: 'en' });

    expect(id['@id']).toBe(`${SITE_URL}/#webpage`);
    expect(en['@id']).toBe(`${SITE_URL}/en#webpage`);
    expect(id.inLanguage).toBe('id');
    expect(en.inLanguage).toBe('en');
  });

  // inLanguage is a CreativeWork property, so it belongs on the page node and
  // not on the venue (a Place) or the list (an Intangible) it describes.
  it('keeps the locale off the venue and list nodes', () => {
    const node = venueNode(card()) as Record<string, unknown>;
    const list = venueItemList([card()], { name: 'x', url: '/' }) as Record<string, unknown>;

    expect(node.inLanguage).toBeUndefined();
    expect(list.inLanguage).toBeUndefined();
  });
});

describe('venueNode', () => {
  it('types a star-rated venue as a hotel so starRating is valid', () => {
    const node = venueNode(card({ stars: 5 }));
    expect(node['@type']).toEqual(['EventVenue', 'Hotel']);
    expect(node.starRating).toEqual({ '@type': 'Rating', ratingValue: 5, bestRating: 5 });
  });

  // starRating is not a property of EventVenue, so an unrated venue must not
  // carry one rather than carrying a zero.
  it('drops starRating for an unrated venue', () => {
    const node = venueNode(card({ stars: 0 }));
    expect(node['@type']).toBe('EventVenue');
    expect(node.starRating).toBeUndefined();
  });

  it('addresses Singapore venues to SG and Indonesian ones to ID', () => {
    expect(countryCodeFor('singapore')).toBe('SG');
    expect(venueNode(card({ city: 'singapore' })).address.addressCountry).toBe('SG');
    expect(venueNode(card({ city: 'bali' })).address.addressCountry).toBe('ID');
  });

  it('identifies the venue by an absolute url', () => {
    const node = venueNode(card());
    expect(node['@id']).toBe(`${SITE_URL}/wedding-venue/jakarta/grand-ballroom#venue`);
    expect(node.url).toBe(`${SITE_URL}/wedding-venue/jakarta/grand-ballroom`);
  });
});

describe('venuePackageNode', () => {
  it('aggregates the package prices into one offer range', () => {
    const node = venuePackageNode(detail())!;
    expect(node.offers.lowPrice).toBe(120_000_000);
    expect(node.offers.highPrice).toBe(180_000_000);
    expect(node.offers.offerCount).toBe(2);
    expect(node.offers.priceCurrency).toBe('IDR');
  });

  // A Product with no offer fails validation everywhere it is consumed, so an
  // on-request venue is better off with no Product node at all.
  it('emits nothing for a venue priced on request', () => {
    expect(venuePackageNode(detail({ price_start_from: null, packages: [] }))).toBeUndefined();
  });
});

describe('venueItemList', () => {
  it('continues positions across pages instead of restarting', () => {
    const list = venueItemList([card(), card({ slug: 'b', path_url: '/wedding-venue/bali/b' })], {
      name: 'Results',
      url: '/wedding-venue/search?page=2',
      startPosition: 13
    });

    expect(list.itemListElement.map((i) => i.position)).toEqual([13, 14]);
    expect(list.numberOfItems).toBe(2);
    expect(list.itemListElement[0].item['@type']).toEqual(['EventVenue', 'Hotel']);
  });
});

describe('articleNode', () => {
  const article: ArticleDetail = {
    id: 1,
    title: 'Wedding planning in Jakarta',
    slug: 'wedding-planning',
    category: 'planning',
    summary: 'How to plan.',
    image_url: '/img/a.jpg',
    author: 'Fiona',
    status: 'published',
    featured: false,
    updated_at: '2026-02-01T00:00:00',
    path: '/artikel/planning/wedding-planning',
    alternates: {
      id: '/artikel/planning/wedding-planning',
      en: '/en/articles/planning/wedding-planning-en'
    },
    content: '<p>x</p>',
    topic: ['venue', 'budget'],
    word_count: 900,
    published_at: '2026-01-01T00:00:00'
  };

  it('carries the dates, author and publisher a BlogPosting needs', () => {
    const node = articleNode(article, '/artikel/planning/wedding-planning', 'id');

    expect(node['@type']).toBe('BlogPosting');
    expect(node.datePublished).toBe('2026-01-01T00:00:00');
    expect(node.dateModified).toBe('2026-02-01T00:00:00');
    expect(node.author).toEqual({ '@type': 'Person', name: 'Fiona' });
    expect(node.image).toBe(`${SITE_URL}/img/a.jpg`);
    expect(node.mainEntityOfPage['@id']).toBe(`${SITE_URL}/artikel/planning/wedding-planning`);
  });

  it('falls back to the publish date when the article was never edited', () => {
    const node = articleNode({ ...article, updated_at: '' }, '/artikel/a/b', 'id');
    expect(node.dateModified).toBe('2026-01-01T00:00:00');
  });

  // Google truncates at 110 characters; sending more just gets cut.
  it('trims an over-long headline', () => {
    const node = articleNode({ ...article, title: 'x'.repeat(200) }, '/artikel/a/b', 'id');
    expect(node.headline.length).toBeLessThanOrEqual(110);
  });
});
