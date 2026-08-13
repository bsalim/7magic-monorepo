<script lang="ts">
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import TourForm from '$lib/components/TourForm.svelte';
  import TourPitch from '$lib/components/TourPitch.svelte';
  import * as m from '$lib/paraglide/messages';
  import { localizeHref } from '$lib/paraglide/runtime';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const ERROR_MESSAGES: Record<string, () => string> = {
    already_registered: m.tour_error_already,
    event_full: m.tour_error_full
  };

  const errorMessage = $derived(
    form && form.ok === false ? (ERROR_MESSAGES[form.code] ?? m.tour_error_generic)() : ''
  );
</script>

<svelte:head>
  <title>{`${m.tour_title()} · ${data.branch.name}`}</title>
  <meta name="description" content={m.tour_meta_description()} />
</svelte:head>

<PublicHeader />

<main class="mx-auto w-full max-w-3xl px-4 py-12">
  <!-- No branch address: the visit happens at the venue the guest names below, so
       showing head office's street would point them at the wrong place. -->
  <h1 class="text-3xl font-semibold">{data.branch.name}</h1>

  {#if data.settings.tour_intro_html}
    <!-- A branch that wrote its own pitch replaces the default one rather than
         stacking a second one under it. Sanitized on write; see core/html.py. -->
    <div class="prose mt-4">{@html data.settings.tour_intro_html}</div>
  {:else}
    <TourPitch venueName={data.lockedVenue?.name ?? null} />
  {/if}

  {#if form?.ok}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_success()}</p>
  {:else if !data.event || !data.event.registration_open}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_closed()}</p>
  {:else}
    {#if errorMessage}
      <p class="mt-6 text-sm text-destructive">{errorMessage}</p>
    {/if}

    <TourForm
      venues={data.venues}
      cities={data.cities}
      lockedVenue={data.lockedVenue}
      changeVenueHref={data.lockedVenue ? localizeHref(`/tour/${data.branch.slug}`) : null}
    />
  {/if}

  {#if data.settings.arrival_instructions || data.settings.parking_notes}
    <div class="mt-10 grid gap-2 text-sm text-muted-foreground">
      {#if data.settings.arrival_instructions}<p>{data.settings.arrival_instructions}</p>{/if}
      {#if data.settings.parking_notes}<p>{data.settings.parking_notes}</p>{/if}
    </div>
  {/if}
</main>

<PublicFooter />
