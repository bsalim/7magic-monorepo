<script lang="ts">
  import { enhance } from '$app/forms';

  import DateField from '$lib/components/DateField.svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as m from '$lib/paraglide/messages';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  let visitDate = $state('');
  let guests = $state(2);

  // The guest's own pick, or null while they have not touched the dropdown -- in
  // which case ?venue= from the load wins. Derived rather than state seeded by an
  // effect, for two reasons: the server render already has the venue selected
  // (state seeded on the client only selects it after hydration, so it visibly
  // flashes), and arriving at a different branch or ?venue= follows the new load
  // instead of keeping the previous page's choice.
  let venueChoice = $state<string | null>(null);
  const venueId = $derived(venueChoice ?? data.preselectedVenueId);

  const today = new Date().toISOString().slice(0, 10);

  // Grouped into <optgroup> by city. 121 venues is far too many for a flat list,
  // and city is how a couple actually narrows it down.
  const venuesByCity = $derived(
    data.venues.reduce<Record<string, typeof data.venues>>((groups, venue) => {
      (groups[venue.city] ??= []).push(venue);
      return groups;
    }, {})
  );

  const cityLabel = (city: string) => city.charAt(0).toUpperCase() + city.slice(1);

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
  <!-- No branch address: the visit happens at the venue the guest picks below, so
       showing head office's street would point them at the wrong place. -->
  <h1 class="text-3xl font-semibold">{data.branch.name}</h1>

  {#if data.settings.tour_intro_html}
    <!-- Sanitized on write by the API's allowlist; see core/html.py -->
    <div class="prose mt-4">{@html data.settings.tour_intro_html}</div>
  {/if}

  {#if form?.ok}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_success()}</p>
  {:else if !data.event || !data.event.registration_open}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_closed()}</p>
  {:else}
    {#if errorMessage}
      <p class="mt-6 text-sm text-destructive">{errorMessage}</p>
    {/if}

    <form method="POST" use:enhance class="mt-8 grid gap-4 sm:grid-cols-2">
      <div class="grid gap-2 sm:col-span-2">
        <Label for="venue_id">{m.tour_field_venue()}</Label>
        <select
          id="venue_id"
          name="venue_id"
          value={venueId}
          onchange={(event) => (venueChoice = event.currentTarget.value)}
          required
          class="h-10 rounded-lg border border-border/60 bg-background px-3 text-sm"
        >
          <option value="">{m.tour_field_venue_choose()}</option>
          {#each Object.entries(venuesByCity) as [city, venues] (city)}
            <optgroup label={cityLabel(city)}>
              {#each venues as venue (venue.id)}
                <option value={String(venue.id)}>{venue.name}</option>
              {/each}
            </optgroup>
          {/each}
        </select>
      </div>

      <div class="grid gap-2">
        <Label for="name">{m.tour_field_name()}</Label>
        <Input id="name" name="name" required />
      </div>
      <div class="grid gap-2">
        <Label for="email">{m.tour_field_email()}</Label>
        <Input id="email" name="email" type="email" required />
      </div>
      <div class="grid gap-2">
        <Label for="mobile">{m.tour_field_mobile()}</Label>
        <Input id="mobile" name="mobile" />
      </div>
      <div class="grid gap-2">
        <Label for="visit_date">{m.tour_field_date()}</Label>
        <!-- Any future day, no slots: the team confirms a time when they follow up,
             so there is nothing here to grey out. -->
        <DateField name="visit_date" bind:value={visitDate} min={today} />
      </div>
      <div class="grid gap-2">
        <Label for="party_size">{m.tour_field_guests_total()}</Label>
        <Input
          id="party_size"
          name="party_size"
          type="number"
          min="1"
          max="20"
          bind:value={guests}
        />
        <p class="text-xs text-muted-foreground">{m.tour_guests_hint()}</p>
      </div>

      <div class="sm:col-span-2">
        <Button type="submit" disabled={!venueId || !visitDate}>{m.tour_submit()}</Button>
      </div>
    </form>

    {#if data.settings.arrival_instructions || data.settings.parking_notes}
      <div class="mt-10 grid gap-2 text-sm text-muted-foreground">
        {#if data.settings.arrival_instructions}<p>{data.settings.arrival_instructions}</p>{/if}
        {#if data.settings.parking_notes}<p>{data.settings.parking_notes}</p>{/if}
      </div>
    {/if}
  {/if}
</main>

<PublicFooter />
