import { SITE_URL } from '$lib/seo/schema';

/**
 * Served from a route rather than static/robots.txt so the sitemap line carries
 * the same origin constant the rest of the SEO code uses -- a hardcoded copy in
 * a static file is the kind that goes stale silently.
 *
 * /api/ is disallowed because those are the web app's own form endpoints; they
 * are not pages, and crawling them submits nothing useful.
 */
const BODY = `User-agent: *
Allow: /
Disallow: /api/

Sitemap: ${SITE_URL}/sitemap.xml
`;

export function GET({ setHeaders }) {
  setHeaders({
    'content-type': 'text/plain; charset=utf-8',
    'cache-control': 'public, max-age=86400'
  });

  return new Response(BODY);
}
