import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('$env/dynamic/public', () => ({ env: {} }));
import type { AlmanacDayOut, AlmanacResponse, Rating } from '$lib/tools/almanac';
import { EMAIL_KEY, UNLOCK_KEY } from '$lib/tools/lead';
import Page from './+page.svelte';

/**
 * The almanac month behind the same gate as Ba Zi: the month is read first and
 * waits blurred until this browser has given an email, then shows with a day's
 * reading open. With an email on file it shows at once.
 */

const branch = (animal_label: string, char = '巳') => ({
  index: 5,
  char,
  pinyin: 'Sì',
  element: 'fire',
  element_label: 'Api',
  animal: 'snake',
  animal_label
});
const stem = { index: 1, char: '乙', pinyin: 'Yǐ', element: 'wood', element_label: 'Kayu', yang: false };

function day(number: number, rating: Rating, overrides: Partial<AlmanacDayOut> = {}): AlmanacDayOut {
  return {
    date: `2027-03-${String(number).padStart(2, '0')}`,
    pillar: { stem, branch: branch('Ular'), depends_on_time: false, near_term: false },
    officer:
      rating === 'good'
        ? { index: 8, char: '成', pinyin: 'Chéng', label: 'Berhasil', rating: 'favoured' }
        : rating === 'avoid'
          ? { index: 6, char: '破', pinyin: 'Pò', label: 'Pecah', rating: 'avoided' }
          : { index: 3, char: '平', pinyin: 'Píng', label: 'Rata', rating: 'ordinary' },
    clashes: branch('Babi', '亥'),
    reasons: [],
    rating,
    ...overrides
  };
}

const month = (monthNumber: number): AlmanacResponse => ({
  year: 2027,
  month: monthNumber,
  shio: [branch('Babi', '亥'), branch('Tikus', '子')],
  days: Array.from({ length: 31 }, (_, index) => {
    const number = index + 1;
    const built =
      number === 6
        ? day(number, 'good', {
            reasons: [{ partner: 1, rule: 'six_combination', rule_label: 'Kombinasi Enam (Liu He)' }]
          })
        : number === 14
          ? day(number, 'good')
          : number === 7
            ? day(number, 'avoid', { reasons: [{ partner: 0, rule: 'clash', rule_label: 'Benturan (Chong)' }] })
            : day(number, 'ordinary');
    return { ...built, date: `2027-${String(monthNumber).padStart(2, '0')}-${String(number).padStart(2, '0')}` };
  })
});

type Call = { url: string; body: Record<string, unknown> };

function stubFetch(): Call[] {
  const calls: Call[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init: RequestInit) => {
      const body = JSON.parse(String(init.body));
      calls.push({ url, body });
      return url === '/api/almanac'
        ? new Response(JSON.stringify(month(body.month)), { status: 200 })
        : new Response(JSON.stringify({ ok: true }), { status: 201 });
    })
  );
  return calls;
}

async function choose() {
  await fireEvent.change(screen.getByLabelText('Bulan'), { target: { value: '3' } });
  await fireEvent.change(screen.getByLabelText('Tahun'), { target: { value: '2027' } });
  await fireEvent.change(screen.getByLabelText('Shio calon pengantin pertama'), { target: { value: 'pig' } });
  await fireEvent.change(screen.getByLabelText('Shio calon pengantin kedua'), { target: { value: 'rat' } });
}

const search = () => fireEvent.click(screen.getByRole('button', { name: 'Cari tanggal baik' }));

const GATE_TITLE = 'Kalender kalian sudah siap';
const PREVIEW_TITLE = 'Kalender kalian muncul di sini';
const goodHeading = () => screen.queryByRole('heading', { name: 'Tanggal baik bulan ini' });
// jsdom does not reflect `inert` to an attribute, so the blur stands in for it.
const lockedCalendar = () => document.querySelector('#tionghoa-result [aria-hidden="true"][class*="blur-"]');

describe('Tanggal Baik Tionghoa page', () => {
  beforeEach(() => {
    // jsdom has neither, and the page scrolls to the calendar after reading it.
    vi.stubGlobal('matchMedia', () => ({ matches: true }));
    Element.prototype.scrollIntoView = vi.fn();
    // The year picker starts at the current year; pin it so 2027 is on offer.
    vi.useFakeTimers({ toFake: ['Date'], now: new Date('2026-11-21T03:00:00Z') });
  });

  afterEach(() => {
    vi.useRealTimers();
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  it('asks for both shio before reading a month', async () => {
    const calls = stubFetch();
    render(Page);
    expect(screen.getByText(PREVIEW_TITLE)).toBeInTheDocument();

    await fireEvent.change(screen.getByLabelText('Shio calon pengantin pertama'), { target: { value: 'pig' } });
    await search();

    expect(await screen.findByRole('alert')).toHaveTextContent('Pilih shio kalian berdua dulu.');
    expect(calls).toEqual([]);
  });

  it('holds the calendar behind the gate until an email is given', async () => {
    // The flag another tool left is not an email: this browser is still asked.
    localStorage.setItem(UNLOCK_KEY, JSON.stringify({ unlockedAt: '2026-11-01T00:00:00.000Z' }));
    const calls = stubFetch();
    render(Page);
    await choose();
    await search();

    expect(await screen.findByText(GATE_TITLE)).toBeInTheDocument();
    expect(lockedCalendar()).not.toBeNull();
    expect(calls[0]).toEqual({
      url: '/api/almanac',
      body: { year: 2027, month: 3, shio: ['pig', 'rat'], locale: 'id' }
    });

    await fireEvent.input(screen.getByLabelText('Email'), { target: { value: 'raka@example.com' } });
    expect(screen.getByLabelText(/Nomor WhatsApp/)).not.toBeRequired();
    await fireEvent.click(screen.getByRole('checkbox', { name: /Saya setuju/ }));
    await fireEvent.click(screen.getByRole('button', { name: 'Buka kalender' }));

    await waitFor(() => expect(lockedCalendar()).toBeNull());
    expect(screen.queryByText(GATE_TITLE)).toBeNull();
    expect(screen.getByRole('heading', { name: 'Maret 2027' })).toBeInTheDocument();
    const lead = calls.find((call) => call.url === '/api/tool-lead');
    expect(lead?.body).toMatchObject({
      tool: 'tionghoa',
      email: 'raka@example.com',
      phone: null,
      inputs: { month: 'Maret 2027', shio: 'Babi & Tikus', good_days: '6, 14' },
      source_path: '/wedding-tools/tanggal-baik-tionghoa'
    });
    expect(localStorage.getItem(EMAIL_KEY)).toBe('raka@example.com');
  });

  it('shows the month at once to a browser with an email on file, first good day open', async () => {
    localStorage.setItem(EMAIL_KEY, 'raka@example.com');
    const calls = stubFetch();
    render(Page);
    await waitFor(() => expect(screen.queryByText(/Sebelum kalender tampil/)).toBeNull());
    await choose();
    await search();

    await waitFor(() => expect(goodHeading()).not.toBeNull());
    expect(screen.queryByText(GATE_TITLE)).toBeNull();
    expect(calls.map((call) => call.url)).toEqual(['/api/almanac']);
    expect(screen.getByText('2 hari umum dipilih untuk pernikahan, 1 hari dihindari.')).toBeInTheDocument();

    // The 6th is the first good day: its reading is open, with the note for the second partner.
    expect(screen.getByRole('heading', { name: 'Sabtu, 6 Maret 2027' })).toBeInTheDocument();
    expect(screen.getByText(/Hari Chéng \(Berhasil\): salah satu dari tiga hari/)).toBeInTheDocument();
    expect(screen.getByText('Hari Ular berkombinasi (Liu He) dengan shio Tikus.')).toBeInTheDocument();
  });

  it('opens the reading of whichever day is picked', async () => {
    localStorage.setItem(EMAIL_KEY, 'raka@example.com');
    stubFetch();
    render(Page);
    await choose();
    await search();
    await waitFor(() => expect(goodHeading()).not.toBeNull());

    await fireEvent.click(screen.getByRole('button', { name: 'Minggu, 7 Maret 2027: Dihindari' }));

    expect(screen.getByRole('heading', { name: 'Minggu, 7 Maret 2027' })).toBeInTheDocument();
    expect(screen.getByText(/Hari Pò \(Pecah\): hari yang umum dihindari/)).toBeInTheDocument();
    expect(screen.getByText('Hari Ular ciong (berbenturan) dengan shio Babi.')).toBeInTheDocument();
  });

  it('steps to the next month from the arrows over the calendar', async () => {
    localStorage.setItem(EMAIL_KEY, 'raka@example.com');
    const calls = stubFetch();
    render(Page);
    await choose();
    await search();
    await waitFor(() => expect(goodHeading()).not.toBeNull());

    await fireEvent.click(screen.getByRole('button', { name: 'Bulan berikutnya' }));

    expect(await screen.findByRole('heading', { name: 'April 2027' })).toBeInTheDocument();
    expect(calls.at(-1)?.body).toMatchObject({ year: 2027, month: 4 });
    expect(screen.getByLabelText('Bulan')).toHaveValue('4');
  });
});
