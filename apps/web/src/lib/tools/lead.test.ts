import { afterEach, describe, expect, it, vi } from 'vitest';
import { UNLOCK_KEY, isUnlocked, markUnlocked, normalizeWhatsapp } from './lead';

describe('normalizeWhatsapp', () => {
  it('turns the usual Indonesian spellings into +62', () => {
    expect(normalizeWhatsapp('0812-3456-7890')).toBe('+6281234567890');
    expect(normalizeWhatsapp('0812 3456 7890')).toBe('+6281234567890');
    expect(normalizeWhatsapp('6281234567890')).toBe('+6281234567890');
    expect(normalizeWhatsapp('+62 812 3456 7890')).toBe('+6281234567890');
    expect(normalizeWhatsapp('81234567890')).toBe('+6281234567890');
    expect(normalizeWhatsapp('(0812) 3456.7890')).toBe('+6281234567890');
  });

  it('leaves a foreign number in international format alone', () => {
    expect(normalizeWhatsapp('+65 9123 4567')).toBe('+6591234567');
  });

  it('rejects input that is too short or too long once normalised', () => {
    expect(normalizeWhatsapp('0812')).toBeNull();
    expect(normalizeWhatsapp('')).toBeNull();
    expect(normalizeWhatsapp('+62 812 3456 7890 1234 5678')).toBeNull();
    expect(normalizeWhatsapp('not a number')).toBeNull();
  });
});

describe('unlock flag', () => {
  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('is shared by every tool under one key', () => {
    expect(isUnlocked()).toBe(false);
    markUnlocked(new Date('2026-10-18T03:00:00Z'));
    expect(isUnlocked()).toBe(true);
    expect(JSON.parse(localStorage.getItem(UNLOCK_KEY)!)).toEqual({
      unlockedAt: '2026-10-18T03:00:00.000Z'
    });
  });

  it('ignores a corrupt stored value', () => {
    localStorage.setItem(UNLOCK_KEY, '{oops');
    expect(isUnlocked()).toBe(false);
  });

  it('never throws when storage is blocked', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    expect(isUnlocked()).toBe(false);
    expect(() => markUnlocked()).not.toThrow();
  });
});
