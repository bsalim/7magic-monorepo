import { afterEach, describe, expect, it, vi } from 'vitest';

import { trackEvent } from './analytics';

describe('trackEvent', () => {
  afterEach(() => {
    delete window.plausible;
  });

  it('stays silent when the Plausible script never loaded', () => {
    // The common case off production, and for anyone running a blocker.
    expect(() => trackEvent('Venue Viewed', { venue: 'Dome of The Harvest' })).not.toThrow();
  });

  it('forwards the event name with its properties nested under props', () => {
    const plausible = vi.fn();
    window.plausible = plausible;

    trackEvent('Venue Viewed', { venue: 'Dome of The Harvest', city: 'Tangerang', stars: 5 });

    expect(plausible).toHaveBeenCalledWith('Venue Viewed', {
      props: { venue: 'Dome of The Harvest', city: 'Tangerang', stars: 5 }
    });
  });

  it('sends no options object when there are no properties', () => {
    const plausible = vi.fn();
    window.plausible = plausible;

    trackEvent('Venue Quote Requested');

    expect(plausible).toHaveBeenCalledWith('Venue Quote Requested', undefined);
  });
});
