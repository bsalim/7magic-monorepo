import { localizeHref, type Locale } from '$lib/paraglide/runtime';

/**
 * Where the language switcher should point for `target`.
 *
 * `localizeHref` translates the path *structure*, which is the whole story for
 * every page whose URL is the same words in both languages. Articles are not one
 * of those: their category and slug segments are translated content, so the
 * structurally-localized path carries the other locale's words and only resolves
 * because the API recognises either locale's slug and 301s to the canonical one.
 * That redirect makes the wrong link look correct in a browser while the anchor
 * in the DOM disagrees with the page's own canonical and hreflang tags.
 *
 * So an `alternates` map from the API wins whenever it names the target locale.
 * It is absent on pages whose paths are locale-independent -- venues, showcases,
 * every static page -- and there `localizeHref` is already right.
 */
export function switcherHref(
  pathname: string,
  target: Locale,
  alternates?: Record<string, string>
): string {
  // A page may supply alternates that omit the target: an article with no
  // English translation does. Falling back keeps the switcher usable rather
  // than dropping the visitor on a dead link.
  return alternates?.[target] ?? localizeHref(pathname, { locale: target });
}
