/**
 * Human-readable dates for the CMS: "18 Aug 2026", or "18 Aug" when the date
 * falls in the current year.
 *
 * The year is dropped only for the *current* year, so "18 Aug" always means this
 * year and never an ambiguous past one. Everything is read off the date parts
 * rather than through `new Date(iso)`: an ISO date string is parsed as UTC
 * midnight, which lands on the previous day for anyone west of Greenwich.
 */

const MONTHS = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec'
];

type DateParts = { year: number; month: number; day: number; hour?: number; minute?: number };

/** Pulls the parts out of "YYYY-MM-DD" or a full ISO timestamp, ignoring any zone. */
function parts(value: string): DateParts | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?/.exec(value.trim());
  if (!match) return null;

  const [, year, month, day, hour, minute] = match;
  const parsed = {
    year: Number(year),
    month: Number(month),
    day: Number(day),
    hour: hour === undefined ? undefined : Number(hour),
    minute: minute === undefined ? undefined : Number(minute)
  };
  if (parsed.month < 1 || parsed.month > 12 || parsed.day < 1 || parsed.day > 31) return null;
  return parsed;
}

/**
 * "18 Aug 2026", or "18 Aug" in the current year. Returns `fallback` for null,
 * empty or unparseable input so callers do not each repeat an em-dash check.
 */
export function formatDate(value: string | null | undefined, fallback = '—'): string {
  if (!value) return fallback;
  const date = parts(value);
  if (!date) return fallback;

  const stem = `${date.day} ${MONTHS[date.month - 1]}`;
  return date.year === new Date().getFullYear() ? stem : `${stem} ${date.year}`;
}

/** "18 Aug 2026, 14:30". Falls back to the date alone when there is no time. */
export function formatDateTime(value: string | null | undefined, fallback = '—'): string {
  if (!value) return fallback;
  const date = parts(value);
  if (!date) return fallback;
  if (date.hour === undefined || date.minute === undefined) return formatDate(value, fallback);

  const time = `${String(date.hour).padStart(2, '0')}:${String(date.minute).padStart(2, '0')}`;
  return `${formatDate(value, fallback)}, ${time}`;
}

/** "10 Aug → 10 Sep 2026" for a window, or `fallback` when either end is missing. */
export function formatDateRange(
  from: string | null | undefined,
  to: string | null | undefined,
  fallback = '—'
): string {
  if (!from || !to) return fallback;
  return `${formatDate(from, fallback)} → ${formatDate(to, fallback)}`;
}
