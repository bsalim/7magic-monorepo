<script lang="ts">
  import CameraIcon from '@lucide/svelte/icons/camera';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import * as Card from '$lib/components/ui/card';
  import { m } from '$lib/paraglide/messages.js';
  import { buttonVariants } from '$lib/components/ui/button';
  import type { VenueDetail } from '$lib/api';
  import { cn } from '$lib/utils';
  import { whatsappHref } from '$lib/whatsapp';

  let { venue }: { venue?: VenueDetail } = $props();

  const href = $derived(
    whatsappHref(
      venue
        ? `Hi 7Magic, I want to ask about ${venue.name} wedding packages.`
        : 'Hi 7Magic, I want to ask about wedding venue packages.'
    )
  );
</script>

<Card.Root class="gap-0 py-0 shadow-sm">
  <Card.Content class="p-5">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">{m.cta_eyebrow()}</p>
    <h2 class="mt-2 text-2xl font-semibold">{m.cta_heading()}</h2>
    <p class="mt-3 text-sm leading-6 text-muted-foreground">
      {m.cta_body()}
    </p>
    <div class="mt-5 grid gap-3">
      <a
        {href}
        class={cn(
          buttonVariants(),
          'h-auto bg-brand-success py-3 font-semibold text-white hover:bg-brand-success-hover'
        )}
      >
        <MessageCircleIcon size={18} />
        {m.cta_whatsapp()}
      </a>
      <a
        href="https://www.instagram.com/7magicwedding"
        class={cn(
          buttonVariants({ variant: 'outline' }),
          'h-auto py-3 font-semibold text-accent-foreground'
        )}
      >
        <CameraIcon size={18} />
        {m.cta_instagram()}
      </a>
    </div>
  </Card.Content>
</Card.Root>
