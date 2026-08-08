/**
 * The switcher is the one place a visitor changes locale by hand, and its
 * failure mode is quiet: the structurally-localized article path resolves via a
 * 301, so a wrong link still lands on the right page and nothing looks broken
 * until you read the anchor.
 */

import { describe, expect, it } from 'vitest';
import { switcherHref } from './locale-href';

const ARTICLE_ID = '/artikel/pernikahan-islami/menikah-di-bulan-ramadan';
const ARTICLE_EN = '/en/articles/islamic-wedding/getting-married-during-ramadan';

describe('switcherHref', () => {
  it('uses the API alternate for an article, not the localized path', () => {
    const alternates = { id: ARTICLE_ID, en: ARTICLE_EN };
    expect(switcherHref(ARTICLE_ID, 'en', alternates)).toBe(ARTICLE_EN);
    expect(switcherHref(ARTICLE_EN, 'id', alternates)).toBe(ARTICLE_ID);
  });

  it('does not merely prefix /en onto the Indonesian segments', () => {
    const alternates = { id: ARTICLE_ID, en: ARTICLE_EN };
    // What the old switcher produced: valid structure, wrong words.
    expect(switcherHref(ARTICLE_ID, 'en', alternates)).not.toBe(
      '/en/articles/pernikahan-islami/menikah-di-bulan-ramadan'
    );
  });

  it('falls back to the localized path when the page has no alternates', () => {
    // Venues, showcases and static pages: the same URL in both locales, so the
    // structural localization is already correct.
    const venue = '/wedding-venue/jakarta/jw-marriott-hotel-jakarta';
    expect(switcherHref(venue, 'en', undefined)).toBe(`/en${venue}`);
    expect(switcherHref(`/en${venue}`, 'id', undefined)).toBe(venue);
  });

  it('falls back when alternates omit the target locale', () => {
    // An article with no English translation announces only Indonesian.
    expect(switcherHref(ARTICLE_ID, 'en', { id: ARTICLE_ID })).toBe(
      '/en/articles/pernikahan-islami/menikah-di-bulan-ramadan'
    );
  });
});
