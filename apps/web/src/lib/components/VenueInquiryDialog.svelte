<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import MapPinIcon from '@lucide/svelte/icons/map-pin';

  import DateField from '$lib/components/DateField.svelte';
  import { Button } from '$lib/components/ui/button';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { titleCase } from '$lib/utils';
  import { submitVenueInquiry, type InquiryVenue } from '$lib/venue-inquiry';

  let {
    venue,
    open = $bindable(false),
    onSubmitted
  }: {
    venue: InquiryVenue & { address: string; district: string };
    open?: boolean;
    // Fires once per pricing request that actually landed, so the caller can
    // record a conversion without this component knowing anything about analytics.
    onSubmitted?: (detail: { tour: boolean }) => void;
  } = $props();

  let sending = $state(false);
  let errorMessage = $state('');
  // Null until a pricing request lands; then 'skipped', 'ok' or the API's code.
  let tourOutcome = $state<string | null>(null);

  let weddingDate = $state('');
  let wantsTour = $state(false);
  let visitDate = $state('');
  let partySize = $state(2);

  const ids = $derived(`inquiry-${venue.id}`);
  const today = new Date().toISOString().slice(0, 10);
  // A row with no street address still has a district, which is enough to tell
  // two branches of the same hotel chain apart.
  const location = $derived(
    venue.address.trim() || `${venue.district}, ${titleCase(venue.city)}`
  );

  // The calendar submits through a hidden input, which `required` cannot guard.
  const canSubmit = $derived(!sending && (!wantsTour || Boolean(visitDate)));

  const TOUR_ERRORS: Record<string, () => string> = {
    already_registered: m.tour_error_already,
    no_open_event: m.tour_closed
  };

  // Back to an empty form on every open, so a previous success screen does not
  // greet the next request -- cards on a listing share nothing, but the venue
  // page reopens the same instance.
  $effect(() => {
    if (open) {
      tourOutcome = null;
      errorMessage = '';
    }
  });

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (!canSubmit) return;

    const data = new FormData(event.currentTarget as HTMLFormElement);
    sending = true;
    errorMessage = '';

    const result = await submitVenueInquiry(
      {
        venue,
        name: String(data.get('name') ?? '').trim(),
        whatsapp: String(data.get('whatsapp') ?? '').trim(),
        email: String(data.get('email') ?? '').trim(),
        weddingDate,
        bestTimeToReach: String(data.get('best_time_to_reach') ?? 'morning'),
        tour: wantsTour ? { visitDate, partySize } : null,
        locale: getLocale()
      },
      fetch
    );
    sending = false;

    if (result.pricing === 'failed') {
      // Keep the couple's input on screen so they can retry rather than showing
      // a success state for a request that never landed.
      errorMessage = m.vd_modal_error();
      return;
    }

    tourOutcome = result.tour;
    onSubmitted?.({ tour: result.tour === 'ok' });
  }

  const CONTROL = 'h-10 text-base md:text-[15px]';
</script>

<Dialog.Root bind:open>
  <Dialog.Content class="max-h-[92vh] overflow-y-auto sm:max-w-lg">
    <Dialog.Header>
      <Dialog.Title class="font-display text-xl font-bold">
        {tourOutcome === null ? m.vd_modal_title() : m.vd_modal_success_title()}
      </Dialog.Title>
      {#if tourOutcome === null}
        <Dialog.Description>{m.vd_modal_subtitle({ venue: venue.name })}</Dialog.Description>
      {/if}
    </Dialog.Header>

    {#if tourOutcome !== null}
      <div class="flex flex-col items-center gap-4 py-2 text-center">
        <span
          class="flex size-14 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover"
        >
          <CheckIcon size={28} />
        </span>
        <p class="text-sm leading-6 text-muted-foreground">{m.vd_modal_success_body()}</p>
        {#if tourOutcome === 'ok'}
          <p class="text-sm leading-6">{m.vd_modal_tour_success()}</p>
        {:else if tourOutcome !== 'skipped'}
          <!-- Pricing landed, so this is a notice and not an error: retrying
               the whole form would file the pricing request a second time. -->
          <div class="w-full rounded-xl border border-border/60 p-4 text-sm leading-6">
            <p>{m.vd_modal_tour_failed()}</p>
            <p class="mt-1 text-muted-foreground">
              {(TOUR_ERRORS[tourOutcome] ?? m.tour_error_generic)()}
            </p>
            {#if tourOutcome !== 'already_registered'}
              <a
                class="mt-2 inline-block font-medium underline"
                href={localizeHref(`/tour?venue=${venue.id}`)}
              >
                {m.vd_modal_tour_retry()}
              </a>
            {/if}
          </div>
        {/if}
        <Button variant="ghost" class="w-full" onclick={() => (open = false)}>
          {m.vd_modal_close()}
        </Button>
      </div>
    {:else}
      <!-- The venue is the one the couple clicked, so it is stated, not asked. -->
      <div class="flex items-start gap-3 rounded-xl border border-border/60 p-4">
        <MapPinIcon size={18} class="mt-0.5 shrink-0 text-brand-gold" />
        <div class="min-w-0">
          <p class="font-medium">{venue.name}</p>
          <p class="text-sm text-muted-foreground">{location}</p>
        </div>
      </div>

      <form onsubmit={submit} class="grid gap-4">
        <div class="grid gap-1.5">
          <Label for="{ids}-name">
            {m.vd_modal_name()} <span class="text-destructive" aria-hidden="true">*</span>
          </Label>
          <Input
            id="{ids}-name"
            name="name"
            required
            autocomplete="name"
            placeholder={m.vd_modal_name_ph()}
            class={CONTROL}
          />
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="grid gap-1.5">
            <Label for="{ids}-whatsapp">
              {m.vd_modal_whatsapp()} <span class="text-destructive" aria-hidden="true">*</span>
            </Label>
            <Input
              id="{ids}-whatsapp"
              name="whatsapp"
              required
              autocomplete="tel"
              placeholder={m.vd_modal_whatsapp_ph()}
              class={CONTROL}
            />
          </div>
          <div class="grid gap-1.5">
            <Label for="{ids}-email">
              {m.vd_modal_email()}
              {#if wantsTour}
                <span class="text-destructive" aria-hidden="true">*</span>
              {:else}
                <span class="text-muted-foreground">({m.vd_modal_optional()})</span>
              {/if}
            </Label>
            <!-- Required only with a tour: the booking confirmation goes by email,
                 and the tour API will not take a registration without one. -->
            <Input
              id="{ids}-email"
              name="email"
              type="email"
              required={wantsTour}
              autocomplete="email"
              placeholder={m.vd_modal_email_ph()}
              class={CONTROL}
            />
          </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="grid gap-1.5">
            <Label for="{ids}-wedding-date">
              {m.vd_modal_wedding_date()}
              <span class="text-muted-foreground">({m.vd_modal_optional()})</span>
            </Label>
            <DateField
              id="{ids}-wedding-date"
              bind:value={weddingDate}
              min={today}
              placeholder={m.vd_modal_date_ph()}
              class="w-full {CONTROL}"
            />
          </div>
          <div class="grid gap-1.5">
            <Label for="{ids}-reach-time">{m.vd_modal_reach_time()}</Label>
            <select
              id="{ids}-reach-time"
              name="best_time_to_reach"
              class="rounded-md border border-input bg-transparent px-2.5 shadow-xs {CONTROL}"
            >
              <option value="morning">{m.vd_modal_morning()}</option>
              <option value="afternoon">{m.vd_modal_afternoon()}</option>
              <option value="after_working_hours">{m.vd_modal_after_hours()}</option>
            </select>
          </div>
        </div>

        <div class="rounded-xl border border-border/60 p-4">
          <label class="flex cursor-pointer items-start gap-3">
            <input
              type="checkbox"
              bind:checked={wantsTour}
              class="mt-1 size-4 shrink-0 accent-brand-gold"
            />
            <span>
              <span class="font-medium">{m.vd_modal_tour_opt_in()}</span>
              <span class="mt-0.5 block text-sm text-muted-foreground">{m.vd_modal_tour_hint()}</span>
            </span>
          </label>

          {#if wantsTour}
            <div class="mt-4 grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <Label for="{ids}-visit-date">
                  {m.tour_field_date()} <span class="text-destructive" aria-hidden="true">*</span>
                </Label>
                <!-- Any future day, no slots: the team confirms a time when they
                     follow up, as on the tour page. -->
                <DateField
                  id="{ids}-visit-date"
                  bind:value={visitDate}
                  min={today}
                  placeholder={m.vd_modal_date_ph()}
                  class="w-full {CONTROL}"
                />
              </div>
              <div class="grid gap-1.5">
                <Label for="{ids}-party-size">{m.tour_field_guests_total()}</Label>
                <Input
                  id="{ids}-party-size"
                  type="number"
                  min="1"
                  max="20"
                  bind:value={partySize}
                  class={CONTROL}
                />
                <p class="text-xs text-muted-foreground">{m.tour_guests_hint()}</p>
              </div>
            </div>
            <p class="mt-3 text-xs text-muted-foreground">{m.vd_modal_tour_email_hint()}</p>
          {/if}
        </div>

        {#if errorMessage}
          <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
        {/if}

        <Button type="submit" variant="gold" size="lg" class="w-full" disabled={!canSubmit}>
          {sending ? m.vd_modal_sending() : m.vd_modal_submit()}
        </Button>
      </form>
    {/if}
  </Dialog.Content>
</Dialog.Root>
