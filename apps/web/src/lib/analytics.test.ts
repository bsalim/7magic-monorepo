import { afterEach, describe, expect, it, vi } from 'vitest';

import { trackEvent } from './analytics';

describe('trackEvent', () => {
  afterEach(() => {
    delete window.gtag;
  });

  it('stays silent when the gtag script never loaded', () => {
    // The common case off production, and for anyone running a blocker.
    expect(() => trackEvent('Venue Viewed', { venue: 'Dome of The Harvest' })).not.toThrow();
  });

  it('forwards the event name with its properties as the event params', () => {
    const gtag = vi.fn();
    window.gtag = gtag;

    trackEvent('Venue Viewed', { venue: 'Dome of The Harvest', city: 'Tangerang', stars: 5 });

    expect(gtag).toHaveBeenCalledWith('event', 'Venue Viewed', {
      venue: 'Dome of The Harvest',
      city: 'Tangerang',
      stars: 5
    });
  });

  it('sends undefined params when there are no properties', () => {
    const gtag = vi.fn();
    window.gtag = gtag;

    trackEvent('Venue Quote Requested');

    expect(gtag).toHaveBeenCalledWith('event', 'Venue Quote Requested', undefined);
  });
});
