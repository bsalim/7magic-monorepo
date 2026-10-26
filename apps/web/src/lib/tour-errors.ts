import * as m from '$lib/paraglide/messages';

// Codes the API rejects a booking with because of what the guest typed or chose.
// They are form validation, so the action answers 422 and the page puts the text
// beside the field instead of in a banner above the whole form.
const FIELD_CODES = new Set(['already_registered', 'event_full', 'validation_error']);

/**
 * The status the form action answers with. The old rule sent everything that was
 * not a 422 out as a 409, which dressed an API outage up as a conflict.
 */
export function tourFailureStatus(apiStatus: number, code: string): number {
  if (FIELD_CODES.has(code)) return 422;
  if (apiStatus >= 500) return 502;
  return 409;
}

export type TourFormErrors = { email: string; guests: string; general: string };

/** Splits one failed action result into the text for each place it is shown. */
export function tourFormErrors(form: { ok?: boolean; code?: string } | null | undefined): TourFormErrors {
  const none: TourFormErrors = { email: '', guests: '', general: '' };
  if (!form || form.ok !== false) return none;
  switch (form.code) {
    case 'already_registered':
      return { ...none, email: m.tour_error_already() };
    case 'event_full':
      return { ...none, guests: m.tour_error_full() };
    default:
      return { ...none, general: m.tour_error_generic() };
  }
}
