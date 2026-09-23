<script lang="ts">
  let { class: className = '' }: { class?: string } = $props();
</script>

<!-- Candi bentar, the split gate at the entrance to Uluwatu and most Balinese
     temples. Lucide has no temple glyph, so this is drawn to its grid (24px,
     round joins, currentColor) to sit with the other nav icons. -->
<svg
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.75"
  stroke-linecap="round"
  stroke-linejoin="round"
  class={className}
  aria-hidden="true"
>
  <path d="M2.5 21v-5h2v-5h1.75V6H8V3h2v18" />
  <path d="M21.5 21v-5h-2v-5h-1.75V6H16V3h-2v18" />
  <path d="M2 21h20" />
</svg>
