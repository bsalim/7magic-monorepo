/**
 * Shared by every wedding tool's lead gate: the WhatsApp normaliser and the
 * "already unlocked" flag.
 *
 * The flag is one key for all tools, so a couple who gave their details on the
 * mahar page is not asked again on the next tool. It lives in localStorage and
 * nowhere else: it is a convenience for this browser, not an entitlement, and
 * losing it (private window, cleared storage) only means seeing the gate again.
 */

export const UNLOCK_KEY = '7m_tools_unlocked';

/** The tools with a gate; mirrors `WeddingTool` in the API's schemas. */
export type WeddingTool = 'mahar' | 'hashtag';

/**
 * A WhatsApp number in E.164-ish form, or null when it cannot be one.
 *
 * Indonesians write the same number as 0812..., 62812..., +62 812... or just
 * 812...; the team's WhatsApp alert links to wa.me, which needs the country
 * code, so every spelling becomes +62.... A number already written with a
 * foreign "+" prefix is kept as given. The API accepts 8-20 characters; the
 * nine-digit floor here is stricter on purpose, since no real mobile number is
 * shorter, so a typo like "0812" is caught before it becomes a lead nobody can
 * call.
 */
export function normalizeWhatsapp(raw: string): string | null {
  const trimmed = raw.trim();
  const international = trimmed.startsWith('+');
  let digits = trimmed.replace(/\D/g, '');
  if (!digits) return null;

  if (!international) {
    if (digits.startsWith('0')) digits = `62${digits.slice(1)}`;
    else if (digits.startsWith('8')) digits = `62${digits}`;
  }

  const normalized = `+${digits}`;
  return digits.length >= 9 && normalized.length <= 20 ? normalized : null;
}

export function isUnlocked(): boolean {
  try {
    const stored = localStorage.getItem(UNLOCK_KEY);
    if (!stored) return false;
    const parsed: unknown = JSON.parse(stored);
    return typeof parsed === 'object' && parsed !== null && 'unlockedAt' in parsed;
  } catch {
    return false;
  }
}

export function markUnlocked(now: Date = new Date()): void {
  try {
    localStorage.setItem(UNLOCK_KEY, JSON.stringify({ unlockedAt: now.toISOString() }));
  } catch {
    // Blocked storage only costs the visitor a second gate on the next visit.
  }
}
