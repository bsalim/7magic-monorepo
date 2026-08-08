<script lang="ts">
  import GlobeIcon from '@lucide/svelte/icons/globe';
  import { page } from '$app/state';
  import { buttonVariants } from '$lib/components/ui/button';
  import { switcherHref } from '$lib/locale-href';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, type Locale } from '$lib/paraglide/runtime';
  import { cn } from '$lib/utils';

  let { variant = 'solid' }: { variant?: 'solid' | 'overlay' } = $props();

  // Two locales, so the switcher is a straight toggle to "the other one",
  // keeping the visitor on the page they are already reading -- on the article
  // it translates to, not on the structurally-localized path that merely
  // redirects there.
  let target = $derived<Locale>(getLocale() === 'id' ? 'en' : 'id');
  let alternates = $derived(page.data.alternates as Record<string, string> | undefined);
  let href = $derived(switcherHref(page.url.pathname, target, alternates));
</script>

<!-- data-sveltekit-reload forces a full navigation: messages are resolved per
     request, so a client-side transition would keep the old locale's copy. -->
<a
  {href}
  hreflang={target}
  data-sveltekit-reload
  class={cn(
    buttonVariants({ variant: 'ghost', size: 'sm' }),
    'gap-2 font-medium',
    variant === 'overlay' ? 'text-white/90 hover:bg-white/10 hover:text-white' : ''
  )}
>
  <GlobeIcon size={16} />
  {m.language_switch()}
</a>
