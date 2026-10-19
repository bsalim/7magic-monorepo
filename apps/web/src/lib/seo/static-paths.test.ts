import { describe, expect, it } from 'vitest';
import { STATIC_PATHS } from './static-paths';

describe('STATIC_PATHS', () => {
  // Tools are added one route at a time, and a tool missing from this list is
  // missing from sitemap.xml, the footer and llms.txt all at once, silently.
  it('lists every wedding tool page', () => {
    const tools = Object.keys(import.meta.glob('/src/routes/wedding-tools/**/+page.svelte')).map((file) =>
      file.replace('/src/routes', '').replace(/\/\+page\.svelte$/, '')
    );
    expect(tools.length).toBeGreaterThan(1);
    expect(tools.filter((path) => !STATIC_PATHS.includes(path))).toEqual([]);
  });
});
