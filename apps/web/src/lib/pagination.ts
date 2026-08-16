/**
 * Condense long runs to first / last / current-and-neighbours so ten pages of
 * results do not wrap onto three lines on a phone.
 */
export function pageWindow(current: number, total: number): (number | 'gap')[] {
  if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1);

  const wanted = [1, total, current, current - 1, current + 1]
    .filter((page, index, all) => page >= 1 && page <= total && all.indexOf(page) === index)
    .sort((a, b) => a - b);

  return wanted.flatMap((page, index) =>
    index > 0 && page - wanted[index - 1] > 1 ? ['gap' as const, page] : [page]
  );
}

/**
 * A page link that carries the rest of the query string with it. The venue
 * search filters on `q`, `city`, `stars_min` and a repeatable `stars`, so the
 * bare `?page=2` the article list uses would silently reset the very search it
 * is meant to page through.
 *
 * Returned relative, which is also what keeps the `/en` prefix: the English
 * site is a path prefix, so replacing only the query leaves the locale alone.
 */
export function paginationHref(url: URL, target: number): string {
  const params = new URLSearchParams(url.search);

  // Page 1 is the unparameterised URL. Leaving ?page=1 on it would publish a
  // second address serving results identical to the bare one.
  if (target <= 1) params.delete('page');
  else params.set('page', String(target));

  const query = params.toString();
  return query ? `?${query}` : url.pathname;
}
