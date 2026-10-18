import { describe, expect, it } from 'vitest';
import type { ArticleDetail, VenueCard, VenueDetail } from '$lib/api';
import { OFFICES, OFFICE_ADDRESSES } from '$lib/offices';
import { localizeHref } from '$lib/paraglide/runtime';
import {
  FOUNDING_YEAR,
  ORGANIZATION_ID,
  SITE_URL,
  absoluteUrl,
  articleNode,
  breadcrumbList,
  canonicalUrl,
  countryCodeFor,
  faqPage,
  graph,
  jsonLdScript,
  landingPageJsonLd,
  optionalUrl,
  organization,
  serviceNode,
  toolPageJsonLd,
  venueItemList,
  venueNode,
  venuePackageNode,
  webApplicationNode,
  webPageNode
} from './schema';

describe('faqPage', () => {
  it('wraps each question and answer as a Question with an accepted Answer', () => {
    const node = faqPage([
      { q: 'Berapa harga paket wedding di Jakarta?', a: 'Mulai Rp 45 juta.' },
      { q: 'Bisa lihat venue-nya dulu?', a: 'Bisa, kunjungan gratis.' }
    ]);

    expect(node).toEqual({
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'Berapa harga paket wedding di Jakarta?',
          acceptedAnswer: { '@type': 'Answer', text: 'Mulai Rp 45 juta.' }
        },
        {
          '@type': 'Question',
          name: 'Bisa lihat venue-nya dulu?',
          acceptedAnswer: { '@type': 'Answer', text: 'Bisa, kunjungan gratis.' }
        }
      ]
    });
  });
});

const card = (over: Partial<VenueCard> = {}): VenueCard => ({
  id: 1,
  name: 'Grand Ballroom',
  slug: 'grand-ballroom',
  city: 'jakarta',
  district: 'Kuningan',
  address: '',
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

  it('keeps the root slash while trimming it below the root', () => {
    // canonicalUrl strips a trailing slash on anything *below* the root only:
    // `https://host/` is the conventional form for a homepage, and rewriting it to
    // `https://host` would be the change that redirects.
    const crumbs = breadcrumbList([
      { name: 'Home', path: '/' },
      { name: 'Venues', path: '/wedding-venue/search' }
    ]);
    expect(crumbs.itemListElement[0].item).toBe(`${SITE_URL}/`);
    expect(crumbs.itemListElement[1].item).toBe(`${SITE_URL}/wedding-venue/search`);
  });

  it('localizes each link, so an English trail does not point at Indonesian URLs', () => {
    const crumbs = breadcrumbList([{ name: 'Venues', path: '/wedding-venue/search' }]);
    // Under the base locale this is the unprefixed path; the point of the test is
    // that the value went through localizeHref rather than being pasted verbatim.
    expect(crumbs.itemListElement[0].item).toBe(
      canonicalUrl(localizeHref('/wedding-venue/search'))
    );
  });
});

describe('venueNode images', () => {
  it('emits the whole gallery when given one, deduplicated', () => {
    const node = venueNode(card(), {
      image: 'https://cdn.test/a.jpg',
      images: ['https://cdn.test/a.jpg', 'https://cdn.test/a.jpg', 'https://cdn.test/b.jpg']
    });
    expect(node.image).toEqual(['https://cdn.test/a.jpg', 'https://cdn.test/b.jpg']);
  });

  it('falls back to the single cover for a listing entry with no gallery', () => {
    const node = venueNode(card(), { image: 'https://cdn.test/a.jpg' });
    expect(node.image).toBe('https://cdn.test/a.jpg');
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
    published_at: '2026-01-01T00:00:00',
    related: []
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

describe('organization', () => {
  it('states the founding year, every served region and a contact point', () => {
    const org = organization();
    expect(org.foundingDate).toBe(String(FOUNDING_YEAR));
    expect(org.areaServed).toEqual(
      expect.arrayContaining(['Jakarta', 'Bali', 'Batam', 'Singapore'])
    );
    expect(org.contactPoint.availableLanguage).toEqual(['Indonesian', 'English']);
  });

  it('places each office at the address the footer prints', () => {
    const org = organization();
    expect(org.location).toHaveLength(3);
    for (const key of Object.keys(OFFICE_ADDRESSES) as (keyof typeof OFFICES)[]) {
      expect(OFFICES[key].join(' ')).toContain(OFFICE_ADDRESSES[key].postalCode);
    }
    expect(org.address.postalCode).toBe(OFFICE_ADDRESSES.jakarta.postalCode);
  });
});

describe('serviceNode', () => {
  it('points at the organization rather than restating it', () => {
    const node = serviceNode({ url: '/paket-sangjit', name: 'Paket Sangjit', serviceType: 'x' });
    expect(node.provider).toEqual({ '@id': ORGANIZATION_ID });
    expect(node['@id']).toBe(`${SITE_URL}/paket-sangjit#service`);
  });

  // Structured data has to match the page; a price only in markup is the
  // kind Google penalises.
  it('carries no offer unless the page prints a price', () => {
    expect(serviceNode({ url: '/x', name: 'X', serviceType: 'x' }).offers).toBeUndefined();
    const priced = serviceNode({
      url: '/x',
      name: 'X',
      serviceType: 'x',
      offer: { price: '4000000' }
    });
    expect(priced.offers).toMatchObject({ price: '4000000', priceCurrency: 'IDR' });
  });
});

describe('landingPageJsonLd', () => {
  it('emits the full set a landing page needs, with the service as the page subject', () => {
    const html = landingPageJsonLd({
      path: '/bali-event-organizer',
      title: 'T',
      description: 'D',
      locale: 'id',
      crumbs: [{ name: 'Beranda', path: '/' }, { name: 'Bali Event Organizer' }],
      service: { name: 'Bali Event Organizer', serviceType: 'Corporate event organizing' },
      faqs: [{ q: 'Question?', a: 'Answer.' }]
    });
    const data = JSON.parse(html.replace(/^<script[^>]*>|<\/script>$/g, ''));
    const types = data['@graph'].map((node: { '@type': string }) => node['@type']);

    expect(types).toEqual([
      'Organization',
      'WebSite',
      'WebPage',
      'BreadcrumbList',
      'Service',
      'FAQPage'
    ]);
    expect(data['@graph'][2].mainEntity).toEqual({
      '@id': `${SITE_URL}/bali-event-organizer#service`
    });
  });

  it('leaves the FAQ out when the page has none', () => {
    const html = landingPageJsonLd({
      path: '/x',
      title: 'T',
      description: 'D',
      locale: 'id',
      crumbs: [{ name: 'X' }],
      service: { name: 'X', serviceType: 'x' }
    });
    expect(html).not.toContain('FAQPage');
  });
});

describe('webApplicationNode', () => {
  it('describes a free browser tool published by the company', () => {
    const node = webApplicationNode({
      url: '/wedding-tools/mahar-tanggal-pernikahan',
      name: 'Mahar dari Tanggal Pernikahan',
      description: 'D',
      locale: 'id'
    });

    expect(node).toMatchObject({
      '@type': 'WebApplication',
      '@id': `${SITE_URL}/wedding-tools/mahar-tanggal-pernikahan#app`,
      url: `${SITE_URL}/wedding-tools/mahar-tanggal-pernikahan`,
      applicationCategory: 'LifestyleApplication',
      operatingSystem: 'Any',
      isAccessibleForFree: true,
      inLanguage: 'id',
      publisher: { '@id': ORGANIZATION_ID },
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'IDR' }
    });
  });
});

describe('toolPageJsonLd', () => {
  const parse = (html: string) => JSON.parse(html.replace(/^<script[^>]*>|<\/script>$/g, ''));

  it('carries the app, its page, the breadcrumb and the FAQ', () => {
    const data = parse(
      toolPageJsonLd({
        path: '/en/wedding-tools/mahar-tanggal-pernikahan',
        title: 'T',
        description: 'D',
        locale: 'en',
        crumbs: [{ name: 'Home', path: '/' }, { name: 'Mahar' }],
        faqs: [{ q: 'Question?', a: 'Answer.' }]
      })
    );
    const types = data['@graph'].map((node: { '@type': string }) => node['@type']);

    expect(types).toEqual([
      'Organization',
      'WebSite',
      'WebPage',
      'BreadcrumbList',
      'WebApplication',
      'FAQPage'
    ]);
    const page = data['@graph'][2];
    expect(page.mainEntity).toEqual({
      '@id': `${SITE_URL}/en/wedding-tools/mahar-tanggal-pernikahan#app`
    });
    expect(page.inLanguage).toBe('en');
  });

  it('leaves the FAQ out when there is none', () => {
    const data = parse(
      toolPageJsonLd({ path: '/x', title: 'T', description: 'D', locale: 'id', crumbs: [] })
    );
    expect(data['@graph'].some((node: { '@type': string }) => node['@type'] === 'FAQPage')).toBe(
      false
    );
  });
});
