<script lang="ts">
  import CalendarDays from '@lucide/svelte/icons/calendar-days';
  import MapPinned from '@lucide/svelte/icons/map-pinned';
  import MessageCircle from '@lucide/svelte/icons/message-circle';
  import { m } from '$lib/paraglide/messages.js';

  let {
    venueName,
    whatsappHref,
    tourHref,
    onQuote
  }: {
    venueName: string;
    whatsappHref: string;
    /** Books a free tour of *this* venue -- it arrives preselected in the form. */
    tourHref: string;
    onQuote: () => void;
  } = $props();
</script>

<section class="section">
  <div class="wrap">
    <div class="cta-band">
      <div>
        <h2>{m.vd_cta_title({ venue: venueName })}</h2>
        <p>{m.vd_cta_body()}</p>
      </div>
      <div class="acts">
        <button class="btn btn-gold btn-lg" type="button" onclick={onQuote}>
          <CalendarDays size={17} /> {m.vd_see_pricing()}
        </button>
        <!-- Soft, not a second solid gold. These two sat side by side in the same
             colour, so neither read as the primary action. Matches the hero card,
             where pricing is the ask and the tour is the strong second. -->
        <a class="btn btn-soft btn-lg" href={tourHref}>
          <MapPinned size={17} /> {m.vd_book_tour()}
        </a>
        <a class="btn btn-wa btn-lg" href={whatsappHref}>
          <MessageCircle size={18} /> {m.vd_whatsapp_us()}
        </a>
      </div>
    </div>
  </div>
</section>
