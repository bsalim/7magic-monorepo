<script lang="ts">
  import { enhance } from '$app/forms';

  import DateField from '$lib/components/DateField.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as m from '$lib/paraglide/messages';
  // Imported, never redeclared: `export type` is invalid in a Svelte instance
  // script, and $lib/tour is where the wire shape already lives.
  import type { TourVenue } from '$lib/tour';

  let {
    venues,
    cities,
    lockedVenue = null,
    changeVenueHref = null
  }: {
    venues: TourVenue[];
    cities: string[];
    /** Set when the guest arrived from a venue page, so the form does not ask. */
    lockedVenue?: TourVenue | null;
    /** Clears ?venue= and reveals the fields. Null when there is nothing to clear. */
    changeVenueHref?: string | null;
  } = $props();

  let venueName = $state('');
  let city = $state('');
  let visitDate = $state('');
  let guests = $state(2);

  // The id only survives while the typed name still matches the suggestion it came
  // from. Editing the text after picking means the guest meant something else, and
  // silently keeping the old FK would book the wrong venue.
  const matched = $derived(
    venues.find((venue) => venue.name.toLowerCase() === venueName.trim().toLowerCase()) ?? null
  );

  // A matched venue knows its own city, so the dropdown stops being a question.
  const effectiveCity = $derived(matched?.city ?? city);

  const today = new Date().toISOString().slice(0, 10);

  const canSubmit = $derived(
    Boolean(visitDate) && (lockedVenue ? true : Boolean(venueName.trim()) && Boolean(effectiveCity))
  );

  const cityLabel = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);
</script>

<form method="POST" use:enhance class="mt-8 grid gap-4 sm:grid-cols-2">
  {#if lockedVenue}
    <input type="hidden" name="venue_id" value={lockedVenue.id} />
    <input type="hidden" name="venue_name" value={lockedVenue.name} />
    <input type="hidden" name="city" value={lockedVenue.city} />
    <div
      class="flex flex-wrap items-center gap-3 rounded-xl border border-border/60 p-4 sm:col-span-2"
    >
      <span class="font-medium">{m.tour_venue_locked({ venue: lockedVenue.name })}</span>
      <span class="text-sm text-muted-foreground">{cityLabel(lockedVenue.city)}</span>
      {#if changeVenueHref}
        <a class="ml-auto text-sm underline" href={changeVenueHref}>{m.tour_venue_change()}</a>
      {/if}
    </div>
  {:else}
    <div class="grid gap-2 sm:col-span-2">
      <Label for="venue_name">{m.tour_field_venue_name()}</Label>
      <!-- A datalist, not a select: the network is wider than the catalogue, so an
           unlisted venue has to be typeable. Picking a suggestion fills this same
           input, which is how `matched` recovers the id. -->
      <Input id="venue_name" name="venue_name" list="tour-venues" bind:value={venueName} required />
      <datalist id="tour-venues">
        {#each venues as venue (venue.id)}
          <option value={venue.name}>{cityLabel(venue.city)}</option>
        {/each}
      </datalist>
      <p class="text-xs text-muted-foreground">{m.tour_field_venue_hint()}</p>
      {#if matched}
        <input type="hidden" name="venue_id" value={matched.id} />
      {/if}
    </div>

    <div class="grid gap-2 sm:col-span-2">
      <Label for="city">{m.tour_field_city()}</Label>
      <select
        id="city"
        name="city"
        value={effectiveCity}
        onchange={(event) => (city = event.currentTarget.value)}
        required
        class="h-10 rounded-lg border border-border/60 bg-background px-3 text-sm"
      >
        <option value="">{m.tour_field_city_choose()}</option>
        {#each cities as option (option)}
          <option value={option}>{cityLabel(option)}</option>
        {/each}
      </select>
    </div>
  {/if}

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
    <Input id="party_size" name="party_size" type="number" min="1" max="20" bind:value={guests} />
    <p class="text-xs text-muted-foreground">{m.tour_guests_hint()}</p>
  </div>

  <div class="sm:col-span-2">
    <Button type="submit" disabled={!canSubmit}>{m.tour_submit()}</Button>
  </div>
</form>
