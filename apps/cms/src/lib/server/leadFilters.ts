/**
 * The leads filters, read off the CMS URL and passed through to the API under the
 * same snake_case names. Shared by the page load and the CSV proxy so an export
 * always matches the list it was clicked from.
 */
export const LEAD_FILTERS = ['source', 'q', 'date_from', 'date_to'] as const;

export type LeadFilters = Record<(typeof LEAD_FILTERS)[number], string>;

export function readLeadFilters(url: URL): LeadFilters {
  return Object.fromEntries(
    LEAD_FILTERS.map((name) => [name, (url.searchParams.get(name) ?? '').trim()])
  ) as LeadFilters;
}

/** Only the filters that are set: an empty `date_from=` would fail the API's date parsing. */
export function leadFilterQuery(filters: LeadFilters, page?: number): URLSearchParams {
  const query = new URLSearchParams();
  for (const name of LEAD_FILTERS) {
    if (filters[name]) query.set(name, filters[name]);
  }
  if (page && page > 1) query.set('page', String(page));
  return query;
}
