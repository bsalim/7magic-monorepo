import { describe, expect, it } from 'vitest';
import { authorNameForSlug, authorPath } from './authors';

describe('authors', () => {
  it('maps a known display name to its profile path and back', () => {
    expect(authorPath('Fiona')).toBe('/author/fiona');
    expect(authorNameForSlug('fiona')).toBe('Fiona');
  });

  it('has nothing for an author without a profile', () => {
    expect(authorPath('Someone Else')).toBeNull();
    expect(authorNameForSlug('someone-else')).toBeNull();
  });
});
