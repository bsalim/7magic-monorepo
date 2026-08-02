<script lang="ts">
  import { onMount } from 'svelte';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';
  import { m } from '$lib/paraglide/messages.js';
  import { dismissalCookie, shouldShow } from '$lib/promotion-cookie';

  type Promotion = {
    version: string;
    title: string;
    body: string;
    banner_url: string | null;
    cta_label: string | null;
    cta_url: string | null;
    frequency: 'daily' | 'weekly' | 'once';
  };

  let { promotion }: { promotion: Promotion | null } = $props();

  let open = $state(false);
  // The dismissal effect must not fire on the initial render, when `open` is
  // still false — that would write the cookie before onMount ever reads it, and
  // the popup would mark itself dismissed without being shown.
  let hasOpened = $state(false);

  onMount(() => {
    if (!promotion) return;
    // Read the cookie on the client only — deciding this during SSR would bake
    // one visitor's dismissal state into a cached page.
    if (shouldShow(promotion.version, document.cookie)) {
      open = true;
    }
  });

  // Recorded on close rather than on open, so a visitor who never actually sees
  // it is not counted as having dismissed it. Covers Escape and overlay clicks,
  // which bypass the buttons.
  $effect(() => {
    if (open) {
      hasOpened = true;
      return;
    }
    if (hasOpened && promotion) {
      document.cookie = dismissalCookie(promotion.version, promotion.frequency);
    }
  });
</script>

{#if promotion}
  <Dialog.Root bind:open>
    <Dialog.Content class="max-w-md overflow-hidden p-0">
      {#if promotion.banner_url}
        <img
          src={promotion.banner_url}
          alt=""
          class="max-h-64 w-full object-cover"
          loading="lazy"
          decoding="async"
        />
      {/if}

      <div class="grid gap-3 p-6">
        <Dialog.Header>
          <Dialog.Title class="font-display text-xl font-bold">{promotion.title}</Dialog.Title>
          {#if promotion.body}
            <Dialog.Description class="whitespace-pre-line text-[15px] leading-relaxed">
              {promotion.body}
            </Dialog.Description>
          {/if}
        </Dialog.Header>

        {#if promotion.cta_url}
          <a
            href={promotion.cta_url}
            class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'mt-1 w-full')}
            onclick={() => (open = false)}
          >
            {promotion.cta_label || m.promo_default_cta()}
          </a>
        {/if}

        <Button variant="ghost" class="w-full" onclick={() => (open = false)}>
          {m.promo_dismiss()}
        </Button>
      </div>
    </Dialog.Content>
  </Dialog.Root>
{/if}
