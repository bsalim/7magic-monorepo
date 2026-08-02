<script lang="ts">
  import GlobeIcon from '@lucide/svelte/icons/globe';
  import { page } from '$app/state';
  import { buttonVariants } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, localizeHref, type Locale } from '$lib/paraglide/runtime';
  import { cn } from '$lib/utils';

  let { variant = 'solid' }: { variant?: 'solid' | 'overlay' } = $props();

  // Two locales, so the switcher is a straight toggle to "the other one",
  // keeping the visitor on the page they are already reading.
  let target = $derived<Locale>(getLocale() === 'id' ? 'en' : 'id');
  let href = $derived(localizeHref(page.url.pathname, { locale: target }));
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
