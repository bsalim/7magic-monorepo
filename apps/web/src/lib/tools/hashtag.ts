/**
 * Wedding hashtags from the couple's names: the logic behind the hashtag
 * generator.
 *
 * Pure and deterministic, with no DOM and no randomness, so the server render,
 * the hydrated page and the tests all list the same tags in the same order. A
 * "shuffle" would have to break that, and a couple comparing two lists on two
 * phones would see different ones.
 *
 * Every tag is CamelCase: Instagram treats #AndreAmanda and #andreamanda as
 * one tag, so the capitals cost nothing and make a long tag readable on a sign.
 */

import { parseIsoDate } from './mahar';

export type HashtagEvent = 'lamaran' | 'prewedding' | 'sangjit' | 'akad' | 'pemberkatan' | 'resepsi';
export type HashtagGroupId = 'classic' | 'blend' | 'indonesian' | 'english' | 'date' | 'events';

export type HashtagInput = {
  groom: string;
  bride: string;
  /** The family name the couple will share, for #HappilyEver… and #MrAndMrs…. */
  family?: string;
  /** ISO "YYYY-MM-DD", as `DateField` binds it. */
  date?: string;
  city?: string;
  events?: HashtagEvent[];
  /** Whose name leads the name-pair tags. Role tags (#…SaidYes) ignore it. */
  brideFirst?: boolean;
};

export type Hashtag = {
  /** With the leading "#". */
  tag: string;
  /** Over `LONG_TAG` characters: easy to mistype from a sign, so flagged, not dropped. */
  long: boolean;
};

export type HashtagGroup = { id: HashtagGroupId; tags: Hashtag[] };

export const LONG_TAG = 24;

export const HASHTAG_EVENTS: HashtagEvent[] = [
  'lamaran',
  'prewedding',
  'sangjit',
  'akad',
  'pemberkatan',
  'resepsi'
];

/**
 * How each event reads at the end of a tag. "Prewed" because that is how
 * couples here write it; "HolyMatrimony" because church weddings in Indonesia
 * are announced in English far more often than as "pemberkatan".
 */
const EVENT_SUFFIX: Record<HashtagEvent, string> = {
  lamaran: 'Lamaran',
  prewedding: 'Prewed',
  sangjit: 'Sangjit',
  akad: 'Akad',
  pemberkatan: 'HolyMatrimony',
  resepsi: 'Resepsi'
};

const VOWELS = new Set(['a', 'e', 'i', 'o', 'u']);
const isVowel = (letter: string) => VOWELS.has(letter.toLowerCase());

// Onsets that stay together when a syllable is cut off the end of a name:
// An-dre, Pu-tri, Sya-fi-ra. Splitting them would leave "re" or "ri".
const CLUSTERS = new Set([
  'bl', 'br', 'ch', 'dr', 'fl', 'fr', 'gl', 'gr', 'kh', 'kl', 'kr', 'ng', 'ny',
  'ph', 'pl', 'pr', 'sh', 'sy', 'th', 'tr'
]);

const capitalise = (word: string) => (word ? word[0].toUpperCase() + word.slice(1) : '');

/**
 * A name as it can appear inside a hashtag: accents stripped, anything but
 * letters and digits removed, each word capitalised, words joined.
 *
 * A word typed all in one case is re-cased ("ANDRE", "andre" → "Andre"); a
 * mixed-case one keeps its inner capitals, so "McKenzie" survives.
 */
export function toTagWord(raw: string | null | undefined): string {
  if (!raw) return '';
  return raw
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .split(/[^A-Za-z0-9]+/)
    .filter(Boolean)
    .map((word) => {
      const oneCase = word === word.toLowerCase() || word === word.toUpperCase();
      return capitalise(oneCase ? word.toLowerCase() : word);
    })
    .join('');
}

/** The first word of a CamelCase tag word, which is what the blends cut from. */
function firstWord(word: string): string {
  const match = /^[A-Z0-9]?[a-z0-9]*/.exec(word);
  return match?.[0] || word;
}

/**
 * The opening of a name, for blends: up to its first vowel (Raka → Ra,
 * Brian → Bri), or the first two letters when it starts with one (Andre → An,
 * Amanda → Am), since a lone vowel says nothing about whose name it was.
 */
export function nameHead(name: string): string {
  const word = firstWord(name);
  if (word.length <= 2) return word;
  if (isVowel(word[0])) return word.slice(0, 2);
  for (let index = 1; index < word.length; index++) {
    if (isVowel(word[index])) return word.slice(0, index + 1);
  }
  return word;
}

/**
 * The last syllable of a name, for blends: its final vowel run, the
 * consonants after it, and its onset (one consonant, or two that belong
 * together). Amanda → da, Kevin → vin, Andre → dre, Nadia → dia.
 */
export function nameTail(name: string): string {
  const word = firstWord(name).toLowerCase();
  let end = word.length - 1;
  while (end >= 0 && !isVowel(word[end])) end--;
  if (end < 0) return word;
  let start = end;
  // Two vowels at most: Na-di-a reads as "dia" at the end, not "a".
  if (start > 0 && isVowel(word[start - 1])) start--;
  if (start >= 2 && CLUSTERS.has(word.slice(start - 2, start))) start -= 2;
  else if (start >= 1 && !isVowel(word[start - 1])) start -= 1;
  return word.slice(start);
}

/** The groups of tags for one couple; groups with nothing in them are left out. */
export function generateHashtags(input: HashtagInput): HashtagGroup[] {
  const groom = toTagWord(input.groom);
  const bride = toTagWord(input.bride);
  if (!groom || !bride) return [];

  const [first, second] = input.brideFirst ? [bride, groom] : [groom, bride];
  const pair = `${first}${second}`;
  const family = toTagWord(input.family);
  const city = toTagWord(input.city);
  const date = parseIsoDate(input.date);

  const headPair = capitalise(nameHead(first)) + capitalise(nameHead(second));
  const headTail = capitalise(nameHead(first)) + nameTail(second);
  const tailHead = capitalise(nameHead(second)) + nameTail(first);

  const groups: [HashtagGroupId, string[]][] = [
    ['classic', [pair, `${second}${first}`, `${first}Dan${second}`, `${first}And${second}`, `${pair}Wedding`]],
    ['blend', [headPair, headTail, tailHead, `${headPair}Wedding`, `${headTail}Forever`]],
    [
      'indonesian',
      [
        `Sahnya${pair}`,
        // "Halalin" (to make it halal, i.e. to marry) is said of the groom.
        `${groom}Halalin${bride}`,
        `Kisah${pair}`,
        `${pair}Selamanya`,
        `Akhirnya${pair}`,
        `${headPair}Menikah`
      ]
    ],
    [
      'english',
      [
        `${first}Loves${second}`,
        `${bride}SaidYes`,
        `${pair}EverAfter`,
        `Team${headPair}`,
        ...(family ? [`HappilyEver${family}`, `MrAndMrs${family}`] : [])
      ]
    ]
  ];

  if (date) {
    const dd = String(date.day).padStart(2, '0');
    const mm = String(date.month).padStart(2, '0');
    const yy = String(date.year % 100).padStart(2, '0');
    groups.push([
      'date',
      [`${pair}${date.year}`, `${headPair}${dd}${mm}${yy}`, `${headPair}${date.year}`, `${pair}${dd}${mm}`]
    ]);
  }

  const events = HASHTAG_EVENTS.filter((event) => input.events?.includes(event));
  const eventTags = events.map((event) => `${pair}${EVENT_SUFFIX[event]}`);
  if (city) eventTags.push(`${pair}Di${city}`, `${headPair}In${city}`);
  if (eventTags.length) groups.push(['events', eventTags]);

  // One tag appears once, in the first group that produced it: short names
  // make blends that equal a plain pair (Al + Ra), and so on.
  const seen = new Set<string>();
  const fresh = (word: string) => {
    const key = word.toLowerCase();
    if (word.length < 3 || seen.has(key)) return false;
    seen.add(key);
    return true;
  };
  return groups
    .map(([id, words]) => ({
      id,
      tags: words.filter(fresh).map((word) => ({ tag: `#${word}`, long: word.length > LONG_TAG }))
    }))
    .filter((group) => group.tags.length);
}

/** The tag's page on Instagram, where a couple can see whether it is taken. */
export function instagramTagUrl(tag: string): string {
  return `https://www.instagram.com/explore/tags/${encodeURIComponent(tag.replace(/^#/, '').toLowerCase())}/`;
}
