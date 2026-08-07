import { render, screen } from '@testing-library/svelte';
import { afterEach, describe, expect, it } from 'vitest';
import { tick } from 'svelte';
import PublicHeader from './PublicHeader.svelte';

const scrollTo = async (y: number) => {
  Object.defineProperty(window, 'scrollY', { value: y, configurable: true, writable: true });
  window.dispatchEvent(new Event('scroll'));
  await tick();
};

const brandRow = () => screen.getAllByAltText('7Magic Wedding')[0].closest('a')!.parentElement!;

afterEach(() => scrollTo(0));

const navLinks = () =>
  screen.getAllByRole('link').filter((a) => {
    const href = a.getAttribute('href');
    return href === '/wedding-venue/search' || href === '/artikel' || href === '/our-vendors' || href === '/about';
  });

describe('PublicHeader', () => {
  it('renders the primary nav destinations', () => {
    render(PublicHeader);
    const hrefs = navLinks().map((a) => a.getAttribute('href'));
    expect(hrefs).toContain('/wedding-venue/search');
    expect(hrefs).toContain('/artikel');
    expect(hrefs).toContain('/our-vendors');
    expect(hrefs).toContain('/about');
  });

  it('marks the matching nav item as the current page', () => {
    render(PublicHeader, { props: { pathname: '/artikel' } });
    const active = screen.getAllByRole('link').filter((a) => a.getAttribute('aria-current') === 'page');
    expect(active).toHaveLength(1);
    expect(active[0]).toHaveAttribute('href', '/artikel');
  });

  it('treats a nested path as active for its section', () => {
    render(PublicHeader, { props: { pathname: '/wedding-venue/search/jakarta' } });
    const active = screen.getAllByRole('link').filter((a) => a.getAttribute('aria-current') === 'page');
    expect(active).toHaveLength(1);
    expect(active[0]).toHaveAttribute('href', '/wedding-venue/search');
  });

  // The header is sticky and in normal flow, so anything that changes its
  // height reflows the page below it. The browser then compensates the scroll
  // offset, which pushes scrollY back across the collapse threshold and makes
  // the header oscillate. Collapsing must therefore stay layout-neutral: the
  // brand row keeps its box and the header is pinned above the viewport instead.
  it('keeps the brand row in the layout once scrolled', async () => {
    render(PublicHeader, { props: { pathname: '/' } });
    const row = brandRow();
    expect(row.className).not.toContain('hidden');

    await scrollTo(400);

    expect(row.isConnected).toBe(true);
    expect(row.className).not.toContain('hidden');
  });

  it('swaps the compact logo and CTA into the nav bar once scrolled', async () => {
    render(PublicHeader, { props: { pathname: '/' } });
    expect(screen.getAllByAltText('7Magic Wedding')).toHaveLength(1);

    await scrollTo(400);

    expect(screen.getAllByAltText('7Magic Wedding')).toHaveLength(2);
  });

  it('marks nothing active when the path matches no section', () => {
    render(PublicHeader, { props: { pathname: '/nowhere' } });
    const active = screen.getAllByRole('link').filter((a) => a.getAttribute('aria-current') === 'page');
    expect(active).toHaveLength(0);
  });
});
