import type { Range } from '$lib/tools/bali-cost';

/**
 * Formatting for the Bali-for-Australians pages, which are written for an
 * Australian reader: dollars as A$, day before month, short month names.
 * Dates are parsed and printed in UTC so a server in one zone and a browser in
 * another never disagree by a day.
 */

const AUD = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 0 });
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export function formatAud(amount: number): string {
  return `A$${AUD.format(amount)}`;
}

export function formatAudRange(range: Range): string {
  if (range.low === range.high) return formatAud(range.low);
  return `${formatAud(range.low)} – ${formatAud(range.high)}`;
}

export function monthLabel(year: number, month: number): string {
  const name = new Intl.DateTimeFormat('en-AU', { month: 'long', timeZone: 'UTC' }).format(
    new Date(Date.UTC(year, month - 1, 1))
  );
  return `${name} ${year}`;
}

const parts = (iso: string) => {
  const date = new Date(`${iso}T00:00:00Z`);
  return {
    day: date.getUTCDate(),
    month: MONTHS[date.getUTCMonth()],
    year: date.getUTCFullYear(),
    weekday: WEEKDAYS[date.getUTCDay()]
  };
};

/** "Mon 8 Mar 2027", "9–15 Mar 2027", "27 Sep – 8 Oct 2027", "21 Dec 2027 – 28 Jan 2028". */
export function formatDateRange(start: string, end: string): string {
  const a = parts(start);
  const b = parts(end);
  if (start === end) return `${a.weekday} ${a.day} ${a.month} ${a.year}`;
  if (a.year !== b.year) return `${a.day} ${a.month} ${a.year} – ${b.day} ${b.month} ${b.year}`;
  if (a.month !== b.month) return `${a.day} ${a.month} – ${b.day} ${b.month} ${b.year}`;
  return `${a.day}–${b.day} ${a.month} ${a.year}`;
}
