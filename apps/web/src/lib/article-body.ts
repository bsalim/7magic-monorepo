import { localizeHref } from '$lib/paraglide/runtime';
import { SITE_URL } from '$lib/seo/schema';

/**
 * Rewrites the links inside CMS-authored article HTML so they stay in the
 * reader's locale.
 *
 * Article bodies are written in the CMS editor, which inserts whatever the
 * author pasted -- in practice `https://7magicwedding.com/artikel/...`, an
 * absolute link to the Indonesian site. Rendered inside `{@html}` those bypass
 * every `localizeHref` call in the codebase, so an English reader following a
 * cross-reference silently left /en. No lint or type check can see them; they
 * are data.
 *
 * Only `href` is touched. An `src` pointing at the old domain is a legacy image
 * that still has to resolve there, and localizing it would 404.
 *
 * For an article link this produces the structurally localized path
 * (`/en/articles/<id-category>/<id-slug>`), which the detail route answers with
 * a 301 to the English slug. The slugs are content the client cannot know, so
 * one redirect is the cost of not dropping the locale -- still better than
 * landing the reader on Indonesian text.
 */
export function localizeArticleBody(html: string): string {
  if (!html) return html;

  return html.replace(/href="([^"]+)"/g, (match, target: string) => {
    const path = internalPath(target);
    if (!path) return match;
    return `href="${localizeHref(path)}"`;
  });
}

/**
 * The site-relative path for a link, or null if it points somewhere this app
 * does not serve. Anchors and query-only links have no path to localize.
 */
function internalPath(target: string): string | null {
  if (target.startsWith(SITE_URL)) {
    return target.slice(SITE_URL.length) || '/';
  }
  // The live site is also reachable on www, and editors paste both forms.
  const withoutWww = SITE_URL.replace('://', '://www.');
  if (target.startsWith(withoutWww)) {
    return target.slice(withoutWww.length) || '/';
  }
  // Root-relative, but not the protocol-relative `//host/path`.
  if (target.startsWith('/') && !target.startsWith('//')) {
    return target;
  }
  return null;
}
