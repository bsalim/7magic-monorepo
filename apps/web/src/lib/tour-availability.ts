export type OpeningHour = {
  dayOfWeek: number; // ISO: Monday = 1 ... Sunday = 7
  opensAtLocal: string; // "10:00:00"
  closesAtLocal: string;
};

/** ISO weekday for a "YYYY-MM-DD" string, without dragging the browser timezone
 * into it: `new Date('2026-09-07')` is parsed as UTC midnight, which lands on the
 * previous day west of Greenwich. */
export function isoWeekday(isoDate: string): number {
  const [year, month, day] = isoDate.split('-').map(Number);
  const weekday = new Date(Date.UTC(year, month - 1, day)).getUTCDay();
  return weekday === 0 ? 7 : weekday;
}

const toMinutes = (value: string) => {
  const [hours, minutes] = value.split(':').map(Number);
  return hours * 60 + minutes;
};

const pad = (value: number) => String(value).padStart(2, '0');

export function isDateBookable(
  isoDate: string,
  hours: OpeningHour[],
  closedDates: string[]
): boolean {
  if (closedDates.includes(isoDate)) {
    return false;
  }
  const weekday = isoWeekday(isoDate);
  return hours.some((hour) => hour.dayOfWeek === weekday);
}

/** Slots on the hour, from opening onwards, that leave at least 30 minutes before
 * closing. Slots are an hour apart but only need half an hour of room, so a window
 * closing at 10:30 still offers 10:00 as its last slot -- and never 10:30, which
 * would put a guest at the door as it locks. */
export function slotsForDate(isoDate: string, hours: OpeningHour[]): string[] {
  const weekday = isoWeekday(isoDate);
  const slots: string[] = [];

  for (const hour of hours.filter((row) => row.dayOfWeek === weekday)) {
    const opens = toMinutes(hour.opensAtLocal);
    const closes = toMinutes(hour.closesAtLocal);
    for (let start = opens; start + 30 <= closes; start += 60) {
      slots.push(`${pad(Math.floor(start / 60))}:${pad(start % 60)}`);
    }
  }

  return [...new Set(slots)].sort();
}
