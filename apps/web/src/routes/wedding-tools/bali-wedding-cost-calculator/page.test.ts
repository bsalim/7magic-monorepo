import { fireEvent, render, screen } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const replaceState = vi.fn();
vi.mock('$app/navigation', () => ({ replaceState: (...args: unknown[]) => replaceState(...args) }));
vi.mock('$app/state', () => ({
  page: {
    url: new URL('https://7magicwedding.com/en/wedding-tools/bali-wedding-cost-calculator'),
    data: {}
  }
}));
vi.mock('$env/dynamic/public', () => ({ env: {} }));
import Page from './+page.svelte';

const guestsField = () => screen.getByRole('spinbutton') as HTMLInputElement;

describe('Bali wedding cost calculator page', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    replaceState.mockReset();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  // A link copied after going 55 -> 60 -> 55 must open on 55, not 60.
  it('keeps the share link in step when an input returns to its first value', async () => {
    render(Page);
    await fireEvent.input(guestsField(), { target: { value: '60' } });
    await vi.advanceTimersByTimeAsync(1000);
    await fireEvent.input(guestsField(), { target: { value: '55' } });
    await vi.advanceTimersByTimeAsync(1000);
    expect(replaceState).toHaveBeenLastCalledWith(expect.stringContaining('guests=55'), {});
  });

  // Safari throws after ~100 history writes in 10 seconds; a dragged slider
  // must not write once per step.
  it('writes the URL once for a burst of slider steps', async () => {
    render(Page);
    for (let guests = 56; guests < 120; guests++) {
      await fireEvent.input(guestsField(), { target: { value: String(guests) } });
    }
    await vi.advanceTimersByTimeAsync(1000);
    expect(replaceState).toHaveBeenCalledTimes(1);
  });

  it('survives the browser refusing a history write', async () => {
    replaceState.mockImplementation(() => {
      throw new Error('SecurityError');
    });
    render(Page);
    await fireEvent.input(guestsField(), { target: { value: '70' } });
    await expect(vi.advanceTimersByTimeAsync(1000)).resolves.not.toThrow();
  });

  it('offers WhatsApp in the result, before the method section', () => {
    render(Page);
    const whatsapp = screen.getAllByRole('link', { name: /WhatsApp/ })[0];
    const method = screen.getByRole('heading', { name: 'How we estimate' });
    expect(
      whatsapp.compareDocumentPosition(method) & Node.DOCUMENT_POSITION_FOLLOWING
    ).toBeTruthy();
  });

  it('pulls the guest field down to the elopement maximum', async () => {
    render(Page);
    await fireEvent.input(guestsField(), { target: { value: '80' } });
    await fireEvent.click(screen.getByRole('radio', { name: /Elopement/ }));
    expect(guestsField().value).toBe('10');
  });

  it('counts whole guests', async () => {
    render(Page);
    await fireEvent.input(guestsField(), { target: { value: '5.5' } });
    expect(screen.queryByText(/5\.5 guests/)).toBeNull();
  });

  it('does not claim Bali is cheaper per guest', () => {
    const { container } = render(Page);
    expect(container.textContent).not.toMatch(/16,980|Usually per guest/);
  });
});
