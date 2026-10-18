<script module lang="ts">
  export type MaharCardCopy = {
    fallbackTitle: string;
    kicker: string;
    paidCash: string;
    goldPrefix: string;
    emptyAmount: string;
  };
</script>

<script lang="ts">
  import { downloadBlob, printCard, svgToPng } from '$lib/tools/card-export';

  /**
   * The mahar card: a 4:5 portrait SVG, 1080 x 1350, the size Instagram shows a
   * portrait post at without cropping.
   *
   * One SVG serves as the live preview, the PNG and the printed A5 page, so what
   * the couple sees is exactly what they download. Layout is computed here
   * rather than left to CSS because SVG text does not wrap or shrink: long names,
   * a ten-digit amount and the amount in words all have to be fitted by hand.
   */

  interface Props {
    names: string;
    /** "Minggu, 20 September 2026". */
    dateLine: string;
    /** Hijri method only: "9 Rabiul Akhir 1448 H". */
    hijriLine?: string;
    /** Formatted, or empty while no date is picked. */
    amount: string;
    /** Cash + gold only: "20,09 gram". */
    gold?: string;
    /** The amount in words. */
    words?: string;
    copy: MaharCardCopy;
    /** Accessible summary of the card, read instead of the SVG's text runs. */
    label: string;
    class?: string;
  }

  let { names, dateLine, hijriLine, amount, gold, words, copy, label, class: className }: Props =
    $props();

  const WIDTH = 1080;
  const HEIGHT = 1350;
  const CENTER = WIDTH / 2;
  /** The widest a line may run inside the inner border, with breathing room. */
  const MEASURE = 840;

  const SERIF = "Georgia, 'Times New Roman', serif";
  const DISPLAY = "Poppins, ui-sans-serif, system-ui, sans-serif";
  const BODY = "'Jost Variable', Jost, ui-sans-serif, system-ui, sans-serif";

  let svg = $state<SVGSVGElement>();

  // Average advance widths as a share of the font size, measured on the
  // typical strings: close enough to keep a line inside MEASURE without a DOM
  // measurement, which would not exist during SSR.
  const fit = (text: string, max: number, advance: number) =>
    Math.min(max, Math.floor(MEASURE / Math.max(1, text.length * advance)));

  /** Greedy wrap by characters into at most `lines` lines. */
  function wrap(text: string, perLine: number, lines: number): string[] {
    const out: string[] = [];
    let current = '';
    for (const word of text.split(' ')) {
      const next = current ? `${current} ${word}` : word;
      if (next.length > perLine && current) {
        out.push(current);
        current = word;
      } else {
        current = next;
      }
    }
    if (current) out.push(current);
    if (out.length <= lines) return out;
    return [...out.slice(0, lines - 1), out.slice(lines - 1).join(' ')];
  }

  const title = $derived(names.trim() || copy.fallbackTitle);
  const titleSize = $derived(fit(title, 92, 0.5));
  const amountText = $derived(amount || copy.emptyAmount);
  const amountSize = $derived(amount ? fit(amountText, 132, 0.6) : 64);
  const goldText = $derived(gold ? `${copy.goldPrefix} ${gold}` : '');
  const wordLines = $derived(words ? wrap(words, 46, 3) : []);

  // A vertical cursor: optional lines (Hijri, gold, words) push what follows
  // down, and the block is centred in the space between the date and the foot.
  const layout = $derived.by(() => {
    const amountY = hijriLine ? 790 : 760;
    const goldY = amountY + 92;
    const wordsY = (gold ? goldY : amountY) + (gold ? 74 : 86);
    const wordsEnd = wordsY + Math.max(0, wordLines.length - 1) * 44;
    const paidY = Math.max(1070, wordsEnd + 96);
    return { amountY, goldY, wordsY, paidY };
  });

  /** "mahar-raka-nadia-20092026.png": the bare digits, not "rp20-092-026". */
  function fileName(): string {
    const slug = `${names} ${amount.replace(/\D/g, '')}`
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
    return `mahar-${slug || 'pernikahan'}.png`;
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
    <radialGradient id="mahar-card-glow" cx="50%" cy="22%" r="80%">
      <stop offset="0%" stop-color="#fffdf8" />
      <stop offset="70%" stop-color="#fbf7f0" />
      <stop offset="100%" stop-color="#f2e4cc" />
    </radialGradient>
    <linearGradient id="mahar-card-gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#d4b27f" />
      <stop offset="50%" stop-color="#b08542" />
      <stop offset="100%" stop-color="#8a6524" />
    </linearGradient>
  </defs>

  <rect width={WIDTH} height={HEIGHT} fill="url(#mahar-card-glow)" />
  <rect x="44" y="44" width="992" height="1262" rx="30" fill="none" stroke="url(#mahar-card-gold)" stroke-width="3" />
  <rect x="66" y="66" width="948" height="1218" rx="20" fill="none" stroke="#b08542" stroke-opacity="0.45" stroke-width="1.5" />

  <!-- Corner sprigs: one small leaf pair, rotated into each corner. -->
  {#each [[66, 66, 0], [1014, 66, 90], [1014, 1284, 180], [66, 1284, 270]] as [x, y, angle] (angle)}
    <g transform="translate({x} {y}) rotate({angle})" fill="#b08542" fill-opacity="0.7">
      <path d="M18 18 C 38 22, 52 36, 56 56 C 36 52, 22 38, 18 18 Z" />
      <circle cx="16" cy="16" r="4" />
    </g>
  {/each}

  <!-- Crest: a diamond between two hairlines. -->
  <g transform="translate({CENTER} 196)">
    <line x1="-150" y1="0" x2="-30" y2="0" stroke="#b08542" stroke-width="2" />
    <line x1="30" y1="0" x2="150" y2="0" stroke="#b08542" stroke-width="2" />
    <path d="M0 -18 L18 0 L0 18 L-18 0 Z" fill="url(#mahar-card-gold)" />
    <path d="M0 -8 L8 0 L0 8 L-8 0 Z" fill="#fbf7f0" />
  </g>

  <text
    x={CENTER}
    y="282"
    text-anchor="middle"
    font-family={BODY}
    font-weight="500"
    font-size="27"
    letter-spacing="9"
    fill="#8a6524">{copy.kicker}</text
  >

  <text
    x={CENTER}
    y="410"
    text-anchor="middle"
    font-family={SERIF}
    font-style="italic"
    font-size={titleSize}
    fill="#141414">{title}</text
  >

  <g transform="translate({CENTER} 478)">
    <line x1="-90" y1="0" x2="-14" y2="0" stroke="#b08542" stroke-opacity="0.7" stroke-width="1.5" />
    <line x1="14" y1="0" x2="90" y2="0" stroke="#b08542" stroke-opacity="0.7" stroke-width="1.5" />
    <circle r="5" fill="#b08542" />
  </g>

  {#if dateLine}
    <text x={CENTER} y="568" text-anchor="middle" font-family={BODY} font-size="38" fill="#3a3a3a"
      >{dateLine}</text
    >
  {/if}
  {#if hijriLine}
    <text x={CENTER} y="624" text-anchor="middle" font-family={BODY} font-size="32" fill="#8a6524"
      >{hijriLine}</text
    >
  {/if}

  <text
    x={CENTER}
    y={layout.amountY}
    text-anchor="middle"
    font-family={DISPLAY}
    font-weight="600"
    font-size={amountSize}
    letter-spacing={amount ? -1 : 0}
    fill={amount ? '#141414' : '#a39a8c'}>{amountText}</text
  >

  {#if goldText}
    <text
      x={CENTER}
      y={layout.goldY}
      text-anchor="middle"
      font-family={DISPLAY}
      font-weight="500"
      font-size={fit(goldText, 58, 0.58)}
      fill="#8a6524">{goldText}</text
    >
  {/if}

  {#each wordLines as line, index (index)}
    <text
      x={CENTER}
      y={layout.wordsY + index * 44}
      text-anchor="middle"
      font-family={SERIF}
      font-style="italic"
      font-size="32"
      fill="#5f5a52">{line}</text
    >
  {/each}

  {#if amount}
    <text
      x={CENTER}
      y={layout.paidY}
      text-anchor="middle"
      font-family={SERIF}
      font-style="italic"
      font-size="48"
      fill="#b08542">{copy.paidCash}</text
    >
  {/if}

  <line x1={CENTER - 60} y1="1188" x2={CENTER + 60} y2="1188" stroke="#b08542" stroke-opacity="0.5" stroke-width="1.5" />
  <text
    x={CENTER}
    y="1238"
    text-anchor="middle"
    font-family={BODY}
    font-weight="500"
    font-size="24"
    letter-spacing="6"
    fill="#b08542">7magicwedding</text
  >
</svg>
