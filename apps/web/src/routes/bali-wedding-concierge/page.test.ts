import { fireEvent, render, screen, within } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';
import { CONCIERGE_SERVICES } from '$lib/bali-concierge';

// The footer's partner strip reads the media host from SvelteKit's runtime env.
vi.mock('$env/dynamic/public', () => ({ env: {} }));
import Page from './+page.svelte';

describe('Bali wedding concierge page', () => {
  it('offers exactly the confirmed services, one card each', () => {
    render(Page);
    const list = screen.getByRole('group', { name: /Choose what you'd like help with/ });
    expect(within(list).getAllByRole('checkbox')).toHaveLength(CONCIERGE_SERVICES.length);
  });

  it('puts the chosen services in the WhatsApp message', async () => {
    render(Page);
    await fireEvent.click(screen.getByRole('checkbox', { name: /Private car & driver/ }));
    await fireEvent.click(screen.getByRole('checkbox', { name: /Balinese massage & spa/ }));
    const href = screen.getAllByRole('link', { name: /WhatsApp/ })[0].getAttribute('href') ?? '';
    const text = decodeURIComponent(href);
    expect(text).toContain('Private car & driver');
    expect(text).toContain('Balinese massage & spa');
  });

  // Scoped to the services: the site header carries the prenup price.
  it('prices none of the services', () => {
    render(Page);
    const list = screen.getByRole('group', { name: /Choose what you'd like help with/ });
    expect(within(list).queryByText(/A\$\d|US\$\d|Rp\s?\d/)).toBeNull();
  });
});
