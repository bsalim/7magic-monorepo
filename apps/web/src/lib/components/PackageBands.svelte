<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import { buttonVariants } from '$lib/components/ui/button';
  import type { VenuePriceBands } from '$lib/api';
  import { m } from '$lib/paraglide/messages.js';
  import { cn, formatMillions } from '$lib/utils';
  import { whatsappHref } from '$lib/whatsapp';
  import { localizeHref } from '$lib/paraglide/runtime';

  let {
    priceBands,
    totalVenues
  }: {
    priceBands: VenuePriceBands;
    totalVenues: number;
  } = $props();

  // Bound to the active locale so English readers see "million", not "juta".
  const money = (value: number) => formatMillions(value, m.currency_millions_unit());

  function bandLabel(band: VenuePriceBands['bands'][number]) {
    if (band.max_price === null) return m.packages_band_over({ min: money(band.min_price) });
    if (band.min_price === 0) return m.packages_band_under({ max: money(band.max_price) });
    return m.packages_band_between({
      min: money(band.min_price),
      max: money(band.max_price)
    });
  }

  // Pre-filling the budget means the first reply can quote a real shortlist
  // instead of asking "berapa budget-nya?" and losing a message round-trip.
  function bandHref(band: VenuePriceBands['bands'][number]) {
    return whatsappHref(
      `${m.packages_wa_intro()} ${m.packages_wa_budget({ band: bandLabel(band) })}.`
    );
  }

  // Only advertise bands that actually have venues behind them.
  const visibleBands = $derived(priceBands.bands.filter((band) => band.count > 0));
</script>

<section class="bg-white py-14">
  <div class="mx-auto max-w-7xl px-5 lg:px-8">
    <div class="mx-auto max-w-3xl text-center">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {m.packages_eyebrow()}
      </p>

      {#if priceBands.floor}
        <h2 class="mt-3 text-3xl font-semibold md:text-4xl">
          {m.packages_headline({ floor: money(priceBands.floor) })}
        </h2>
      {/if}

      <p class="mt-4 leading-7 text-muted-foreground">
        {m.packages_sub({ venues: totalVenues })}
      </p>
    </div>

    {#if visibleBands.length}
      <div class="mx-auto mt-9 grid max-w-4xl gap-4 sm:grid-cols-3">
        {#each visibleBands as band (band.label)}
          <a
            href={bandHref(band)}
            class="group flex flex-col items-center rounded-md border border-border bg-background px-4 py-5 text-center transition hover:border-primary hover:bg-white hover:shadow-sm"
          >
            <span class="text-base font-semibold">{bandLabel(band)}</span>
            <span class="mt-1 text-sm text-muted-foreground">
              {m.packages_band_count({ count: band.count })}
            </span>
          </a>
        {/each}
      </div>
    {/if}

    <div class="mt-9 flex flex-col items-center">
      <a
        href={whatsappHref(`${m.packages_wa_intro()}.`)}
        class={cn(
          buttonVariants({ size: 'lg' }),
          'h-auto bg-brand-success px-7 py-3.5 text-base font-semibold text-white hover:bg-brand-success-hover'
        )}
      >
        <MessageCircleIcon size={20} />
        {m.packages_wa_cta()}
      </a>

      <p class="mt-4 text-sm text-muted-foreground">{m.packages_trust()}</p>

      <a
        href={localizeHref('/artikel')}
        class="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-accent-foreground"
      >
        {m.packages_read_guides()}
        <ArrowRightIcon size={16} />
      </a>
    </div>
  </div>
</section>
