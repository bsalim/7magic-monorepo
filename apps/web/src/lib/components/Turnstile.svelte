<script lang="ts" module>
  type TurnstileApi = {
    render: (el: HTMLElement, options: Record<string, unknown>) => string;
    reset: (id: string) => void;
    remove: (id: string) => void;
  };

  declare global {
    interface Window {
      turnstile?: TurnstileApi;
    }
  }

  const SCRIPT_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';

  // One load per page, shared by every widget: client-side navigation between the
  // two tour pages would otherwise append the script again on each mount.
  let loading: Promise<TurnstileApi> | null = null;

  function loadTurnstile(): Promise<TurnstileApi> {
    if (window.turnstile) return Promise.resolve(window.turnstile);
    loading ??= new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = SCRIPT_SRC;
      script.async = true;
      script.onload = () => (window.turnstile ? resolve(window.turnstile) : reject());
      script.onerror = () => {
        loading = null;
        reject(new Error('turnstile script failed to load'));
      };
      document.head.appendChild(script);
    });
    return loading;
  }
</script>

<script lang="ts">
  import { onMount } from 'svelte';

  import { env } from '$env/dynamic/public';
  import { getLocale } from '$lib/paraglide/runtime';

  /**
   * Cloudflare Turnstile. Renders nothing while PUBLIC_TURNSTILE_SITE_KEY is
   * unset, matching the server, which skips verification without its secret.
   *
   * The widget puts its token in a hidden `cf-turnstile-response` input inside
   * the container, so a plain form POST carries it with no wiring here. `token`
   * is bound out only so the form can hold the submit button until it exists.
   */
  let { token = $bindable('') }: { token?: string } = $props();

  const siteKey = env.PUBLIC_TURNSTILE_SITE_KEY;

  let container = $state<HTMLDivElement | null>(null);
  let widgetId: string | null = null;

  /** Tokens are single-use: call after every submission, accepted or not. */
  export function reset() {
    token = '';
    if (widgetId && window.turnstile) window.turnstile.reset(widgetId);
  }

  onMount(() => {
    if (!siteKey || !container) return;
    let cancelled = false;

    loadTurnstile()
      .then((api) => {
        if (cancelled || !container) return;
        widgetId = api.render(container, {
          sitekey: siteKey,
          language: getLocale(),
          callback: (value: string) => (token = value),
          'expired-callback': () => (token = ''),
          'error-callback': () => {
            token = '';
          }
        });
      })
      .catch((err) => console.error('[turnstile]', err));

    return () => {
      cancelled = true;
      if (widgetId && window.turnstile) window.turnstile.remove(widgetId);
      widgetId = null;
    };
  });
</script>

{#if siteKey}
  <div bind:this={container}></div>
{/if}
