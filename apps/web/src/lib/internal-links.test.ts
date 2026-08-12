import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

import { describe, expect, it } from 'vitest';

/**
 * Guards the /en prefix.
 *
 * English lives under /en, but a plain `href="/contact"` is locale-blind: an
 * English visitor clicking it lands on the Indonesian page. That leak reached the
 * canonical and breadcrumb annotations too, so it was an indexing problem and not
 * only a navigation one. Every internal link therefore goes through
 * `localizeHref`, and this test fails if a new plain one appears.
 *
 * Assets are exempt -- /img, /favicons and /fonts are not localized routes.
 */
const ROOTS = ['src/routes', 'src/lib/components'];
const ASSET_PREFIXES = ['/img/', '/favicons/', '/fonts/'];

/** Vendored shadcn components; upstream code we do not edit. */
const IGNORED = ['/ui/'];

function svelteFiles(dir: string): string[] {
  const found: string[] = [];
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      found.push(...svelteFiles(path));
    } else if (path.endsWith('.svelte')) {
      found.push(path);
    }
  }
  return found;
}

describe('internal links', () => {
  it('never hardcodes a site path, so English navigation stays under /en', () => {
    const offenders: string[] = [];

    for (const root of ROOTS) {
      for (const file of svelteFiles(root)) {
        if (IGNORED.some((part) => file.includes(part))) continue;

        const source = readFileSync(file, 'utf8');

        // Literal paths: href="/contact"
        for (const match of source.matchAll(/href="(\/[^"]*)"/g)) {
          const href = match[1];
          if (ASSET_PREFIXES.some((prefix) => href.startsWith(prefix))) continue;
          offenders.push(`${file}: href="${href}"`);
        }

        // Built paths: href={`/wedding-showcases/${slug}`} and href={venue.path_url}.
        // These slipped past an earlier sweep that only looked for literals, and
        // they are the ones that matter most -- venue cards and pagination.
        for (const match of source.matchAll(/href=\{([^}]*(?:`\/|path_url)[^}]*)\}/g)) {
          const expression = match[1];
          if (expression.includes('localizeHref')) continue;
          offenders.push(`${file}: href={${expression}}`);
        }
      }
    }

    expect(offenders).toEqual([]);
  });
});
