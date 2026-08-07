/**
 * Sitemap XML for a bilingual site.
 *
 * The one thing that is easy to get wrong, and that this module exists to get
 * right: a page that exists in two languages is *two* URLs, and each of them
 * needs its own <url> entry carrying the complete set of alternates -- including
 * a self-referencing one. Listing the Indonesian URL with an English
 * <xhtml:link> hanging off it looks reasonable and is the common mistake;
 * search engines drop the annotation because the English URL never appeared as
 * a <loc> and never pointed back. `expand()` below is what produces both sides.
 *
 * x-default points at Indonesian throughout: it is the canonical content and
 * the base locale, so it is the right landing place for an unmatched language.
 */

import { canonicalUrl } from '$lib/seo/schema';

/** One page, in every language it exists in, keyed by locale. */
export type SitemapEntry = {
  /** Locale code to path (or absolute URL). Must contain at least `id`. */
  alternates: Record<string, string>;
  /** ISO date or datetime. Anything unparseable is dropped rather than guessed. */
  lastmod?: string | null;
};

const XML_ESCAPES: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&apos;'
};

function escapeXml(value: string): string {
  return value.replace(/[&<>"']/g, (char) => XML_ESCAPES[char]);
}

/**
 * `<lastmod>` as a plain date. A blank or unparseable input returns null so the
 * element is left out -- an absent lastmod is a non-signal, while a wrong one
 * actively misleads a crawler about what has changed.
 */
export function lastmodDate(value: string | null | undefined): string | null {
  if (!value) return null;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toISOString().slice(0, 10);
}

function alternateLinks(alternates: Record<string, string>): string {
  const links = Object.entries(alternates).map(
    ([locale, href]) =>
      `    <xhtml:link rel="alternate" hreflang="${escapeXml(locale)}" href="${escapeXml(canonicalUrl(href))}" />`
  );
  if (alternates.id) {
    links.push(
      `    <xhtml:link rel="alternate" hreflang="x-default" href="${escapeXml(canonicalUrl(alternates.id))}" />`
    );
  }
  return links.join('\n');
}

function expand(entry: SitemapEntry): string[] {
  const links = alternateLinks(entry.alternates);
  const lastmod = lastmodDate(entry.lastmod);

  return Object.values(entry.alternates).map((href) =>
    [
      '  <url>',
      `    <loc>${escapeXml(canonicalUrl(href))}</loc>`,
      ...(lastmod ? [`    <lastmod>${lastmod}</lastmod>`] : []),
      links,
      '  </url>'
    ].join('\n')
  );
}

export function buildSitemap(entries: SitemapEntry[]): string {
  const urls = entries.flatMap(expand).join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls}
</urlset>
`;
}
