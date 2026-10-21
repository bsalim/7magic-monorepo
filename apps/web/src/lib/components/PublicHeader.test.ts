import { render, screen, within } from '@testing-library/svelte';
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

/** A menu's trigger and panel share one wrapper. */
const panelOf = (label: string) =>
  screen.getByRole('button', { name: new RegExp(label) }).parentElement!;

const navLinks = () =>
  screen.getAllByRole('link').filter((a) => {
    const href = a.getAttribute('href');
    return (
      href === '/wedding-venue/search' ||
      href === '/artikel' ||
      href === '/our-vendors' ||
      href === '/about' ||
      href === '/tour'
    );
  });

describe('PublicHeader', () => {
  it('renders the primary nav destinations', () => {
    render(PublicHeader);
    const hrefs = navLinks().map((a) => a.getAttribute('href'));
    expect(hrefs).toContain('/wedding-venue/search');
    expect(hrefs).toContain('/artikel');
    expect(hrefs).toContain('/our-vendors');
  });

  // The row is Wedding Venue, Paket & Layanan, Vendor, Inspirasi, Events:
  // Vendor stays a plain link beside the menus, as the marketplace's other
  // catalogue.
  it('orders the top-level items with Vendor as the one plain link', () => {
    render(PublicHeader);
    const row = screen.getAllByRole('navigation', { name: 'Navigasi utama' })[0];
    const items = [...row.children].map((el) =>
      el.matches('a') ? `link:${el.textContent!.trim()}` : el.querySelector('button')!.textContent!.trim()
    );
    expect(items).toEqual(['Wedding Venue', 'Paket & Layanan', 'link:Vendor', 'Inspirasi', 'Events']);
  });

  // One column per region the business operates in. The Singapore, Jabodetabek
  // and Bali landing pages moved in here from the top level, and Batam -- which
  // had no nav entry at all -- now has a column of its own.
  it('groups the venue menu by region, each with its city hubs', () => {
    render(PublicHeader);
    const panel = panelOf('Wedding Venue');
    const columns = [...panel.querySelectorAll('ul')].map((ul) => ({
      region: ul.previousElementSibling!.textContent!.trim(),
      hrefs: [...ul.querySelectorAll('a')].map((a) => a.getAttribute('href'))
    }));

    expect(columns).toEqual([
      {
        region: 'Jabodetabek',
        hrefs: [
          '/jabodetabek-wedding',
          '/wedding-venue/jakarta',
          '/wedding-venue/tangerang',
          '/wedding-venue/bogor',
          '/wedding-venue/bekasi'
        ]
      },
      {
        region: 'Bali',
        hrefs: [
          '/en/bali-wedding-planning',
          '/en/bali-wedding-cost',
          '/en/legally-married-in-bali',
          '/en/bali-wedding-concierge',
          '/wedding-venue/bali'
        ]
      },
      { region: 'Batam', hrefs: ['/wedding-venue/batam'] },
      { region: 'Singapura', hrefs: ['/en/wedding-planning-singapore', '/wedding-venue/singapore'] }
    ]);
    expect(within(panel).getByText('Venue Bali')).toBeInTheDocument();
    expect(within(panel).getByRole('link', { name: /Lihat Semua Venue/ })).toHaveAttribute(
      'href',
      '/wedding-venue/search'
    );
  });

  // Tentang lives in the footer's company column; the top nav is kept for the
  // pages that sell something.
  it('leaves the about page out of the header', () => {
    render(PublicHeader);
    expect(navLinks().map((a) => a.getAttribute('href'))).not.toContain('/about');
  });

  // Event organizer pages are grouped per city under Events, apart from the
  // wedding packages, so a new city slots in without crowding the top level.
  it('groups packages, inspiration and events into their own menus', () => {
    render(PublicHeader);
    const hrefsIn = (el: HTMLElement) =>
      [...el.querySelectorAll('a')].map((a) => a.getAttribute('href'));

    expect(hrefsIn(panelOf('Paket & Layanan'))).toEqual(['/paket-sangjit', '/perjanjian-pranikah']);
    expect(hrefsIn(panelOf('Inspirasi'))).toEqual([
      '/wedding-showcases',
      '/artikel',
      '/wedding-tools'
    ]);
    expect(hrefsIn(panelOf('Events'))).toEqual(['/bali-event-organizer']);
  });

  it('marks the venue menu active on a city hub it does not list', () => {
    render(PublicHeader, { props: { pathname: '/wedding-venue/surabaya' } });
    expect(screen.getByRole('button', { name: /Wedding Venue/ })).toHaveClass('border-brand-gold');
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

  // The label is deliberately untranslated: the brand uses the English phrase in
  // both locales, so this asserts the words, not just the destination.
  it('offers the free venue tour under its English label', () => {
    render(PublicHeader);
    const hrefs = navLinks().map((a) => a.getAttribute('href'));
    expect(hrefs).toContain('/tour');
    expect(screen.getAllByText('Free Venue Tour').length).toBeGreaterThan(0);
  });

  it('marks nothing active when the path matches no section', () => {
    render(PublicHeader, { props: { pathname: '/nowhere' } });
    const active = screen.getAllByRole('link').filter((a) => a.getAttribute('aria-current') === 'page');
    expect(active).toHaveLength(0);
  });
});
