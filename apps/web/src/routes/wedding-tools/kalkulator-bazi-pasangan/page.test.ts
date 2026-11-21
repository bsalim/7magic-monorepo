import { fireEvent, render, screen, waitFor, within } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('$env/dynamic/public', () => ({ env: {} }));
import { EMAIL_KEY, UNLOCK_KEY } from '$lib/tools/lead';
import type { BaziResponse } from '$lib/tools/bazi';
import Page from './+page.svelte';

/**
 * The result gate: until this browser has given an email, a calculation is
 * run but stays blurred behind the gate, whose lead carries that calculation so
 * the API can email the couple the card and a copy. The card is not on the page
 * at all; the email is the only place it appears.
 */

const stem = (char: string, element_label: string) => ({
  index: 0,
  char,
  pinyin: 'Jiǎ',
  element: 'wood',
  element_label,
  yang: true
});
const branch = (animal_label: string) => ({
  index: 0,
  char: '子',
  pinyin: 'Zǐ',
  element: 'water',
  element_label: 'Air',
  animal: 'rat',
  animal_label
});
const pillar = { stem: stem('甲', 'Kayu'), branch: branch('Tikus'), depends_on_time: false, near_term: false };
const chart = (name: string, shio: string) => ({
  name,
  year: pillar,
  month: pillar,
  day: pillar,
  hour: null,
  day_master: stem('甲', 'Kayu'),
  shio: branch(shio),
  elements: { wood: 2, fire: 1, earth: 1, metal: 1, water: 1 }
});
const RESULT: BaziResponse = {
  charts: [chart('Raka', 'Babi'), chart('Nadia', 'Tikus')],
  tone: 'balanced',
  tone_label: 'Seimbang',
  findings: [],
  date_checks: [{ date: '2026-09-26', pillar, verdict: 'safe', reasons: [] }]
};

type Call = { url: string; body: Record<string, unknown> };

function stubFetch(): Call[] {
  const calls: Call[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init: RequestInit) => {
      calls.push({ url, body: JSON.parse(String(init.body)) });
      return url === '/api/bazi'
        ? new Response(JSON.stringify(RESULT), { status: 200 })
        : new Response(JSON.stringify({ ok: true }), { status: 201 });
    })
  );
  return calls;
}

async function calculateExample() {
  await fireEvent.click(screen.getByRole('button', { name: 'Coba contoh: Raka & Nadia' }));
  await fireEvent.click(screen.getByRole('button', { name: 'Hitung Ba Zi' }));
}

async function fillGate(scope: ReturnType<typeof within>, submit: string, phone = '0812 3456 7890') {
  await fireEvent.input(scope.getByLabelText('Email'), { target: { value: 'raka@example.com' } });
  await fireEvent.input(scope.getByLabelText(/Nomor WhatsApp/), { target: { value: phone } });
  await fireEvent.click(scope.getByRole('checkbox', { name: /Saya setuju/ }));
  await fireEvent.click(scope.getByRole('button', { name: submit }));
}

const GATE_TITLE = 'Hasil Ba Zi kalian sudah siap';
const PREVIEW_TITLE = 'Hasil kalian muncul di sini';
// Only a result that is actually on show has the card section under it.
const cardHeading = () => screen.queryByRole('heading', { name: 'Kartu Ba Zi pasangan' });
// jsdom does not reflect `inert` to an attribute, so the blur stands in for it.
const lockedResult = () => document.querySelector('#bazi-result [aria-hidden="true"][class*="blur-"]');

describe('Ba Zi calculator page', () => {
  beforeEach(() => {
    // jsdom has neither, and the page scrolls to the result after calculating.
    vi.stubGlobal('matchMedia', () => ({ matches: true }));
    Element.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  it('shows a locked stand-in before anything is calculated', () => {
    render(Page);

    expect(screen.getByText(PREVIEW_TITLE)).toBeInTheDocument();
    expect(lockedResult()).not.toBeNull();
    expect(cardHeading()).toBeNull();
  });

  it('takes a birth date as a day, a month and a year, typed', async () => {
    const calls = stubFetch();
    render(Page);
    const type = (label: string, index: number, value: string) =>
      fireEvent.input(screen.getAllByLabelText(label)[index], { target: { value } });
    const pick = (index: number, value: string) =>
      fireEvent.change(screen.getAllByLabelText('Bulan')[index], { target: { value } });

    await type('Tanggal', 0, '5');
    await pick(0, '5');
    await type('Tahun', 0, '1995');
    await type('Tanggal', 1, '14');
    await pick(1, '4');
    // Half a year is not a date yet, so there is nothing to calculate.
    await type('Tahun', 1, '199');
    await fireEvent.click(screen.getByRole('button', { name: 'Hitung Ba Zi' }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/Isi tanggal lahir kalian berdua/);
    expect(calls).toEqual([]);

    await type('Tahun', 1, '1996');
    await fireEvent.click(screen.getByRole('button', { name: 'Hitung Ba Zi' }));

    await screen.findByText(GATE_TITLE);
    const partners = calls[0].body.partners as { birth_date: string }[];
    expect(partners.map((partner) => partner.birth_date)).toEqual(['1995-05-05', '1996-04-14']);
  });

  it('shows the example couple in the three birth fields', async () => {
    render(Page);

    await fireEvent.click(screen.getByRole('button', { name: 'Coba contoh: Raka & Nadia' }));

    await waitFor(() => expect(screen.getAllByLabelText('Tahun')[0]).toHaveValue('1995'));
    expect(screen.getAllByLabelText('Tanggal')[0]).toHaveValue('5');
    expect(screen.getAllByLabelText('Bulan')[0]).toHaveValue('5');
    expect(screen.getAllByLabelText('Bulan')[1]).toHaveValue('4');
  });

  it('asks for the email, in the place of the result, before showing a first one', async () => {
    const calls = stubFetch();
    render(Page);

    await calculateExample();

    expect(await screen.findByText(GATE_TITLE)).toBeInTheDocument();
    expect(screen.queryByText(PREVIEW_TITLE)).toBeNull();
    // Calculated already, but out of reach: blurred, inert, and no card yet.
    expect(lockedResult()).not.toBeNull();
    expect(cardHeading()).toBeNull();
    // Dates go in the same call, so the gate opens over the whole result.
    expect(calls.map((call) => call.url)).toEqual(['/api/bazi']);
    expect(calls[0].body.dates).toEqual(['2026-09-26', '2026-10-10']);
  });

  it('reveals the result once the gate is passed, and sends the calculation for the email', async () => {
    const calls = stubFetch();
    render(Page);
    await calculateExample();
    await screen.findByText(GATE_TITLE);

    await fillGate(screen, 'Buka hasil & kirim ke email');

    await waitFor(() => expect(cardHeading()).not.toBeNull());
    expect(lockedResult()).toBeNull();
    expect(screen.queryByText(GATE_TITLE)).toBeNull();
    expect(screen.getByText(/Salinan hasil dan kartu Ba Zi kami kirim ke email kalian/)).toBeInTheDocument();
    expect(screen.getByText(/Kartu ini kami kirim ke email kalian/)).toBeInTheDocument();

    const lead = calls.find((call) => call.url === '/api/tool-lead');
    expect(lead?.body).toMatchObject({
      tool: 'bazi',
      email: 'raka@example.com',
      phone: '+6281234567890',
      names: 'Raka & Nadia',
      inputs: { shio: 'Babi & Tikus', tone: 'Seimbang' },
      calculation: calls[0].body
    });
  });

  it('takes the gate back when the form changes under it', async () => {
    stubFetch();
    render(Page);
    await calculateExample();
    await screen.findByText(GATE_TITLE);

    await fireEvent.input(screen.getAllByLabelText('Nama panggilan')[0], { target: { value: 'Bima' } });

    // The waiting result was for other inputs; unlocking it would email that one.
    await waitFor(() => expect(screen.queryByText(GATE_TITLE)).toBeNull());
    expect(screen.getByText(PREVIEW_TITLE)).toBeInTheDocument();
  });

  it('opens with the email alone: WhatsApp is optional', async () => {
    const calls = stubFetch();
    render(Page);
    await calculateExample();
    await screen.findByText(GATE_TITLE);
    expect(screen.getByLabelText(/Nomor WhatsApp/)).not.toBeRequired();

    await fillGate(screen, 'Buka hasil & kirim ke email', '');

    await waitFor(() => expect(cardHeading()).not.toBeNull());
    const lead = calls.find((call) => call.url === '/api/tool-lead');
    expect(lead?.body).toMatchObject({ tool: 'bazi', email: 'raka@example.com', phone: null });
    // Remembered, so the next visit is not asked.
    expect(localStorage.getItem(EMAIL_KEY)).toBe('raka@example.com');
  });

  it('still refuses a WhatsApp number that is typed but incomplete', async () => {
    const calls = stubFetch();
    render(Page);
    await calculateExample();
    await screen.findByText(GATE_TITLE);

    await fillGate(screen, 'Buka hasil & kirim ke email', '0812');

    expect(await screen.findByText(/Nomor WhatsApp belum lengkap/)).toBeInTheDocument();
    expect(calls.map((call) => call.url)).toEqual(['/api/bazi']);
  });

  it('asks a browser that another tool unlocked before emails were remembered', async () => {
    localStorage.setItem(UNLOCK_KEY, JSON.stringify({ unlockedAt: '2026-11-01T00:00:00.000Z' }));
    stubFetch();
    render(Page);

    await calculateExample();

    expect(await screen.findByText(GATE_TITLE)).toBeInTheDocument();
    expect(cardHeading()).toBeNull();
  });

  it('never draws the card, nor offers a download or print: it comes by email', async () => {
    localStorage.setItem(EMAIL_KEY, 'raka@example.com');
    stubFetch();
    render(Page);
    await waitFor(() => expect(screen.queryByText(/Sebelum hasil tampil/)).toBeNull());
    await calculateExample();
    await waitFor(() => expect(cardHeading()).not.toBeNull());

    expect(screen.queryByText('BA ZI PASANGAN')).toBeNull();
    expect(screen.queryByRole('img', { name: /Kartu Ba Zi pasangan/ })).toBeNull();
    expect(screen.queryByRole('button', { name: /Unduh|PNG/ })).toBeNull();
    expect(screen.queryByRole('button', { name: /Cetak/ })).toBeNull();
  });

  it('does not ask a browser that has an email on file, and offers to send the result there', async () => {
    localStorage.setItem(EMAIL_KEY, 'nadia@example.com');
    const calls = stubFetch();
    render(Page);
    // The email is read on mount; the hint going away is the sign it has been.
    await waitFor(() => expect(screen.queryByText(/Sebelum hasil tampil/)).toBeNull());

    await calculateExample();

    await waitFor(() => expect(cardHeading()).not.toBeNull());
    expect(screen.queryByText(GATE_TITLE)).toBeNull();
    // No gate, so nothing was emailed: the page must not claim otherwise.
    expect(screen.queryByText(/Kartu ini kami kirim ke email kalian/)).toBeNull();
    expect(screen.queryByText(/Belum masuk\? Cek folder spam/)).toBeNull();
    expect(calls.map((call) => call.url)).toEqual(['/api/bazi']);

    await fireEvent.click(screen.getByRole('button', { name: 'Kirim hasil & kartu ke email' }));
    const dialog = within(await screen.findByRole('dialog'));
    // The address on file is offered back, not typed again.
    expect(dialog.getByLabelText('Email')).toHaveValue('nadia@example.com');
    await fillGate(dialog, 'Kirim ke email');

    expect(await screen.findByText(/Kartu ini kami kirim ke email kalian/)).toBeInTheDocument();
    const lead = calls.find((call) => call.url === '/api/tool-lead');
    expect(lead?.body).toMatchObject({ tool: 'bazi', email: 'raka@example.com', calculation: calls[0].body });
  });
});
