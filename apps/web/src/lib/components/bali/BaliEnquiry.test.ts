import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { CONCIERGE_SERVICES } from '$lib/bali-concierge';
import BaliEnquiry from './BaliEnquiry.svelte';
import { enquiryMessage } from './enquiry';

describe('enquiryMessage', () => {
  // The contact-lead API rejects a message over 2000 characters, and a couple
  // who ticks every add-on is exactly the lead we least want to lose.
  it('stays within the API limit with every add-on and keeps & as typed', () => {
    const context = [
      'Guests: 150',
      'Setting: Clifftop',
      'Month: July 2027',
      'Style: Luxe',
      'Estimate: A$60,000 – A$95,000',
      `Add-ons: ${CONCIERGE_SERVICES.map((service) => service.name).join(', ')}`
    ];
    const message = enquiryMessage(context, 'x'.repeat(3000));
    expect(message.length).toBeLessThanOrEqual(2000);
    expect(message).toContain('Hens & bucks in Bali');
    expect(message.startsWith('Guests: 150')).toBe(true);
  });

  it('says so when there are no notes', () => {
    expect(enquiryMessage(['Guests: 2'], '  ')).toBe('Guests: 2\n\nNo extra notes.');
  });
});

describe('BaliEnquiry', () => {
  const props = {
    sourcePath: '/bali-wedding-cost',
    heading: 'Get your real quote',
    context: ['Guests: 55', 'Setting: Villa'],
    whatsappText: 'Hi 7Magic, 55 guests & a villa',
    event: 'Bali Cost Quote Requested'
  };

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('pre-fills WhatsApp with the text, ampersand encoded', () => {
    render(BaliEnquiry, { props });
    const link = screen.getByRole('link', { name: /WhatsApp/ });
    expect(link.getAttribute('href')).toContain(encodeURIComponent('55 guests & a villa'));
  });

  it('posts the lead with its source path and the context first', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 201 }));
    vi.stubGlobal('fetch', fetchMock);
    render(BaliEnquiry, { props });

    await fireEvent.input(screen.getByLabelText(/Your name/), { target: { value: 'Sam' } });
    await fireEvent.input(screen.getByLabelText(/^WhatsApp/), {
      target: { value: '+61 400 000 000' }
    });
    await fireEvent.submit(screen.getByRole('button', { name: /Send/ }).closest('form')!);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/contact-lead');
    const body = JSON.parse(init.body);
    expect(body.source_path).toBe('/bali-wedding-cost');
    expect(body.message.startsWith('Guests: 55\nSetting: Villa')).toBe(true);
    expect(body.name).toBe('Sam');
  });
});
