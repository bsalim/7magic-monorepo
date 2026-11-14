import { describe, expect, it, vi } from 'vitest';

vi.mock('$env/dynamic/public', () => ({ env: {} }));

import { forwardVenueInquiry, submitVenueInquiry, type VenueInquiry } from './venue-inquiry';

const API = 'http://api.test';

const base: VenueInquiry = {
  venue: { id: 7, slug: 'hotel-mulia', name: 'Hotel Mulia', city: 'jakarta' },
  name: 'Rina',
  whatsapp: '+62 812 0000 0000',
  email: '',
  weddingDate: '2027-03-14',
  bestTimeToReach: 'morning',
  tour: null,
  locale: 'id'
};

const reply = (status: number, body: unknown = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' }
  });

const bodyOf = (fetcher: ReturnType<typeof vi.fn>, call: number) =>
  JSON.parse(fetcher.mock.calls[call][1].body as string);

describe('forwardVenueInquiry', () => {
  it('sends only the pricing request when no tour was asked for', async () => {
    const fetcher = vi.fn().mockResolvedValue(reply(201));

    const result = await forwardVenueInquiry(base, fetcher, API);

    expect(result).toEqual({ pricing: 'ok', tour: 'skipped' });
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher.mock.calls[0][0]).toBe(`${API}/api/v1/public/venue-pricing-requests`);
    expect(bodyOf(fetcher, 0)).toEqual({
      name: 'Rina',
      whatsapp: '+62 812 0000 0000',
      email: null,
      wedding_date: '2027-03-14',
      best_time_to_reach: 'morning',
      venue_id: 7,
      venue_slug: 'hotel-mulia',
      venue_name: 'Hotel Mulia'
    });
  });

  it('books the tour for the same venue after the pricing request lands', async () => {
    const fetcher = vi.fn().mockResolvedValue(reply(201));

    const result = await forwardVenueInquiry(
      {
        ...base,
        email: 'rina@example.com',
        tour: { visitDate: '2026-11-02', partySize: 3 }
      },
      fetcher,
      API
    );

    expect(result).toEqual({ pricing: 'ok', tour: 'ok' });
    expect(fetcher.mock.calls[1][0]).toBe(`${API}/api/v1/public/tour/register`);
    expect(bodyOf(fetcher, 1)).toEqual({
      name: 'Rina',
      email: 'rina@example.com',
      mobile: '+62 812 0000 0000',
      venue_id: 7,
      venue_name: 'Hotel Mulia',
      city: 'jakarta',
      visit_date: '2026-11-02',
      party_size: 3,
      locale: 'id'
    });
  });

  it('clamps the party size to what the API accepts', async () => {
    const fetcher = vi.fn().mockResolvedValue(reply(201));

    await forwardVenueInquiry(
      {
        ...base,
        email: 'rina@example.com',
        tour: { visitDate: '2026-11-02', partySize: 99 }
      },
      fetcher,
      API
    );

    expect(bodyOf(fetcher, 1).party_size).toBe(20);
  });

  it('does not book a tour when the pricing request failed', async () => {
    const fetcher = vi.fn().mockResolvedValue(reply(500));

    const result = await forwardVenueInquiry(
      {
        ...base,
        email: 'rina@example.com',
        tour: { visitDate: '2026-11-02', partySize: 2 }
      },
      fetcher,
      API
    );

    expect(result).toEqual({ pricing: 'failed', tour: 'skipped' });
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it('treats a network error on pricing as a failure', async () => {
    const fetcher = vi.fn().mockRejectedValue(new TypeError('offline'));

    expect(await forwardVenueInquiry(base, fetcher, API)).toEqual({
      pricing: 'failed',
      tour: 'skipped'
    });
  });

  it('reports the API error code when only the tour fails', async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(reply(201))
      .mockResolvedValueOnce(reply(409, { error: { code: 'no_open_event' } }));

    const result = await forwardVenueInquiry(
      {
        ...base,
        email: 'rina@example.com',
        tour: { visitDate: '2026-11-02', partySize: 2 }
      },
      fetcher,
      API
    );

    expect(result).toEqual({ pricing: 'ok', tour: 'no_open_event' });
  });

  it('falls back to a generic code when the tour failure carries none', async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(reply(201))
      .mockRejectedValueOnce(new TypeError('offline'));

    const result = await forwardVenueInquiry(
      {
        ...base,
        email: 'rina@example.com',
        tour: { visitDate: '2026-11-02', partySize: 2 }
      },
      fetcher,
      API
    );

    expect(result).toEqual({ pricing: 'ok', tour: 'generic' });
  });
});

describe('submitVenueInquiry', () => {
  it('sends the whole inquiry in one request, with the captcha token', async () => {
    const fetcher = vi.fn().mockResolvedValue(reply(200, { pricing: 'ok', tour: 'skipped' }));

    const result = await submitVenueInquiry(base, fetcher, 'tok');

    expect(result).toEqual({ pricing: 'ok', tour: 'skipped' });
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher.mock.calls[0][0]).toBe('/api/venue-inquiry');
    expect(fetcher.mock.calls[0][1].headers['x-turnstile-token']).toBe('tok');
    expect(bodyOf(fetcher, 0)).toEqual(base);
  });

  it('reports a rejected or unreachable server as a failed pricing request', async () => {
    const rejected = vi.fn().mockResolvedValue(reply(403, { error: { code: 'captcha_failed' } }));
    const offline = vi.fn().mockRejectedValue(new TypeError('offline'));

    expect(await submitVenueInquiry(base, rejected)).toEqual({
      pricing: 'failed',
      tour: 'skipped'
    });
    expect(await submitVenueInquiry(base, offline)).toEqual({
      pricing: 'failed',
      tour: 'skipped'
    });
  });
});
