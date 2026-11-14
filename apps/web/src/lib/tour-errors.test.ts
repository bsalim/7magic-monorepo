import { describe, expect, it, vi } from 'vitest';

vi.mock('$lib/paraglide/messages', () => ({
  tour_error_already: () => 'already',
  captcha_error: () => 'captcha',
  tour_error_full: () => 'full',
  tour_error_generic: () => 'generic'
}));

import { tourFailureStatus, tourFormErrors } from './tour-errors';

describe('tourFailureStatus', () => {
  it('answers 422 for errors the guest can fix', () => {
    expect(tourFailureStatus(409, 'already_registered')).toBe(422);
    expect(tourFailureStatus(409, 'event_full')).toBe(422);
    expect(tourFailureStatus(422, 'validation_error')).toBe(422);
  });

  it('keeps 409 for a closed event and 502 for an API failure', () => {
    expect(tourFailureStatus(409, 'no_open_event')).toBe(409);
    expect(tourFailureStatus(500, 'generic')).toBe(502);
  });
});

describe('tourFormErrors', () => {
  it('puts a duplicate email beside the email field', () => {
    expect(tourFormErrors({ ok: false, code: 'already_registered' })).toEqual({
      email: 'already',
      guests: '',
      general: ''
    });
  });

  it('puts a full event beside the guest count', () => {
    expect(tourFormErrors({ ok: false, code: 'event_full' }).guests).toBe('full');
  });

  it('shows a failed captcha above the form and answers 422', () => {
    expect(tourFormErrors({ ok: false, code: 'captcha_failed' }).general).toBe('captcha');
    expect(tourFailureStatus(400, 'captcha_failed')).toBe(422);
  });

  it('falls back to a general message and stays empty on success', () => {
    expect(tourFormErrors({ ok: false, code: 'no_open_event' }).general).toBe('generic');
    expect(tourFormErrors({ ok: true, code: '' })).toEqual({ email: '', guests: '', general: '' });
    expect(tourFormErrors(null)).toEqual({ email: '', guests: '', general: '' });
  });
});
