<script lang="ts">
  import CalendarDays from '@lucide/svelte/icons/calendar-days';
  import Check from '@lucide/svelte/icons/check';
  import MapPin from '@lucide/svelte/icons/map-pin';
  import MapPinned from '@lucide/svelte/icons/map-pinned';
  import MessageCircle from '@lucide/svelte/icons/message-circle';
  import PhotoMosaic from './PhotoMosaic.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import type { VenueDetail } from '$lib/api';
  import type { DisplayPhoto } from './photos';
  import { localizeHref } from '$lib/paraglide/runtime';

  let {
    venue,
    cityLabel,
    paxLabel,
    whatsappHref,
    tourHref,
    photos,
    bookingCard = $bindable(),
    onQuote
  }: {
    venue: VenueDetail;
    cityLabel: string;
    paxLabel: string;
    whatsappHref: string;
    /** Books a free tour of *this* venue -- it arrives preselected in the form. */
    tourHref: string;
    photos: DisplayPhoto[];
    bookingCard?: HTMLElement;
    onQuote: () => void;
  } = $props();
</script>

<section class="hero">
  <div class="wrap">
    <nav class="crumbs" aria-label={m.vd_breadcrumb()}>
      <a href={localizeHref('/')}>{m.vd_home()}</a><span class="sep">/</span>
      <a href={localizeHref('/wedding-venue/search')}>{m.vd_wedding_venues()}</a><span class="sep">/</span>
      <a href={localizeHref(`/wedding-venue/search?city=${venue.city}`)}>{cityLabel}</a><span class="sep">/</span>
      <span class="cur">{venue.name}</span>
    </nav>

    <div class="hero-head">
      <h1 class="hero-title">{venue.name}</h1>
      <div class="hero-loc"><MapPin size={17} /> {venue.district}, {cityLabel} · Indonesia</div>
      <div class="hero-meta">
        <span class="stars" aria-label={m.vd_star_hotel({ stars: venue.stars })}>
          {'★'.repeat(Math.max(1, venue.stars))}
        </span>
        <span class="muted">{m.vd_star_hotel({ stars: venue.stars })}</span>
      </div>
      <div class="chips">
        <span class="chip">{m.vd_chip_venue({ stars: venue.stars })}</span>
        <span class="chip">{m.vd_chip_packages_for({ pax: paxLabel })}</span>
        <span class="chip">{m.vd_chip_private_pricing()}</span>
        <span class="chip"><b>{venue.district}</b></span>
      </div>
    </div>

    <div class="hero-grid">
      <div class="gallery">
        <PhotoMosaic {photos} venueName={venue.name} />
      </div>

      <aside class="book" bind:this={bookingCard} aria-label={m.vd_booking()}>
        <div class="book-from">{m.vd_pricing_by_request()}</div>
        <div class="book-private">{m.vd_share_details()}</div>
        <div class="book-note"><Check size={16} /> {m.vd_no_public_pricing()}</div>
        <div class="book-ctas">
          <button class="btn btn-gold btn-lg btn-block" type="button" onclick={onQuote}>
            <CalendarDays size={17} /> {m.vd_see_pricing()}
          </button>
          <!-- Soft rather than a second solid gold: the tour was previously only
               offered in the closing band, below packages and vendors, which most
               visitors never reach. It belongs in the card, but as the strong
               secondary -- two solid CTAs side by side read as no primary at all. -->
          <a class="btn btn-soft btn-block" href={tourHref}>
            <MapPinned size={17} /> {m.vd_book_tour()}
          </a>
          <a class="btn btn-wa btn-block" href={whatsappHref}>
            <MessageCircle size={18} /> {m.vd_chat_whatsapp()}
          </a>
        </div>
        <div class="book-trust">
          <div class="trust-row"><span class="tick"><Check size={16} /></span> {m.vd_trust_free()}</div>
          <div class="trust-row"><span class="tick"><Check size={16} /></span> {m.vd_trust_reply()}</div>
          <div class="trust-row"><span class="tick"><Check size={16} /></span> {m.vd_trust_planner()}</div>
        </div>
      </aside>
    </div>
  </div>
</section>
