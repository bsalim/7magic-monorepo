import { describe, expect, it } from 'vitest';
import { CONCIERGE_GROUPS, CONCIERGE_SERVICES } from './bali-concierge';

// The services 7Magic's Bali team confirmed it can deliver, ticked by the user
// on 2026-10-21. A service on the page that the team cannot deliver is a
// promise a couple would hold us to, so the list is pinned exactly.
const TICKED = [
  'legal',
  'transfers',
  'accommodation',
  'arrival',
  'activities',
  'welcome',
  'blessing',
  'hens',
  'prewedding',
  'renewal',
  'car',
  'massage',
  'chef',
  'reservations',
  'nanny',
  'wellness',
  'doctor',
  'holiday-photographer'
];

describe('CONCIERGE_SERVICES', () => {
  it('offers exactly the services the Bali team confirmed', () => {
    const keys = CONCIERGE_SERVICES.map((service) => service.key);
    expect([...keys].sort()).toEqual([...TICKED].sort());
    expect(new Set(keys).size).toBe(keys.length);
  });

  it('leaves out every service that was not ticked', () => {
    const keys: string[] = CONCIERGE_SERVICES.map((service) => service.key);
    for (const unticked of [
      'beauty',
      'proposal',
      'honeymoon',
      'video-tour',
      'guest-site',
      'aud-invoice',
      'date-check'
    ]) {
      expect(keys).not.toContain(unticked);
    }
  });

  it('files every service under a known group', () => {
    const groups = CONCIERGE_GROUPS.map((group) => group.key);
    expect(CONCIERGE_SERVICES.filter((service) => !groups.includes(service.group))).toEqual([]);
  });
});
