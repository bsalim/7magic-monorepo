<script module lang="ts">
  import type { Verdict } from '$lib/tools/bazi';

  export type BaziCardCopy = {
    fallbackTitle: string;
    kicker: string;
    pillarLabels: [string, string, string, string];
    datesTitle: string;
    verdicts: Record<Verdict, string>;
  };

  /** One partner's chart as the card needs it: names and characters only. */
  export type BaziCardChart = {
    name: string;
    /** Year, month, day, hour as stem + branch characters; null for an unknown hour. */
    pillars: ([string, string] | null)[];
    /** "Day master 乙 Kayu · Shio Babi". */
    summary: string;
  };

  export type BaziCardDate = { label: string; verdict: Verdict };
</script>

<script lang="ts">
  import { downloadBlob, printCard, svgToPng } from '$lib/tools/card-export';

  /**
   * The couple's Ba Zi card: a 4:5 portrait SVG, 1080 x 1350, in the cream and
   * gold of the mahar and hashtag cards so the set reads as one.
   *
   * Families pass a chart round on WhatsApp or bring it to a consultation, so
   * the eight characters per person are the largest thing on it; the reading
   * stays on the page, where it has room to be qualified.
   */

  interface Props {
    charts: BaziCardChart[];
    tone: string;
    dates: BaziCardDate[];
    copy: BaziCardCopy;
    /** Accessible summary, read instead of the SVG's text runs. */
    label: string;
    class?: string;
  }

  let { charts, tone, dates, copy, label, class: className }: Props = $props();

  const WIDTH = 1080;
  const HEIGHT = 1350;
  const CENTER = WIDTH / 2;
  const MEASURE = 840;
  const COLUMNS = [255, 445, 635, 825];

  const SERIF = "Georgia, 'Times New Roman', serif";
  const HAN = "'Noto Serif SC', 'Songti SC', 'STSong', 'SimSun', serif";
  const BODY = "'Jost Variable', Jost, ui-sans-serif, system-ui, sans-serif";

  const VERDICT_FILL: Record<Verdict, string> = { safe: '#3f7a4f', consider: '#b07a1f', clash: '#a3412f' };

  let svg = $state<SVGSVGElement>();

  // Same estimate as the other cards: SVG text cannot be measured during SSR.
  const fit = (text: string, max: number, advance: number) =>
    Math.min(max, Math.floor(MEASURE / Math.max(1, text.length * advance)));

  const title = $derived(
    charts
      .map((chart) => chart.name)
      .filter(Boolean)
      .join(' & ') || copy.fallbackTitle
  );
  const titleSize = $derived(fit(title, 80, 0.5));
  // With dates the charts move up to leave the foot free for the list.
  const top = $derived(dates.length ? 360 : 400);
  const blockHeight = 300;

  function fileName(): string {
    const slug = charts
      .map((chart) => chart.name.toLowerCase().replace(/[^a-z0-9]+/g, ''))
      .filter(Boolean)
      .join('-');
    return `bazi-${slug || 'pasangan'}.png`;
  }

  export async function downloadPng(): Promise<void> {
    if (!svg) return;
    downloadBlob(await svgToPng(svg, WIDTH, HEIGHT), fileName());
  }

  export function print(): void {
    if (svg) printCard(svg);
  }
</script>

<svg
  bind:this={svg}
  viewBox="0 0 {WIDTH} {HEIGHT}"
  role="img"
  aria-label={label}
  class={className}
  xmlns="http://www.w3.org/2000/svg"
>
  <defs>
    <radialGradient id="bazi-card-glow" cx="50%" cy="22%" r="80%">
      <stop offset="0%" stop-color="#fffdf8" />
      <stop offset="70%" stop-color="#fbf7f0" />
      <stop offset="100%" stop-color="#f2e4cc" />
    </radialGradient>
    <linearGradient id="bazi-card-gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#d4b27f" />
      <stop offset="50%" stop-color="#b08542" />
      <stop offset="100%" stop-color="#8a6524" />
    </linearGradient>
  </defs>

  <rect width={WIDTH} height={HEIGHT} fill="url(#bazi-card-glow)" />
  <rect x="44" y="44" width="992" height="1262" rx="30" fill="none" stroke="url(#bazi-card-gold)" stroke-width="3" />
  <rect x="66" y="66" width="948" height="1218" rx="20" fill="none" stroke="#b08542" stroke-opacity="0.45" stroke-width="1.5" />

  {#each [[66, 66, 0], [1014, 66, 90], [1014, 1284, 180], [66, 1284, 270]] as [x, y, angle] (angle)}
    <g transform="translate({x} {y}) rotate({angle})" fill="#b08542" fill-opacity="0.7">
      <path d="M18 18 C 38 22, 52 36, 56 56 C 36 52, 22 38, 18 18 Z" />
      <circle cx="16" cy="16" r="4" />
    </g>
  {/each}

  <text
    x={CENTER}
    y="170"
    text-anchor="middle"
    font-family={BODY}
    font-weight="500"
    font-size="27"
    letter-spacing="9"
    fill="#8a6524">{copy.kicker}</text
  >

  <text x={CENTER} y="262" text-anchor="middle" font-family={SERIF} font-style="italic" font-size={titleSize} fill="#141414"
    >{title}</text
  >

  <g transform="translate({CENTER} 310)">
    <line x1="-90" y1="0" x2="-14" y2="0" stroke="#b08542" stroke-opacity="0.7" stroke-width="1.5" />
    <line x1="14" y1="0" x2="90" y2="0" stroke="#b08542" stroke-opacity="0.7" stroke-width="1.5" />
    <circle r="5" fill="#b08542" />
  </g>

  {#each charts as chart, index (index)}
    {@const y = top + index * blockHeight}
    <text x="130" y={y + 40} font-family={BODY} font-weight="600" font-size="30" fill="#141414">{chart.name}</text>
    <text x="950" y={y + 40} text-anchor="end" font-family={BODY} font-size="24" fill="#5f5a52">{chart.summary}</text>
    {#each COLUMNS as x, column (column)}
      {@const pillar = chart.pillars[column]}
      <text x={x} y={y + 88} text-anchor="middle" font-family={BODY} font-size="22" letter-spacing="3" fill="#8a6524"
        >{copy.pillarLabels[column].toUpperCase()}</text
      >
      <rect x={x - 70} y={y + 106} width="140" height="166" rx="16" fill="#fffdf8" stroke="#b08542" stroke-opacity="0.35" />
      {#if pillar}
        <text x={x} y={y + 180} text-anchor="middle" font-family={HAN} font-size="64" fill="#141414">{pillar[0]}</text>
        <text x={x} y={y + 254} text-anchor="middle" font-family={HAN} font-size="64" fill="#8a6524">{pillar[1]}</text>
      {:else}
        <text x={x} y={y + 210} text-anchor="middle" font-family={SERIF} font-size="56" fill="#a39a8c">?</text>
      {/if}
    {/each}
  {/each}

  <text
    x={CENTER}
    y={top + 2 * blockHeight + 40}
    text-anchor="middle"
    font-family={SERIF}
    font-style="italic"
    font-size="38"
    fill="#5f5a52">{tone}</text
  >

  {#if dates.length}
    {@const listTop = top + 2 * blockHeight + 100}
    <text x={CENTER} y={listTop} text-anchor="middle" font-family={BODY} font-size="22" letter-spacing="4" fill="#8a6524"
      >{copy.datesTitle.toUpperCase()}</text
    >
    {#each dates as item, index (index)}
      <text x={CENTER - 20} y={listTop + 48 + index * 42} text-anchor="end" font-family={BODY} font-size="28" fill="#3a3a3a"
        >{item.label}</text
      >
      <text
        x={CENTER + 20}
        y={listTop + 48 + index * 42}
        font-family={BODY}
        font-weight="600"
        font-size="28"
        fill={VERDICT_FILL[item.verdict]}>{copy.verdicts[item.verdict]}</text
      >
    {/each}
  {/if}

  <line x1={CENTER - 60} y1="1220" x2={CENTER + 60} y2="1220" stroke="#b08542" stroke-opacity="0.5" stroke-width="1.5" />
  <text
    x={CENTER}
    y="1262"
    text-anchor="middle"
    font-family={BODY}
    font-weight="500"
    font-size="24"
    letter-spacing="6"
    fill="#b08542">7magicwedding</text
  >
</svg>
