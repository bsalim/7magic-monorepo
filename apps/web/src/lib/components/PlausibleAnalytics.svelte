<script lang="ts">
  import { env } from '$env/dynamic/public';

  /**
   * Plausible analytics.
   *
   * The script URL carries the site id, so it is both the only thing to
   * configure and the on/off switch: nothing renders unless
   * PUBLIC_PLAUSIBLE_SRC is set, which keeps local and staging traffic out of
   * production stats. It ends up in the page the browser receives, so it has
   * to be a PUBLIC_ variable -- there is nothing to keep secret. Read through
   * $env/dynamic/public rather than import.meta.env, which does not carry
   * PUBLIC_-prefixed vars.
   *
   * SvelteKit navigates with pushState and Plausible hooks the History API
   * itself, so client-side navigations are counted without extra wiring.
   */
  const src = $derived(env.PUBLIC_PLAUSIBLE_SRC);

  // Plausible's own bootstrap, verbatim: it queues plausible() calls made
  // before the async script lands, then starts tracking. Injected as a string
  // because Svelte would otherwise read the braces in these function bodies as
  // template expressions. SSR writes it into the served HTML, so it runs on
  // load rather than waiting for hydration.
  const BOOTSTRAP =
    'window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},' +
    'plausible.init=plausible.init||function(i){plausible.o=i||{}};' +
    'plausible.init()';
</script>

<svelte:head>
  {#if src}
    <script async {src}></script>
    {@html `<script>${BOOTSTRAP}</script>`}
  {/if}
</svelte:head>
