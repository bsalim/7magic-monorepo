import { describe, expect, it } from 'vitest';
import { pageWindow, paginationHref } from './pagination';

const url = (search: string, pathname = '/wedding-venue/search') =>
  new URL(`https://7magicwedding.com${pathname}${search}`);

describe('paginationHref', () => {
  it('keeps the active filters when moving to another page', () => {
    const href = paginationHref(url('?city=jakarta&q=ballroom'), 3);
    const params = new URLSearchParams(href.slice(1));

    expect(params.get('city')).toBe('jakarta');
    expect(params.get('q')).toBe('ballroom');
    expect(params.get('page')).toBe('3');
  });

  it('keeps every repeated stars entry, not just the last', () => {
    const href = paginationHref(url('?stars=5&stars=3'), 2);

    expect(new URLSearchParams(href.slice(1)).getAll('stars')).toEqual(['5', '3']);
  });

  it('replaces the current page rather than appending a second one', () => {
    const href = paginationHref(url('?city=bali&page=2'), 4);

    expect(new URLSearchParams(href.slice(1)).getAll('page')).toEqual(['4']);
  });

  // Page 1 is the unparameterised URL, so paging back to it does not leave
  // ?page=1 as a second address serving identical results.
  it('drops the parameter entirely on page 1', () => {
    expect(paginationHref(url('?city=bali&page=2'), 1)).toBe('?city=bali');
  });

  it('falls back to the path when page 1 has no other filters', () => {
    expect(paginationHref(url('?page=2'), 1)).toBe('/wedding-venue/search');
  });

  // The English site lives under /en; a link that dropped the prefix would send
  // the visitor back to the Indonesian page mid-search.
  it('keeps the locale prefix on the bare page-1 link', () => {
    expect(paginationHref(url('?page=3', '/en/wedding-venue/search'), 1)).toBe(
      '/en/wedding-venue/search'
    );
  });
});

describe('pageWindow', () => {
  it('lists every page when the run is short', () => {
    expect(pageWindow(2, 5)).toEqual([1, 2, 3, 4, 5]);
  });

  it('condenses a long run around the current page', () => {
    expect(pageWindow(6, 12)).toEqual([1, 'gap', 5, 6, 7, 'gap', 12]);
  });

  it('does not open a gap that hides a single page', () => {
    expect(pageWindow(3, 8)).toEqual([1, 2, 3, 4, 'gap', 8]);
  });

  it('handles the first and last page without duplicating them', () => {
    expect(pageWindow(1, 10)).toEqual([1, 2, 'gap', 10]);
    expect(pageWindow(10, 10)).toEqual([1, 'gap', 9, 10]);
  });
});
