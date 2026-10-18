import { describe, expect, it } from 'vitest';
import {
  LONG_TAG,
  generateHashtags,
  instagramTagUrl,
  nameHead,
  nameTail,
  toTagWord,
  type HashtagInput
} from './hashtag';

const tagsOf = (input: HashtagInput) =>
  Object.fromEntries(generateHashtags(input).map((group) => [group.id, group.tags.map((t) => t.tag)]));

describe('toTagWord', () => {
  it('capitalises and joins words, dropping punctuation and spaces', () => {
    expect(toTagWord('andre')).toBe('Andre');
    expect(toTagWord('ANDRE')).toBe('Andre');
    expect(toTagWord('anne-marie  putri')).toBe('AnneMariePutri');
    expect(toTagWord("Sya'ban")).toBe('SyaBan');
  });

  it('strips accents and keeps inner capitals of a mixed-case name', () => {
    expect(toTagWord('Renée')).toBe('Renee');
    expect(toTagWord('McKenzie')).toBe('McKenzie');
  });

  it('returns nothing for empty or symbol-only input', () => {
    expect(toTagWord('')).toBe('');
    expect(toTagWord('  !!  ')).toBe('');
    expect(toTagWord(undefined)).toBe('');
  });
});

describe('nameHead', () => {
  it('cuts up to the first vowel', () => {
    expect(nameHead('Raka')).toBe('Ra');
    expect(nameHead('Brian')).toBe('Bri');
    expect(nameHead('Christian')).toBe('Chri');
  });

  it('keeps two letters when the name opens with a vowel', () => {
    expect(nameHead('Andre')).toBe('An');
    expect(nameHead('Amanda')).toBe('Am');
  });

  it('reads only the first word of a two-word name', () => {
    expect(nameHead('MuhammadRizky')).toBe('Mu');
  });
});

describe('nameTail', () => {
  it('takes the last syllable', () => {
    expect(nameTail('Amanda')).toBe('da');
    expect(nameTail('Kevin')).toBe('vin');
    expect(nameTail('Raka')).toBe('ka');
  });

  it('keeps a consonant cluster and a two-vowel ending together', () => {
    expect(nameTail('Andre')).toBe('dre');
    expect(nameTail('Putri')).toBe('tri');
    expect(nameTail('Nadia')).toBe('dia');
  });
});

describe('generateHashtags', () => {
  it('needs both names', () => {
    expect(generateHashtags({ groom: 'Raka', bride: '' })).toEqual([]);
    expect(generateHashtags({ groom: '', bride: 'Nadia' })).toEqual([]);
  });

  it('builds the name pairs and the blends', () => {
    const tags = tagsOf({ groom: 'Raka', bride: 'Nadia' });
    expect(tags.classic).toEqual([
      '#RakaNadia',
      '#NadiaRaka',
      '#RakaDanNadia',
      '#RakaAndNadia',
      '#RakaNadiaWedding'
    ]);
    expect(tags.blend).toEqual(['#RaNa', '#Radia', '#Naka', '#RaNaWedding', '#RadiaForever']);
  });

  it('puts the bride first when asked, but keeps role tags on their role', () => {
    const tags = tagsOf({ groom: 'Raka', bride: 'Nadia', brideFirst: true });
    expect(tags.classic[0]).toBe('#NadiaRaka');
    expect(tags.blend[0]).toBe('#NaRa');
    expect(tags.indonesian).toContain('#RakaHalalinNadia');
    expect(tags.english).toContain('#NadiaSaidYes');
    expect(tags.english).toContain('#NadiaLovesRaka');
  });

  it('adds the family-name tags only when there is a family name', () => {
    expect(tagsOf({ groom: 'Raka', bride: 'Nadia' }).english).not.toContain('#MrAndMrsWijaya');
    const tags = tagsOf({ groom: 'Raka', bride: 'Nadia', family: 'wijaya' });
    expect(tags.english).toContain('#HappilyEverWijaya');
    expect(tags.english).toContain('#MrAndMrsWijaya');
  });

  it('adds date tags from a valid date only', () => {
    const tags = tagsOf({ groom: 'Raka', bride: 'Nadia', date: '2026-09-20' });
    expect(tags.date).toEqual(['#RakaNadia2026', '#RaNa200926', '#RaNa2026', '#RakaNadia2009']);
    expect(tagsOf({ groom: 'Raka', bride: 'Nadia', date: '2026-02-30' }).date).toBeUndefined();
  });

  it('adds one tag per chosen event, in the order of the day, and the city', () => {
    const tags = tagsOf({
      groom: 'Raka',
      bride: 'Nadia',
      events: ['resepsi', 'lamaran', 'pemberkatan'],
      city: 'bandung'
    });
    expect(tags.events).toEqual([
      '#RakaNadiaLamaran',
      '#RakaNadiaHolyMatrimony',
      '#RakaNadiaResepsi',
      '#RakaNadiaDiBandung',
      '#RaNaInBandung'
    ]);
  });

  it('leaves out the event group when nothing feeds it', () => {
    expect(tagsOf({ groom: 'Raka', bride: 'Nadia' }).events).toBeUndefined();
  });

  it('never lists a tag twice, whatever its case', () => {
    // Two-letter names make blends that equal the plain pair: Al + Ra.
    const all = generateHashtags({ groom: 'Al', bride: 'Ra' }).flatMap((group) =>
      group.tags.map((t) => t.tag.toLowerCase())
    );
    expect(new Set(all).size).toBe(all.length);
  });

  it('flags long tags rather than dropping them', () => {
    const groups = generateHashtags({ groom: 'Maximilian', bride: 'Anastasia' });
    const all = groups.flatMap((group) => group.tags);
    const long = all.find((t) => t.tag === '#MaximilianAnastasiaWedding');
    expect(long?.long).toBe(true);
    expect(all.find((t) => t.tag === '#MaximilianAnastasia')?.long).toBe(false);
    for (const t of all) expect(t.long).toBe(t.tag.length - 1 > LONG_TAG);
  });

  it('only ever emits letters and digits after the #', () => {
    const groups = generateHashtags({ groom: 'José-Luis', bride: "D'Angela", city: 'Nusa Dua!' });
    for (const t of groups.flatMap((group) => group.tags)) expect(t.tag).toMatch(/^#[A-Za-z0-9]+$/);
  });
});

describe('instagramTagUrl', () => {
  it('links the lower-case tag page', () => {
    expect(instagramTagUrl('#RakaNadia')).toBe('https://www.instagram.com/explore/tags/rakanadia/');
  });
});
