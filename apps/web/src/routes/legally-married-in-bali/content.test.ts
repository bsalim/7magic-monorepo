import { describe, expect, it } from 'vitest';
import { FACTS, LAST_CHECKED } from './content';

describe('legal guide facts', () => {
  // The page wins on being right where the ranking guides are years out of
  // date, so a fact without a primary source does not go on it.
  it('gives every fact an https source', () => {
    for (const [key, fact] of Object.entries(FACTS)) {
      expect(fact.source.url, key).toMatch(/^https:\/\//);
      expect(fact.text.length, key).toBeGreaterThan(20);
    }
  });

  it('dates the check', () => {
    expect(LAST_CHECKED).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  // Claims the research could not confirm from a primary source.
  it('leaves out the claims that failed verification', () => {
    const text = Object.values(FACTS)
      .map((fact) => fact.text)
      .join(' ');
    expect(text).not.toMatch(/1995/);
    expect(text).not.toMatch(/six religions|6 religions/i);
    expect(text).not.toMatch(/sponsor letter/i);
    expect(text).not.toMatch(/must marry in a Catholic church/i);
  });
});
