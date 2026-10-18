<script module lang="ts">
  export type HashtagCardCopy = {
    fallbackTitle: string;
    kicker: string;
    invite: string;
    emptyTag: string;
  };
</script>

<script lang="ts">
  import { downloadBlob, printCard, svgToPng } from '$lib/tools/card-export';

  /**
   * The hashtag sign: a 4:5 portrait SVG, 1080 x 1350, in the mahar card's
   * cream and gold so the two read as one set.
   *
   * It doubles as an Instagram post announcing the tag and, printed at A5, as
   * the sign on the guest-book table, which is where most guests first see a
   * couple's hashtag. The tag is the largest thing on it for that reason: it has
   * to be legible from a step away.
   */

  interface Props {
    names: string;
    /** "Minggu, 20 September 2026", or empty without a date. */
    dateLine: string;
    /** With the "#", or empty while there are no names. */
    tag: string;
    copy: HashtagCardCopy;
    /** Accessible summary of the card, read instead of the SVG's text runs. */
    label: string;
    class?: string;
  }

  let { names, dateLine, tag, copy, label, class: className }: Props = $props();

  const WIDTH = 1080;
  const HEIGHT = 1350;
  const CENTER = WIDTH / 2;
  const MEASURE = 840;

  const SERIF = "Georgia, 'Times New Roman', serif";
  const DISPLAY = 'Poppins, ui-sans-serif, system-ui, sans-serif';
  const BODY = "'Jost Variable', Jost, ui-sans-serif, system-ui, sans-serif";

  let svg = $state<SVGSVGElement>();

  // Same estimate as the mahar card: average advance per character as a share
  // of the font size, since SVG text cannot be measured during SSR.
  const fit = (text: string, max: number, advance: number) =>
    Math.min(max, Math.floor(MEASURE / Math.max(1, text.length * advance)));

  /**
   * A long tag on two lines, broken at the word capital nearest the middle
   * (#RakaNadia / Wedding2026), so no word is cut and the type stays large.
   */
  function tagLines(text: string): string[] {
    if (text.length <= 16) return [text];
    const middle = text.length / 2;
    let best = -1;
    for (let index = 2; index < text.length - 1; index++) {
      const boundary = /[A-Z0-9]/.test(text[index]) && !/[0-9]/.test(text[index - 1]);
      if (boundary && (best < 0 || Math.abs(index - middle) < Math.abs(best - middle))) best = index;
    }
    return best < 0 ? [text] : [text.slice(0, best), text.slice(best)];
  }

  const title = $derived(names.trim() || copy.fallbackTitle);
  const titleSize = $derived(fit(title, 92, 0.5));
  const tagText = $derived(tag || copy.emptyTag);
  const lines = $derived(tagLines(tagText));
  const tagSize = $derived(
    fit(
      lines.reduce((a, b) => (b.length > a.length ? b : a), ''),
      lines.length > 1 ? 112 : 128,
      0.6
    )
  );
  // One line sits centred on 900; two lines hang from just under the invite
  // line (cap height is about 0.75 of the size), so the first never rides up
  // into it and the second stays clear of the foot.
  const tagY = $derived(lines.length > 1 ? 834 + tagSize * 0.75 : 900 + tagSize * 0.3);

  function fileName(): string {
    const slug = tag.replace(/^#/, '').toLowerCase().replace(/[^a-z0-9]+/g, '');
    return `hashtag-${slug || 'pernikahan'}.png`;
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
    <radialGradient id="hashtag-card-glow" cx="50%" cy="22%" r="80%">
      <stop offset="0%" stop-color="#fffdf8" />
      <stop offset="70%" stop-color="#fbf7f0" />
      <stop offset="100%" stop-color="#f2e4cc" />
    </radialGradient>
    <linearGradient id="hashtag-card-gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#d4b27f" />
      <stop offset="50%" stop-color="#b08542" />
      <stop offset="100%" stop-color="#8a6524" />
    </linearGradient>
  </defs>

  <rect width={WIDTH} height={HEIGHT} fill="url(#hashtag-card-glow)" />
  <rect x="44" y="44" width="992" height="1262" rx="30" fill="none" stroke="url(#hashtag-card-gold)" stroke-width="3" />
  <rect x="66" y="66" width="948" height="1218" rx="20" fill="none" stroke="#b08542" stroke-opacity="0.45" stroke-width="1.5" />

  {#each [[66, 66, 0], [1014, 66, 90], [1014, 1284, 180], [66, 1284, 270]] as [x, y, angle] (angle)}
    <g transform="translate({x} {y}) rotate({angle})" fill="#b08542" fill-opacity="0.7">
      <path d="M18 18 C 38 22, 52 36, 56 56 C 36 52, 22 38, 18 18 Z" />
      <circle cx="16" cy="16" r="4" />
    </g>
  {/each}

  <g transform="translate({CENTER} 196)">
    <line x1="-150" y1="0" x2="-30" y2="0" stroke="#b08542" stroke-width="2" />
    <line x1="30" y1="0" x2="150" y2="0" stroke="#b08542" stroke-width="2" />
    <path d="M0 -18 L18 0 L0 18 L-18 0 Z" fill="url(#hashtag-card-gold)" />
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

  <text x={CENTER} y="410" text-anchor="middle" font-family={SERIF} font-style="italic" font-size={titleSize} fill="#141414"
    >{title}</text
  >

  <g transform="translate({CENTER} 478)">
    <line x1="-90" y1="0" x2="-14" y2="0" stroke="#b08542" stroke-opacity="0.7" stroke-width="1.5" />
    <line x1="14" y1="0" x2="90" y2="0" stroke="#b08542" stroke-opacity="0.7" stroke-width="1.5" />
    <circle r="5" fill="#b08542" />
  </g>

  {#if dateLine}
    <text x={CENTER} y="562" text-anchor="middle" font-family={BODY} font-size="38" fill="#3a3a3a">{dateLine}</text>
  {/if}

  <!-- A camera outline: the sign's one hint that this is about photos. -->
  <g transform="translate({CENTER} 690)" fill="none" stroke="#b08542" stroke-width="4">
    <rect x="-34" y="-34" width="68" height="68" rx="20" />
    <circle r="16" />
    <circle cx="20" cy="-20" r="3" fill="#b08542" stroke="none" />
  </g>

  <text x={CENTER} y="782" text-anchor="middle" font-family={SERIF} font-style="italic" font-size="38" fill="#5f5a52"
    >{copy.invite}</text
  >

  {#each lines as line, index (index)}
    <text
      x={CENTER}
      y={tagY + index * tagSize * 1.08}
      text-anchor="middle"
      font-family={DISPLAY}
      font-weight="600"
      font-size={tagSize}
      letter-spacing="-1"
      fill={tag ? '#8a6524' : '#a39a8c'}>{line}</text
    >
  {/each}

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
