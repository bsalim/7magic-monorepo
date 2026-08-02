<script lang="ts">
  import CalendarDays from '@lucide/svelte/icons/calendar-days';
  import MessageCircle from '@lucide/svelte/icons/message-circle';
  import { m } from '$lib/paraglide/messages.js';

  let {
    venueName,
    whatsappHref,
    show,
    onQuote
  }: {
    venueName: string;
    whatsappHref: string;
    show: boolean;
    onQuote: () => void;
  } = $props();
</script>

<div class:show class="sticky-bar" aria-hidden={!show}>
  <div class="sticky-in">
    <div class="sticky-info">
      <div class="n">{venueName}</div>
      <div class="p">{m.vd_pricing_by_request()}</div>
    </div>
    <div class="sticky-acts">
      <a class="btn btn-wa" href={whatsappHref}>
        <MessageCircle size={18} /> <span class="wa-label">{m.vd_whatsapp()}</span>
      </a>
      <button class="btn btn-gold" type="button" onclick={onQuote}>
        <CalendarDays size={17} /> {m.vd_see_pricing()}
      </button>
    </div>
  </div>
</div>
