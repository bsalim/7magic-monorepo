<script lang="ts">
  import CalendarCheckIcon from '@lucide/svelte/icons/calendar-check';
  import HandshakeIcon from '@lucide/svelte/icons/handshake';
  import PhoneCallIcon from '@lucide/svelte/icons/phone-call';

  import * as m from '$lib/paraglide/messages';

  // The venue the guest arrived with, if any. Named rather than described
  // generically: someone who already chose a venue is a different reader.
  let { venueName = null }: { venueName?: string | null } = $props();

  const points = $derived([
    { icon: PhoneCallIcon, title: m.tour_pitch_1_title(), body: m.tour_pitch_1_body() },
    { icon: HandshakeIcon, title: m.tour_pitch_2_title(), body: m.tour_pitch_2_body() },
    { icon: CalendarCheckIcon, title: m.tour_pitch_3_title(), body: m.tour_pitch_3_body() }
  ]);
</script>

<section class="mt-6">
  <h2 class="text-xl font-semibold">{m.tour_pitch_title()}</h2>
  <p class="mt-3 max-w-2xl text-muted-foreground">
    {venueName ? m.tour_pitch_venue({ venue: venueName }) : m.tour_pitch_body()}
  </p>

  <div class="mt-6 grid gap-5 sm:grid-cols-3">
    {#each points as point (point.title)}
      <div>
        <point.icon class="size-5 text-muted-foreground" />
        <h3 class="mt-2 text-sm font-semibold">{point.title}</h3>
        <p class="mt-1 text-sm text-muted-foreground">{point.body}</p>
      </div>
    {/each}
  </div>
</section>
