<script lang="ts">
  import { env } from '$env/dynamic/public';

  /**
   * Google Analytics (gtag.js).
   *
   * The measurement id is both the only thing to configure and the on/off
   * switch: nothing renders unless PUBLIC_GA_MEASUREMENT_ID is set, which
   * keeps local and staging traffic out of production stats. It ends up in
   * the page the browser receives, so it has to be a PUBLIC_ variable --
   * there is nothing to keep secret. Read through $env/dynamic/public rather
   * than import.meta.env, which does not carry PUBLIC_-prefixed vars.
   */
  const id = $derived(env.PUBLIC_GA_MEASUREMENT_ID);
</script>

<svelte:head>
  {#if id}
    <script async src={`https://www.googletagmanager.com/gtag/js?id=${id}`}></script>
    {@html `<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${id}');</script>`}
  {/if}
</svelte:head>
