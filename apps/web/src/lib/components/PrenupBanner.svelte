<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import * as Card from '$lib/components/ui/card';
  import { buttonVariants } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { localizeHref } from '$lib/paraglide/runtime';
  import { cn } from '$lib/utils';

  // The price comes from `service_prenup_desc`, the same message the services
  // menu uses, so a price change stays one edit per locale rather than one more
  // hardcoded copy to hunt down.
</script>

<Card.Root class="gap-0 overflow-hidden py-0 shadow-sm">
  <img src="/img/prenup/couple-signing.jpg" alt="" class="h-40 w-full object-cover" loading="lazy" />
  <Card.Content class="p-5">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      {m.prenup_banner_eyebrow()}
    </p>
    <h2 class="mt-2 text-2xl font-semibold">{m.service_prenup()}</h2>
    <p class="mt-1 text-sm font-semibold text-slate-900">{m.service_prenup_desc()}</p>
    <p class="mt-3 text-sm leading-6 text-muted-foreground">{m.prenup_banner_body()}</p>
    <a
      href={localizeHref('/perjanjian-pranikah')}
      class={cn(buttonVariants(), 'mt-5 h-auto w-full py-3 font-semibold')}
    >
      {m.prenup_banner_cta()}
      <ArrowRightIcon size={18} />
    </a>
  </Card.Content>
</Card.Root>
