<script lang="ts">
  import Check from '@lucide/svelte/icons/check';
  import MapPin from '@lucide/svelte/icons/map-pin';
  import type { VenueDetail } from '$lib/api';
  import { vendorCount } from './vendors';
  import { m } from '$lib/paraglide/messages.js';

  let {
    venue,
    cityLabel,
    paxLabel
  }: {
    venue: VenueDetail;
    cityLabel: string;
    paxLabel: string;
  } = $props();

  const venueHighlights = $derived([
    m.vd_hl_hospitality({ stars: venue.stars }),
    m.vd_hl_packages({ pax: paxLabel }),
    m.vd_hl_located({ district: venue.district, city: cityLabel }),
    m.vd_hl_planner(),
    m.vd_hl_shortlist(),
    m.vd_hl_consult()
  ]);

  const venueStats = $derived([
    { value: `${venue.stars}★`, label: m.vd_stat_luxury() },
    { value: venue.price_for_total_pax.toLocaleString('id-ID'), label: m.vd_stat_pax() },
    { value: m.vd_stat_pricing_value(), label: m.vd_stat_pricing() },
    { value: m.vd_stat_reply_value(), label: m.vd_stat_reply() },
    { value: `${vendorCount}`, label: m.vd_stat_vendors() }
  ]);
</script>

<section class="section" id="overview">
  <div class="wrap ov-grid">
    <div>
      <span class="eyebrow">{m.vd_eyebrow_venue()}</span>
      <!-- The generic "iconic address" headline was removed on request: it was
           identical on every venue, so it said nothing the description below
           does not. The eyebrow still labels the section. -->
      <p>{venue.description}</p>
      <p class="address-line"><MapPin size={16} /> {venue.address}</p>
      <ul class="ov-list">
        {#each venueHighlights as highlight (highlight)}
          <li><span class="tick"><Check size={16} /></span>{highlight}</li>
        {/each}
      </ul>
    </div>
    <div class="stats">
      {#each venueStats as stat (stat.label)}
        <div class="stat"><div class="v">{stat.value}</div><div class="l">{stat.label}</div></div>
      {/each}
    </div>
  </div>
</section>
