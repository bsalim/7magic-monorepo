import { fireEvent, render, screen } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';

vi.mock('$env/dynamic/public', () => ({ env: {} }));
import Page from './+page.svelte';

const pickDay = async (value: string) =>
  fireEvent.input(screen.getByLabelText(/A date you have in mind/), { target: { value } });

describe('Bali wedding date planner page', () => {
  // 2028's Indonesian holidays are not published, so a 2028 day with nothing
  // in the data is unknown, not clear.
  it('does not call a 2028 day clear', async () => {
    render(Page);
    await pickDay('2028-06-15');
    expect(screen.queryByText(/No Balinese holy day/)).toBeNull();
    expect(screen.getAllByText(/not (yet )?announced/).length).toBeGreaterThan(0);
  });

  it('calls a 2027 day with nothing on it clear', async () => {
    render(Page);
    await pickDay('2027-06-15');
    expect(screen.getByText(/No Balinese holy day/)).toBeInTheDocument();
  });

  it('warns that Nyepi closes the airport', async () => {
    render(Page);
    await pickDay('2027-03-08');
    expect(screen.getByText(/airport is closed/)).toBeInTheDocument();
  });
});
