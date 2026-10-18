import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import DateField from './DateField.svelte';

describe('DateField', () => {
  // The tour and venue forms were built around this label; the locale prop
  // must not change it for them.
  it('keeps the short English label when no locale is given', () => {
    render(DateField, { id: 'd', value: '2026-09-20' });
    expect(screen.getByRole('button').textContent?.trim()).toBe('20 Sep 2026');
  });

  it('names the weekday and month in Indonesian', () => {
    render(DateField, { id: 'd', value: '2026-09-20', locale: 'id' });
    expect(screen.getByRole('button').textContent?.trim()).toBe('Minggu, 20 September 2026');
  });

  it('does the same in English, day first', () => {
    render(DateField, { id: 'd', value: '2026-09-20', locale: 'en' });
    expect(screen.getByRole('button').textContent?.trim()).toBe('Sunday, 20 September 2026');
  });

  it('shows the placeholder while empty', () => {
    render(DateField, { id: 'd', locale: 'id', placeholder: 'Pilih tanggal' });
    expect(screen.getByRole('button').textContent?.trim()).toBe('Pilih tanggal');
  });

  it('still submits through a hidden input when named', () => {
    const { container } = render(DateField, { name: 'visit_date', value: '2026-09-20' });
    expect(container.querySelector('input[type="hidden"]')?.getAttribute('value')).toBe(
      '2026-09-20'
    );
  });
});
