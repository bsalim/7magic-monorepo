import { render, screen, within } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import TestimonialCarousel from './TestimonialCarousel.svelte';
import type { Testimonial } from '$lib/api';

const photo = (name: string, alt: string) => ({
  alt,
  small_url: `https://media.7magicwedding.com/testimonials/${name}_sm_480w.jpg`,
  webp_srcset: `https://media.7magicwedding.com/testimonials/${name}_xs_320w.webp 320w`,
  jpeg_srcset: `https://media.7magicwedding.com/testimonials/${name}_xs_320w.jpg 320w`,
  width: 480,
  height: 480
});

const items: Testimonial[] = [
  { couple: 'Marcell & Jenny', message: 'Speechless, kerja WO-nya oke banget.', wedding_date: '2022-01-15', photo: photo('a', 'Marcell & Jenny') },
  { couple: 'Ardy & Selvi', message: 'Luar biasa.', wedding_date: '2023-11-04', photo: photo('b', 'Ardy & Selvi') }
];

describe('TestimonialCarousel', () => {
  it('shows every couple with their words, without the wedding date', () => {
    render(TestimonialCarousel, { items, labels: { previous: 'Sebelumnya', next: 'Berikutnya' } });
    const cards = screen.getAllByRole('listitem');
    expect(cards).toHaveLength(2);
    expect(within(cards[0]).getByText('Marcell & Jenny')).toBeTruthy();
    expect(within(cards[0]).getByText(/Speechless, kerja WO-nya oke banget\./)).toBeTruthy();
    expect(within(cards[0]).queryByText(/2022/)).toBeNull();
  });

  it('serves webp ahead of the jpeg fallback', () => {
    const { container } = render(TestimonialCarousel, { items, labels: { previous: 'Previous', next: 'Next' } });
    const sources = container.querySelectorAll('li:first-child picture source');
    expect([...sources].map((s) => s.getAttribute('type'))).toEqual(['image/webp', 'image/jpeg']);
    expect(container.querySelector('li:first-child img')?.getAttribute('alt')).toBe('Marcell & Jenny');
  });

  it('has labelled previous and next buttons', () => {
    render(TestimonialCarousel, { items, labels: { previous: 'Previous', next: 'Next' } });
    expect(screen.getByRole('button', { name: 'Previous' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Next' })).toBeTruthy();
  });
});
