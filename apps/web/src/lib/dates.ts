/**
 * A long-form date in the visitor's language -- "12 September 2026" and
 * "12 September 2026" happen to coincide, since Indonesian and British English
 * share the day-month-year order, but the month names differ.
 *
 * Rendered in Jakarta time: the API stamps dates with +07:00, and a server
 * running on UTC would otherwise show the previous day for anything published
 * before 7am. Missing or unparseable input renders nothing rather than
 * "Invalid Date".
 */
export function formatLongDate(iso: string | null | undefined, locale: string): string {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';

  return new Intl.DateTimeFormat(locale === 'id' ? 'id-ID' : 'en-GB', {
    dateStyle: 'long',
    timeZone: 'Asia/Jakarta'
  }).format(date);
}
