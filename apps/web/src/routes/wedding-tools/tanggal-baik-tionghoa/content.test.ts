import { describe, expect, it } from 'vitest';
import { ANIMALS } from '$lib/tools/almanac';
import { almanacCopy } from './content';

describe('Tanggal Baik Tionghoa copy', () => {
  it('names every shio in both languages', () => {
    for (const locale of ['id', 'en'] as const) {
      const { animals } = almanacCopy(locale);
      expect(Object.keys(animals).sort()).toEqual([...ANIMALS].sort());
    }
  });

  it('carries the note that the almanac is a tradition, in both languages', () => {
    expect(almanacCopy('id').result.elderNote).toMatch(/tradisi, bukan kepastian/);
    expect(almanacCopy('en').result.elderNote).toMatch(/tradition, not a certainty/);
  });

  it('tells couples honestly what the team receives when they unlock', () => {
    const id = almanacCopy('id').faqs.find((faq) => /disimpan/.test(faq.q));
    const en = almanacCopy('en').faqs.find((faq) => /store/.test(faq.q));
    for (const answer of [id?.a, en?.a]) {
      expect(answer).toMatch(/email/);
      expect(answer).toMatch(/WhatsApp/);
    }
    expect(id?.a).toMatch(/shio/);
    expect(en?.a).toMatch(/signs/);
  });
});
