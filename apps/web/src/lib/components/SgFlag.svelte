<script lang="ts">
  let { class: className = '' }: { class?: string } = $props();
</script>

<!-- Inline SVG, not the 🇸🇬 emoji: Windows ships no flag glyphs and renders
     the emoji as the letters "SG". Simplified for icon size, so the stars are dots. -->
<svg viewBox="0 0 30 20" class={className} aria-hidden="true">
  <rect width="30" height="10" fill="#ef3340" />
  <rect y="10" width="30" height="10" fill="#fff" />
  <circle cx="7" cy="5" r="3.6" fill="#fff" />
  <circle cx="8.4" cy="5" r="3.4" fill="#ef3340" />
  <g fill="#fff">
    <circle cx="11" cy="3.2" r="0.7" />
    <circle cx="12.7" cy="4.4" r="0.7" />
    <circle cx="12.1" cy="6.4" r="0.7" />
    <circle cx="9.9" cy="6.4" r="0.7" />
    <circle cx="9.3" cy="4.4" r="0.7" />
  </g>
  <!-- Hairline edge, so the white half does not vanish into a white header. -->
  <rect width="30" height="20" fill="none" stroke="#0000001f" />
</svg>
