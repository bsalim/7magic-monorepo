/**
 * The stand-in shown blurred where the result will appear, before anything has
 * been calculated: the example couple's chart, as the API answers it.
 *
 * Fixed here so the teaser costs no API call on every page view. It is never
 * readable (blurred, clipped, hidden from assistive tech), so the labels are in
 * one language and it does not matter if the engine later disagrees with it.
 */

import type { BaziResponse, BranchOut, ChartOut, PillarOut, StemOut } from '$lib/tools/bazi';

const stem = (index: number, char: string, pinyin: string, element: string, element_label: string): StemOut => ({
  index,
  char,
  pinyin,
  element,
  element_label,
  yang: index % 2 === 0
});

const branch = (index: number, char: string, pinyin: string, animal_label: string): BranchOut => ({
  index,
  char,
  pinyin,
  element: '',
  element_label: '',
  animal: '',
  animal_label
});

const pillar = (stemOut: StemOut, branchOut: BranchOut): PillarOut => ({
  stem: stemOut,
  branch: branchOut,
  depends_on_time: false,
  near_term: false
});

const YI = stem(1, '乙', 'Yǐ', 'wood', 'Kayu');
const BING = stem(2, '丙', 'Bǐng', 'fire', 'Api');
const GENG = stem(6, '庚', 'Gēng', 'metal', 'Logam');
const XIN = stem(7, '辛', 'Xīn', 'metal', 'Logam');
const REN = stem(8, '壬', 'Rén', 'water', 'Air');
const GUI = stem(9, '癸', 'Guǐ', 'water', 'Air');

const ZI = branch(0, '子', 'Zǐ', 'Tikus');
const CHEN = branch(4, '辰', 'Chén', 'Naga');
const SI = branch(5, '巳', 'Sì', 'Ular');
const SHEN = branch(8, '申', 'Shēn', 'Monyet');
const HAI = branch(11, '亥', 'Hài', 'Babi');

const raka: ChartOut = {
  name: 'Raka',
  year: pillar(YI, HAI),
  month: pillar(GENG, CHEN),
  day: pillar(BING, SHEN),
  hour: pillar(GUI, SI),
  day_master: BING,
  shio: HAI,
  elements: { wood: 1, fire: 2, earth: 1, metal: 2, water: 2 }
};

const nadia: ChartOut = {
  name: 'Nadia',
  year: pillar(BING, ZI),
  month: pillar(REN, CHEN),
  day: pillar(XIN, SI),
  hour: pillar(REN, CHEN),
  day_master: XIN,
  shio: ZI,
  elements: { wood: 0, fire: 2, earth: 2, metal: 1, water: 3 }
};

export const PREVIEW: BaziResponse = {
  charts: [raka, nadia],
  tone: 'harmony',
  tone_label: 'Banyak keselarasan',
  findings: [],
  date_checks: []
};

export const PREVIEW_NAMES: [string, string] = ['Raka', 'Nadia'];
