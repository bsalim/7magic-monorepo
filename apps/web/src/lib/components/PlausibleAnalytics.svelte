<script lang="ts">
  import { env } from '$env/dynamic/public';

  /**
   * Plausible analytics.
   *
   * The domain is rendered into the page the browser receives, so it has to be
   * a PUBLIC_ variable -- there is nothing to keep secret here. Read through
   * $env/dynamic/public rather than import.meta.env, which does not carry
   * PUBLIC_-prefixed vars.
   *
   * Nothing renders unless PUBLIC_PLAUSIBLE_DOMAIN is set, so local and preview
   * traffic never reaches production stats. SvelteKit navigates with pushState
   * and Plausible's default script hooks the History API itself, so
   * client-side navigations are counted without extra wiring.
   */
  const domain = $derived(env.PUBLIC_PLAUSIBLE_DOMAIN);
  // Override for self-hosted Plausible or a proxied script path.
  const src = $derived(env.PUBLIC_PLAUSIBLE_SRC || 'https://plausible.io/js/script.js');
</script>

<svelte:head>
  {#if domain}
    <script defer data-domain={domain} {src}></script>
  {/if}
</svelte:head>
