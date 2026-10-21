/**
 * Routes with no data behind them. Listed explicitly rather than discovered from
 * the filesystem, because "has a +page.svelte" and "should be in the sitemap"
 * are different questions -- /articles is a redirect and belongs in neither.
 *
 * Outside the sitemap route so the footer's test can hold the footer to it:
 * every page listed here must be one link away from any page on the site.
 */
export const STATIC_PATHS = [
  '/',
  '/artikel',
  '/wedding-venue/search',
  '/wedding-showcases',
  '/our-vendors',
  '/about',
  '/contact',
  '/free-venue-tour',
  '/tour',
  '/paket-sangjit',
  '/perjanjian-pranikah',
  '/bali-wedding-planning',
  '/bali-wedding-cost',
  '/legally-married-in-bali',
  '/wedding-planning-singapore',
  '/jabodetabek-wedding',
  '/bali-event-organizer',
  '/wedding-tools',
  '/wedding-tools/mahar-tanggal-pernikahan',
  '/wedding-tools/generator-hashtag-pernikahan',
  '/wedding-tools/kalkulator-bazi-pasangan',
  '/wedding-tools/bali-wedding-cost-calculator',
  '/wedding-tools/bali-wedding-date-planner',
  '/privacy',
  '/terms'
];
