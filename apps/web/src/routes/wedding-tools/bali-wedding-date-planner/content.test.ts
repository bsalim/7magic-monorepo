import { describe, expect, it } from 'vitest';
import { bestMonths, faqs } from './content';

describe('date planner copy', () => {
  // Only NSW, VIC, QLD and WA school holidays were checked.
  it('claims school holidays only for the states it checked', () => {
    const text = [...bestMonths.map((b) => b.body), ...faqs.map((f) => f.a)].join(' ');
    expect(text).not.toMatch(/every state|all states/i);
  });
});
