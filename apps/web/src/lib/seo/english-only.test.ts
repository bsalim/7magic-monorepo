import { isRedirect } from '@sveltejs/kit';
import { describe, expect, it } from 'vitest';
import {
  ENGLISH_ONLY_PATHS,
  englishOnlyLoad,
  siteHref,
  staticPathAlternates
} from './english-only';

function loadAt(pathname: string) {
  return englishOnlyLoad('/bali-wedding-planning')({
    url: new URL(`https://x${pathname}`)
  });
}

describe('englishOnlyLoad', () => {
  // A shared calculator link carries its inputs in the query string, so the
  // redirect from the root form must keep them or the result is lost.
  it('sends the root form to /en with its query string', () => {
    try {
      loadAt('/bali-wedding-planning?guests=20');
      expect.unreachable('expected a redirect');
    } catch (error) {
      expect(isRedirect(error)).toBe(true);
      if (!isRedirect(error)) return;
      expect(error.status).toBe(301);
      expect(error.location).toBe('/en/bali-wedding-planning?guests=20');
    }
  });

  it('announces only the English edition on the /en page', () => {
    expect(loadAt('/en/bali-wedding-planning')).toEqual({
      alternates: { en: '/en/bali-wedding-planning' }
    });
  });
});

describe('siteHref', () => {
  it('links an English-only page at its /en URL from any locale', () => {
    expect(siteHref('/bali-wedding-planning')).toBe('/en/bali-wedding-planning');
  });

  it('leaves a bilingual page to the active locale', () => {
    expect(siteHref('/paket-sangjit')).toBe('/paket-sangjit');
  });
});

describe('ENGLISH_ONLY_PATHS', () => {
  // The list is only half the fix: a path on it whose route never redirects is
  // still served at the root, labelled as Indonesian.
  it('has a route load that uses englishOnlyLoad for every path', () => {
    const servers = import.meta.glob('/src/routes/**/+page.server.ts', {
      query: '?raw',
      import: 'default',
      eager: true
    }) as Record<string, string>;
    const missing = ENGLISH_ONLY_PATHS.filter((path) => {
      const source = servers[`/src/routes${path}/+page.server.ts`];
      return !source?.includes(`englishOnlyLoad('${path}')`);
    });
    expect(missing).toEqual([]);
  });
});

describe('staticPathAlternates', () => {
  it('gives an English-only page a single en alternate', () => {
    expect(staticPathAlternates('/bali-wedding-planning')).toEqual({
      en: '/en/bali-wedding-planning'
    });
  });

  it('gives a bilingual page both locales', () => {
    expect(staticPathAlternates('/about')).toEqual({
      id: '/about',
      en: '/en/about'
    });
  });
});
