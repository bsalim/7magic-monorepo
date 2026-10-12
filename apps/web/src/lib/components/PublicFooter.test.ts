import { render, screen, within } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';
import PublicFooter from './PublicFooter.svelte';

// The partner strip above the footer reads the media host from SvelteKit's
// runtime env, which only exists inside a running server.
vi.mock('$env/dynamic/public', () => ({ env: {} }));
import { STATIC_PATHS } from '$lib/seo/static-paths';

const footerHrefs = () =>
  within(screen.getByRole('contentinfo'))
    .getAllByRole('link')
    .map((a) => a.getAttribute('href'));

describe('PublicFooter', () => {
  // The footer is the readable site map. Before this test it had silently
  // fallen behind sitemap.xml -- showcases, both tour pages and every city hub
  // were missing -- so a page added to the sitemap must now be added here too.
  it('links every static page in the sitemap', () => {
    render(PublicFooter);
    const hrefs = footerHrefs();
    expect(STATIC_PATHS.filter((path) => !hrefs.includes(path))).toEqual([]);
  });

  // The canonical hub URLs, not the search page filtered by city: those are
  // the pages the sitemap lists and the ones meant to rank.
  it('links the city venue hubs, not filtered search results', () => {
    render(PublicFooter);
    const hrefs = footerHrefs();
    for (const city of ['jakarta', 'tangerang', 'bogor', 'bekasi', 'bali', 'batam', 'singapore']) {
      expect(hrefs).toContain(`/wedding-venue/${city}`);
    }
    expect(hrefs.some((href) => href?.includes('?city='))).toBe(false);
  });

  it('labels each link group as its own navigation landmark', () => {
    render(PublicFooter);
    const footer = screen.getByRole('contentinfo');
    const names = within(footer)
      .getAllByRole('navigation')
      .map((nav) => nav.getAttribute('aria-labelledby'))
      .map((id) => footer.querySelector(`#${id}`)!.textContent!.trim());
    expect(names).toEqual([
      'Wedding Venue',
      'Paket & Layanan',
      'Inspirasi',
      'Events',
      'Perusahaan',
      'Legal'
    ]);
  });
});
