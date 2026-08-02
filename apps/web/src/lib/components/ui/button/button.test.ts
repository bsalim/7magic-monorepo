import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import { createRawSnippet } from 'svelte';
import Button from './button.svelte';

const label = (text: string) =>
  createRawSnippet(() => ({ render: () => `<span>${text}</span>` }));

describe('Button brand variants', () => {
  it('renders the gold variant', () => {
    render(Button, { props: { variant: 'gold', children: label('Book') } });
    expect(screen.getByRole('button', { name: 'Book' }).className).toContain('bg-brand-gold');
  });

  it('renders the pink variant', () => {
    render(Button, { props: { variant: 'pink', children: label('Inspire') } });
    expect(screen.getByRole('button', { name: 'Inspire' }).className).toContain('text-brand-pink');
  });

  it('renders the whatsapp variant', () => {
    render(Button, { props: { variant: 'whatsapp', children: label('Chat') } });
    expect(screen.getByRole('button', { name: 'Chat' }).className).toContain('brand-whatsapp');
  });

  it('renders as an anchor when href is given', () => {
    render(Button, { props: { variant: 'gold', href: '/contact', children: label('Contact') } });
    expect(screen.getByRole('link', { name: 'Contact' })).toHaveAttribute('href', '/contact');
  });

  it('keeps CTAs pill-shaped', () => {
    render(Button, { props: { variant: 'gold', children: label('Quote') } });
    expect(screen.getByRole('button', { name: 'Quote' }).className).toContain('rounded-full');
  });
});
