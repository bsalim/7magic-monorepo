import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import { hubCopy } from '../../../routes/wedding-tools/content';
import PopularTools from './PopularTools.svelte';
import ToolIcon from './ToolIcon.svelte';

describe('ToolIcon', () => {
  it('has a drawing for every card on the hub', () => {
    for (const tool of hubCopy('id').tools) {
      const { container, unmount } = render(ToolIcon, { tool: tool.key });
      const svg = container.querySelector('svg');
      // More than the halo: an unknown name would leave the circle alone.
      expect(svg?.children.length, tool.key).toBeGreaterThan(1);
      expect(svg).toHaveAttribute('aria-hidden', 'true');
      unmount();
    }
  });
});

describe('PopularTools', () => {
  it('links each tool by its title, and the whole hub', () => {
    render(PopularTools, {
      eyebrow: 'Wedding Tools',
      title: 'Alat gratis',
      body: 'Gratis.',
      tools: [
        { key: 'mahar', title: 'Mahar dari Tanggal Pernikahan', copy: 'Ubah tanggal.', href: '/wedding-tools/mahar' },
        { key: 'tionghoa', title: 'Tanggal Baik Tionghoa', copy: 'Kalender sebulan.', href: '/wedding-tools/tanggal' }
      ],
      allHref: '/wedding-tools',
      allLabel: 'Lihat semua alat',
      openLabel: 'Buka alat'
    });

    expect(screen.getByRole('link', { name: /Mahar dari Tanggal Pernikahan/ })).toHaveAttribute(
      'href',
      '/wedding-tools/mahar'
    );
    expect(screen.getByRole('link', { name: /Tanggal Baik Tionghoa/ })).toHaveAttribute('href', '/wedding-tools/tanggal');
    expect(screen.getByRole('link', { name: 'Lihat semua alat' })).toHaveAttribute('href', '/wedding-tools');
  });
});
