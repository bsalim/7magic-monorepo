<script lang="ts">
  import { enhance } from '$app/forms';

  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as m from '$lib/paraglide/messages';
  import { isDateBookable, slotsForDate } from '$lib/tour-availability';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  let visitDate = $state('');
  let extraGuests = $state(0);

  const slots = $derived(visitDate ? slotsForDate(visitDate, data.openingHours) : []);
  const dateIsClosed = $derived(
    visitDate.length === 10 && !isDateBookable(visitDate, data.openingHours, data.closedDates)
  );

  const today = new Date().toISOString().slice(0, 10);

  const ERROR_MESSAGES: Record<string, () => string> = {
    already_registered: m.tour_error_already,
    event_full: m.tour_error_full,
    branch_closed: m.tour_error_branch_closed
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
  <h1 class="text-3xl font-semibold">{data.branch.name}</h1>
  <p class="mt-2 text-muted-foreground">
    {data.branch.addressLine1}{data.branch.addressLine2 ? `, ${data.branch.addressLine2}` : ''}
  </p>

  {#if data.settings.tourIntroHtml}
    <!-- Sanitized on write by the API's allowlist; see core/html.py -->
    <div class="prose mt-6">{@html data.settings.tourIntroHtml}</div>
  {/if}

  {#if form?.ok}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_success()}</p>
  {:else if !data.event || !data.event.registrationOpen}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_closed()}</p>
  {:else}
    {#if errorMessage}
      <p class="mt-6 text-sm text-destructive">{errorMessage}</p>
    {/if}

    <form method="POST" use:enhance class="mt-8 grid gap-4 sm:grid-cols-2">
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
        <Label for="visitDate">{m.tour_field_date()}</Label>
        <Input
          id="visitDate"
          name="visitDate"
          type="date"
          min={today}
          bind:value={visitDate}
          required
        />
        {#if dateIsClosed}
          <p class="text-sm text-destructive">{m.tour_error_branch_closed()}</p>
        {/if}
      </div>
      <div class="grid gap-2">
        <Label for="visitSlot">{m.tour_field_slot()}</Label>
        <select
          id="visitSlot"
          name="visitSlot"
          class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
          disabled={slots.length === 0 || dateIsClosed}
        >
          {#each slots as slot (slot)}
            <option value={slot}>{slot}</option>
          {/each}
        </select>
      </div>
      <div class="grid gap-2">
        <Label for="guests">{m.tour_field_guests()}</Label>
        <Input id="guests" name="guests" type="number" min="0" max="10" bind:value={extraGuests} />
      </div>

      {#each Array.from({ length: Math.max(0, Math.min(extraGuests, 10)) }, (_, index) => index) as index (index)}
        <div class="grid gap-2">
          <Label for={`guest-${index}`}>{`${m.tour_field_guests()} ${index + 1}`}</Label>
          <Input id={`guest-${index}`} name={`guest-${index}`} />
        </div>
      {/each}

      <div class="sm:col-span-2">
        <Button type="submit" disabled={dateIsClosed}>{m.tour_submit()}</Button>
      </div>
    </form>

    {#if data.settings.arrivalInstructions || data.settings.parkingNotes}
      <div class="mt-10 grid gap-2 text-sm text-muted-foreground">
        {#if data.settings.arrivalInstructions}<p>{data.settings.arrivalInstructions}</p>{/if}
        {#if data.settings.parkingNotes}<p>{data.settings.parkingNotes}</p>{/if}
      </div>
    {/if}
  {/if}
</main>

<PublicFooter />
