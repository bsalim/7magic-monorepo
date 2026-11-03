/**
 * Authors with a public profile page. Keyed by the display name the API returns
 * on an article, which is the only author field it exposes; an author missing
 * from this list still gets a plain byline, just with nothing to link to. If a
 * display name changes in the CMS (a surname added, say), update its key here.
 */
export const AUTHOR_SLUGS: Readonly<Record<string, string>> = {
  Fiona: 'fiona'
};

export const AUTHOR_PATHS: readonly string[] = Object.values(AUTHOR_SLUGS).map(
  (slug) => `/author/${slug}`
);

/** The unlocalized profile path for a display name, or null if it has none. */
export function authorPath(name: string): string | null {
  const slug = AUTHOR_SLUGS[name];
  return slug ? `/author/${slug}` : null;
}

/** The display name for a profile slug, or null if no such profile exists. */
export function authorNameForSlug(slug: string): string | null {
  return Object.keys(AUTHOR_SLUGS).find((name) => AUTHOR_SLUGS[name] === slug) ?? null;
}
