import { render, screen } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';
import { estimateCost } from '$lib/tools/bali-cost';
import { formatAudRange } from '$lib/tools/bali-format';

// The footer's partner strip reads the media host from SvelteKit's runtime env,
// which only exists inside a running server.
vi.mock('$env/dynamic/public', () => ({ env: {} }));
import Page from './+page.svelte';

describe('Bali wedding cost guide', () => {
  // The guide's figures are generated from the same model as the calculator,
  // so the two can never quote different numbers.
  it('shows the 50-guest classic villa total exactly as the model computes it', () => {
    render(Page);
    const total = estimateCost({
      guests: 50,
      setting: 'villa',
      style: 'classic',
      year: 2027,
      month: 7,
      addOns: []
    }).total;
    expect(screen.getAllByText(formatAudRange(total), { exact: false }).length).toBeGreaterThan(0);
  });

  it('says the figures are market ranges, not a quote', () => {
    render(Page);
    expect(screen.getAllByText(/Typical market range, not a 7Magic quote/).length).toBeGreaterThan(
      0
    );
  });

  // The 2025 Bali-resort average contradicted the model's own ranges on the
  // same page; totals are compared on the 2026 survey's figures instead.
  it('does not claim Bali is cheaper per guest', () => {
    const { container } = render(Page);
    expect(container.textContent).not.toMatch(/16,980|cheaper per guest|Per guest, usually/);
  });
});
