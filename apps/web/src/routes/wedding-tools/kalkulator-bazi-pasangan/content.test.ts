import { describe, expect, it } from 'vitest';
import { baziCopy } from './content';

describe('Ba Zi copy', () => {
  it('tells couples honestly what the team receives when they unlock', () => {
    const id = baziCopy('id').faqs.find((faq) => /disimpan/.test(faq.q));
    const en = baziCopy('en').faqs.find((faq) => /store/.test(faq.q));
    expect(id?.a).toMatch(/nama/);
    expect(id?.a).toMatch(/email/);
    expect(id?.a).toMatch(/WhatsApp/);
    expect(en?.a).toMatch(/names/);
    expect(en?.a).toMatch(/email/);
    expect(en?.a).toMatch(/WhatsApp/);
  });

  it('has neutral fallback names that are not the example couple', () => {
    for (const locale of ['id', 'en'] as const) {
      const copy = baziCopy(locale);
      for (const name of copy.form.partnerFallback) {
        expect(copy.example.partners.map((p) => p.name)).not.toContain(name);
      }
    }
  });

  it('has a caveat for readings built on an uncertain pillar', () => {
    expect(baziCopy('id').result.uncertainNote).toBeTruthy();
    expect(baziCopy('en').result.uncertainNote).toBeTruthy();
  });
});
