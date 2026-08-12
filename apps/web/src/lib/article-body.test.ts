/**
 * Article bodies are the one place `localizeHref` cannot be enforced by reading
 * the source: the links live in the database. These cases are the shapes the
 * editor actually produces, taken from the live article bodies.
 */

import { describe, expect, it } from 'vitest';
import { localizeArticleBody } from '$lib/article-body';
import { overwriteGetLocale } from '$lib/paraglide/runtime';

function asEnglish<T>(run: () => T): T {
  overwriteGetLocale(() => 'en');
  try {
    return run();
  } finally {
    overwriteGetLocale(() => 'id');
  }
}

describe('localizeArticleBody', () => {
  it('localizes an absolute link to our own site', () => {
    const html = '<p>See <a href="https://7magicwedding.com/artikel/tradisi-wedding/sangjit">this</a></p>';
    expect(asEnglish(() => localizeArticleBody(html))).toContain(
      'href="/en/articles/tradisi-wedding/sangjit"'
    );
  });

  it('localizes the www form editors also paste', () => {
    const html = '<a href="https://www.7magicwedding.com/about">about</a>';
    expect(asEnglish(() => localizeArticleBody(html))).toContain('href="/en/about"');
  });

  it('localizes a root-relative link', () => {
    const html = '<a href="/wedding-venue/search?city=bali">venues</a>';
    expect(asEnglish(() => localizeArticleBody(html))).toContain(
      'href="/en/wedding-venue/search?city=bali"'
    );
  });

  it('leaves external links, anchors and mailto alone', () => {
    const html =
      '<a href="https://instagram.com/7magicwedding">ig</a><a href="#top">top</a><a href="mailto:x@y.z">mail</a>';
    expect(asEnglish(() => localizeArticleBody(html))).toBe(html);
  });

  it('leaves image sources alone, including ones on the old domain', () => {
    // These still have to resolve against the legacy host; localizing an src
    // would point it at a route that serves HTML.
    const html = '<img src="https://7magicwedding.com/articles/raffles-hotel.webp" alt="" />';
    expect(asEnglish(() => localizeArticleBody(html))).toBe(html);
  });

  it('is a no-op in the base locale', () => {
    const html = '<a href="https://7magicwedding.com/artikel/x/y">x</a>';
    expect(localizeArticleBody(html)).toContain('href="/artikel/x/y"');
  });

  it('tolerates an empty body', () => {
    expect(localizeArticleBody('')).toBe('');
  });
});
