<script lang="ts" module>
  /** One per card on the Wedding Tools hub, live or announced. */
  export type ToolIconName =
    | 'mahar'
    | 'hashtag'
    | 'bazi'
    | 'bali-cost'
    | 'bali-dates'
    | 'weton'
    | 'tionghoa'
    | 'budget';
</script>

<script lang="ts">
  /**
   * The wedding tools' own icon set: one drawing per tool, on a cream halo.
   *
   * Inline SVG from the owner's design, not an icon font or image files, so the
   * hub and the home page draw the same mark at any size with nothing to load.
   * The dark strokes are `currentColor` and follow the text colour of whatever
   * holds the icon; the golds and the halo are the set's own and are fixed.
   * Decorative everywhere it is used: the card's title names the tool.
   */

  interface Props {
    tool: ToolIconName;
    /** Rendered width and height in pixels. */
    size?: number;
    class?: string;
  }

  let { tool, size = 64, class: className = '' }: Props = $props();
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 64 64"
  width={size}
  height={size}
  fill="none"
  aria-hidden="true"
  class={className}
>
  <circle cx="32" cy="32" r="29" fill="#F6EEDC" />
  {#if tool === 'mahar'}
    <rect x="11" y="14" width="33" height="31" rx="6" stroke="currentColor" stroke-width="3" />
    <path d="M11 24h33" stroke="currentColor" stroke-width="3" />
    <path d="M19 10v6M36 10v6" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
    <path
      d="M24.5 38.5c-3.2-2.8-5.5-4.6-5.5-7 0-1.9 1.5-3.4 3.4-3.4 1.1 0 2.1.6 2.8 1.5.7-.9 1.7-1.5 2.8-1.5 1.9 0 3.4 1.5 3.4 3.4 0 2.4-2.3 4.2-5.5 7l-.7.6-.7-.6z"
      fill="#B98A2F"
    />
    <circle cx="44" cy="43" r="12.5" fill="#E9C46A" stroke="#8A6420" stroke-width="3" />
    <circle cx="44" cy="43" r="7.5" stroke="#8A6420" stroke-width="2.4" />
    <path
      d="M44 39.4l1.15 2.3 2.55.4-1.85 1.8.45 2.55-2.3-1.2-2.3 1.2.45-2.55-1.85-1.8 2.55-.4z"
      fill="#8A6420"
    />
    <path d="M51 8l1.4 3.4 3.4 1.4-3.4 1.4-1.4 3.4-1.4-3.4-3.4-1.4 3.4-1.4z" fill="#B98A2F" />
  {:else if tool === 'hashtag'}
    <path d="M28 12l-6 40" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" />
    <path d="M42 12l-6 40" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" />
    <path d="M15 24h34" stroke="#B98A2F" stroke-width="3.6" stroke-linecap="round" />
    <path d="M13 38h23" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" />
    <circle cx="47" cy="45" r="11" fill="#E9C46A" stroke="#8A6420" stroke-width="3" />
    <path
      d="M47 49.8c-2.9-2.5-4.9-4.1-4.9-6.2 0-1.7 1.3-3 3-3 .9 0 1.7.4 2.4 1.3.7-.9 1.5-1.3 2.4-1.3 1.7 0 3 1.3 3 3 0 2.1-2 3.7-4.9 6.2z"
      fill="#8A6420"
    />
    <path d="M14 8l1.2 3 3 1.2-3 1.2-1.2 3-1.2-3-3-1.2 3-1.2z" fill="#B98A2F" />
  {:else if tool === 'bazi'}
    <circle cx="32" cy="33" r="19" stroke="currentColor" stroke-width="3" />
    <path d="M32 17v4M32 45v4M16 33h4M44 33h4" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
    <path d="M32 21l5 12-5 12-5-12z" fill="#E9C46A" stroke="#8A6420" stroke-width="2.4" stroke-linejoin="round" />
    <path d="M32 21l5 12h-10z" fill="#B98A2F" />
    <circle cx="32" cy="33" r="2.2" fill="currentColor" />
    <path d="M14.5 11.5l2.6 2.6-2.6 2.6-2.6-2.6z" fill="#B98A2F" />
    <path d="M49.5 11.5l2.6 2.6-2.6 2.6-2.6-2.6z" fill="#B98A2F" />
    <path d="M14.5 47.5l2.6 2.6-2.6 2.6-2.6-2.6z" fill="#B98A2F" />
    <path d="M49.5 47.5l2.6 2.6-2.6 2.6-2.6-2.6z" fill="#B98A2F" />
  {:else if tool === 'bali-cost'}
    <circle cx="32" cy="33" r="21" fill="#EFCB72" stroke="#8A6420" stroke-width="3" />
    <circle cx="32" cy="33" r="15" stroke="#8A6420" stroke-width="2.4" />
    <path d="M30 46c-.5-4.5 0-8.5 1.5-12.5" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" />
    <path
      d="M31.5 33.5C28 31 24.5 30.5 21.5 31.8M31.5 33.5C28.5 29.5 26 28 22.8 28.2M31.5 33.5C31 29.5 32 26.5 34 24.8M31.5 33.5C34.5 30.8 38 30.3 41 31.6M31.5 33.5C35 33.2 38 34.3 39.8 36.6"
      stroke="currentColor"
      stroke-width="2.4"
      stroke-linecap="round"
    />
    <circle cx="29.8" cy="35.4" r="1.6" fill="#8A6420" />
    <circle cx="33.2" cy="35.2" r="1.6" fill="#8A6420" />
    <path d="M26 46.5h10" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
    <path d="M51 10l1.2 3 3 1.2-3 1.2-1.2 3-1.2-3-3-1.2 3-1.2z" fill="#B98A2F" />
  {:else if tool === 'bali-dates'}
    <rect x="13" y="14" width="38" height="34" rx="6" stroke="currentColor" stroke-width="3" />
    <path d="M13 24h38" stroke="currentColor" stroke-width="3" />
    <path d="M21 10v6M43 10v6" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
    <path
      d="M21 44V36.5h3v-5h2.5v-4H29v-3h1.2V44z"
      fill="#B98A2F"
      stroke="#8A6420"
      stroke-width="1.6"
      stroke-linejoin="round"
    />
    <path
      d="M43 44V36.5h-3v-5h-2.5v-4H35v-3h-1.2V44z"
      fill="#B98A2F"
      stroke="#8A6420"
      stroke-width="1.6"
      stroke-linejoin="round"
    />
  {:else if tool === 'weton'}
    <g stroke="#B98A2F" stroke-width="2.6" stroke-linecap="round">
      <path
        d="M24 13v3.5M24 33.5V37M12 25h3.5M32.5 25H36M15.5 16.5l2.5 2.5M30 31l2.5 2.5M32.5 16.5L30 19M18 31l-2.5 2.5"
      />
    </g>
    <circle cx="24" cy="25" r="8" fill="#E9C46A" stroke="#B98A2F" stroke-width="2.6" />
    <path d="M44 27a11 11 0 1 0 0 22 13.5 13.5 0 0 1 0-22z" fill="currentColor" />
    <path
      d="M33.5 38.5c-2.9-2.5-5-4.2-5-6.3 0-1.8 1.4-3.1 3.1-3.1 1 0 1.9.5 2.4 1.4.6-.9 1.5-1.4 2.4-1.4 1.8 0 3.1 1.4 3.1 3.1 0 2.1-2.1 3.8-5 6.3l-.5.4-.5-.4z"
      fill="#B98A2F"
    />
  {:else if tool === 'tionghoa'}
    <path d="M32 7v4" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" />
    <rect x="26" y="11" width="12" height="5" rx="2" fill="#B98A2F" />
    <path
      d="M20 29c0-7 5.4-12 12-12s12 5 12 12-5.4 12-12 12-12-5-12-12z"
      fill="#EFCB72"
      stroke="#8A6420"
      stroke-width="2.6"
    />
    <path
      d="M32 17v24M25.5 18.2c-2 3.4-2 18.2 0 21.6M38.5 18.2c2 3.4 2 18.2 0 21.6"
      stroke="#8A6420"
      stroke-width="2"
      stroke-linecap="round"
    />
    <rect x="26" y="40" width="12" height="5" rx="2" fill="#B98A2F" />
    <path d="M32 45v5M28.5 45v4M35.5 45v4" stroke="#B98A2F" stroke-width="2.2" stroke-linecap="round" />
    <circle cx="32" cy="52.5" r="1.8" fill="#B98A2F" />
    <path d="M12 18l1.2 3 3 1.2-3 1.2-1.2 3-1.2-3-3-1.2 3-1.2z" fill="#B98A2F" />
    <path d="M52 18l1.2 3 3 1.2-3 1.2-1.2 3-1.2-3-3-1.2 3-1.2z" fill="#B98A2F" />
  {:else if tool === 'budget'}
    <circle cx="39" cy="22" r="5" stroke="#B98A2F" stroke-width="3" />
    <path d="M32 38c0-5.5 3.2-9 7-9s7 3.5 7 9" stroke="#B98A2F" stroke-width="3" stroke-linecap="round" />
    <circle cx="24" cy="25" r="6.5" stroke="currentColor" stroke-width="3" />
    <path d="M12 47c0-7.5 5.4-12 12-12s12 4.5 12 12" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
    <circle cx="47" cy="46" r="11" fill="#E9C46A" stroke="#8A6420" stroke-width="3" />
    <path
      d="M47 41v10M50 43.2c0-1.6-1.4-2.4-3-2.4s-3 .9-3 2.3c0 3.4 6 1.8 6 5.2 0 1.5-1.4 2.4-3 2.4s-3-.9-3-2.4"
      stroke="#8A6420"
      stroke-width="2.2"
      stroke-linecap="round"
    />
  {/if}
</svg>
