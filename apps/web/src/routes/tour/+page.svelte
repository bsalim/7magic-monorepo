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
  <title>{m.tour_meta_title()}</title>
  <meta name="description" content={m.tour_meta_description()} />
</svelte:head>

<PublicHeader />

<main class="mx-auto w-full max-w-3xl px-4 py-12">
  <!-- No branch picker: the tour visits the venue, so which office handles the
       booking is our problem to solve, not a question to put to the guest. -->
  <h1 class="text-3xl font-semibold">{m.tour_title()}</h1>

  <TourPitch venueName={data.lockedVenue?.name ?? null} />

  {#if form?.ok}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_success()}</p>
  {:else if !data.open}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_closed()}</p>
  {:else}
    {#if errorMessage}
      <p class="mt-6 text-sm text-destructive">{errorMessage}</p>
    {/if}

    <TourForm
      venues={data.venues}
      cities={data.cities}
      lockedVenue={data.lockedVenue}
      changeVenueHref={data.lockedVenue ? localizeHref('/tour') : null}
    />
  {/if}
</main>

<PublicFooter />
