<script lang="ts">
  import Check from '@lucide/svelte/icons/check';
  import ChevronRight from '@lucide/svelte/icons/chevron-right';
  import X from '@lucide/svelte/icons/x';
  import { m } from '$lib/paraglide/messages.js';

  let {
    venueName,
    venueId,
    venueSlug,
    open,
    submitted = $bindable(false),
    onClose
  }: {
    venueName: string;
    venueId?: number;
    venueSlug?: string;
    open: boolean;
    submitted?: boolean;
    onClose: () => void;
  } = $props();

  let sending = $state(false);
  let errorMessage = $state('');

  async function submitQuote(event: SubmitEvent) {
    event.preventDefault();
    if (sending) return;

    const form = event.currentTarget as HTMLFormElement;
    const data = new FormData(form);

    sending = true;
    errorMessage = '';

    try {
      const response = await fetch('/api/venue-pricing-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: String(data.get('name') ?? ''),
          whatsapp: String(data.get('whatsapp') ?? ''),
          email: String(data.get('email') ?? '') || null,
          wedding_date: String(data.get('wedding_date') ?? '') || null,
          best_time_to_reach: String(data.get('best_time_to_reach') ?? 'morning'),
          venue_id: venueId ?? null,
          venue_slug: venueSlug ?? null,
          venue_name: venueName
        })
      });

      if (!response.ok) {
        // Keep the couple's input on screen so they can retry rather than
        // showing a success state for a request that never landed.
        errorMessage = m.vd_modal_error();
        return;
      }

      submitted = true;
    } catch {
      errorMessage = m.vd_modal_error();
    } finally {
      sending = false;
    }
  }
</script>

<div class:open class="modal-ov" aria-hidden={!open}>
  <button
    class="modal-backdrop"
    type="button"
    aria-label={m.vd_modal_close_aria()}
    tabindex={open ? 0 : -1}
    onclick={onClose}
  ></button>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="quote-title" tabindex="-1">
    <div class="modal-head">
      <button class="x" type="button" onclick={onClose} aria-label={m.vd_modal_close()}><X size={18} /></button>
      {#if !submitted}
        <h3 id="quote-title">{m.vd_modal_title()}</h3>
        <p>{m.vd_modal_subtitle({ venue: venueName })}</p>
      {:else}
        <h3 class="hidden-heading" id="quote-title">{m.vd_modal_success_title()}</h3>
      {/if}
    </div>
    <div class="modal-body">
      {#if !submitted}
        <form onsubmit={submitQuote}>
          <div class="field">
            <label for="quote-name">{m.vd_modal_name()} <span class="req" aria-hidden="true">*</span></label>
            <input id="quote-name" name="name" required autocomplete="name" placeholder={m.vd_modal_name_ph()} />
          </div>
          <div class="field row2">
            <div>
              <label for="quote-whatsapp">{m.vd_modal_whatsapp()} <span class="req" aria-hidden="true">*</span></label>
              <input id="quote-whatsapp" name="whatsapp" required autocomplete="tel" placeholder={m.vd_modal_whatsapp_ph()} />
            </div>
            <div>
              <label for="quote-email">{m.vd_modal_email()} <span class="muted">({m.vd_modal_optional()})</span></label>
              <input id="quote-email" name="email" type="email" autocomplete="email" placeholder={m.vd_modal_email_ph()} />
            </div>
          </div>
          <div class="field">
            <label for="quote-wedding-date">{m.vd_modal_wedding_date()} <span class="muted">({m.vd_modal_optional()})</span></label>
            <input id="quote-wedding-date" name="wedding_date" type="date" />
          </div>
          <div class="field">
            <label for="quote-reach-time">{m.vd_modal_reach_time()}</label>
            <select id="quote-reach-time" name="best_time_to_reach">
              <option value="morning">{m.vd_modal_morning()}</option>
              <option value="afternoon">{m.vd_modal_afternoon()}</option>
              <option value="after_working_hours">{m.vd_modal_after_hours()}</option>
            </select>
          </div>
          {#if errorMessage}
            <p class="quote-error">{errorMessage}</p>
          {/if}
          <button class="btn btn-gold btn-lg btn-block" type="submit" disabled={sending}>
            {sending ? m.vd_modal_sending() : m.vd_modal_submit()}
            {#if !sending}<ChevronRight size={17} />{/if}
          </button>
        </form>
      {:else}
        <div class="success">
          <div class="big"><Check size={30} /></div>
          <h3>{m.vd_modal_success_title()}</h3>
          <p class="muted">{m.vd_modal_success_body()}</p>
          <button class="btn btn-soft btn-block" type="button" onclick={onClose}>{m.vd_modal_close()}</button>
        </div>
      {/if}
    </div>
  </div>
</div>
