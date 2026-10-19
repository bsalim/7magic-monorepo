import { isRedirect } from '@sveltejs/kit';
import { afterEach, describe, expect, it } from 'vitest';
import { overwriteGetLocale } from '$lib/paraglide/runtime';
import { load } from './+page.server';

const run = (path: string) => () => load({ url: new URL(`https://7magicwedding.com${path}`) } as never);

function redirectOf(fn: () => unknown) {
  try {
    fn();
  } catch (error) {
    if (isRedirect(error)) return { status: error.status, location: error.location };
    throw error;
  }
  return null;
}

describe('paket-sangjit load', () => {
  afterEach(() => overwriteGetLocale(() => 'id'));

  // /en/paket-sangjit was the English URL in the sitemap until the page got an
  // English slug; whatever Google indexed there has to follow it.
  it('moves the old English URL to the English slug, keeping the query', () => {
    overwriteGetLocale(() => 'en');
    expect(redirectOf(run('/en/paket-sangjit?utm_source=ig'))).toEqual({
      status: 301,
      location: '/en/sangjit-package?utm_source=ig'
    });
  });

  it('serves both canonical URLs without a redirect', () => {
    overwriteGetLocale(() => 'en');
    expect(redirectOf(run('/en/sangjit-package'))).toBeNull();
    overwriteGetLocale(() => 'id');
    expect(redirectOf(run('/paket-sangjit'))).toBeNull();
  });
});
