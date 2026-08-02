import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import PhotoMosaic from './PhotoMosaic.svelte';
import { m } from '$lib/paraglide/messages.js';
import type { DisplayPhoto } from './photos';

const photo = (n: number): DisplayPhoto => ({
  src: `/p${n}.jpg`,
  thumb: `/t${n}.jpg`,
  label: `Photo ${n}`,
  real: true
});

const make = (n: number) => Array.from({ length: n }, (_, i) => photo(i + 1));

describe('PhotoMosaic', () => {
  it('renders five tiles when five or more photos exist', () => {
    render(PhotoMosaic, { props: { photos: make(10), venueName: 'JW Marriott' } });
    expect(screen.getAllByRole('img')).toHaveLength(5);
  });

  it('collapses to the photos available when there are fewer than five', () => {
    render(PhotoMosaic, { props: { photos: make(2), venueName: 'JW Marriott' } });
    expect(screen.getAllByRole('img')).toHaveLength(2);
  });

  // Asserted through the message rather than a literal, so the test does not
  // break when the base locale changes or the copy is retranslated.
  it('shows the total count on the last tile when photos are hidden', () => {
    render(PhotoMosaic, { props: { photos: make(10), venueName: 'JW Marriott' } });
    expect(screen.getByText(m.vd_see_all_photos({ count: 10 }))).toBeInTheDocument();
  });

  it('omits the see-all control when everything is already visible', () => {
    render(PhotoMosaic, { props: { photos: make(4), venueName: 'JW Marriott' } });
    expect(screen.queryByText(m.vd_see_all_photos({ count: 4 }))).toBeNull();
  });

  it('renders no images when there are no photos', () => {
    const { container } = render(PhotoMosaic, { props: { photos: [], venueName: 'JW Marriott' } });
    expect(container.querySelector('img')).toBeNull();
  });

  it('skips placeholder entries that have no source', () => {
    const photos: DisplayPhoto[] = [
      photo(1),
      { src: '', thumb: '', label: 'Grand Ballroom', real: false }
    ];
    render(PhotoMosaic, { props: { photos, venueName: 'JW Marriott' } });
    expect(screen.getAllByRole('img')).toHaveLength(1);
  });

  it('names each image after the venue and the photo label', () => {
    render(PhotoMosaic, { props: { photos: make(1), venueName: 'JW Marriott' } });
    expect(screen.getByAltText('JW Marriott — Photo 1')).toBeInTheDocument();
  });
});
