<script lang="ts">
  import { env } from '$env/dynamic/public';
  import { m } from '$lib/paraglide/messages.js';

  /**
   * Continuously scrolling strip of venue-partner logos, shown above the footer.
   *
   * The logos are desaturated to greyscale at upload time rather than with a CSS
   * `filter`, so the browser never paints a colour version first and the strip
   * cannot flash colour on slow paints. They are uploaded by
   * `apps/api/scripts/upload_partner_logos.py`; provenance and licence for each
   * file is recorded in `scripts/partner_logos_manifest.json`.
   *
   * Partners without a sourced logo fall back to a wordmark. That is deliberate:
   * inventing a mark for a real hotel brand would be worse than showing its name
   * set in type, and the fallback disappears on its own once `logo: true` is set
   * and the file exists in R2.
   */

  // These logos are the one set of R2 objects the API does not hand us a URL
  // for, so the bucket host has to be known here. Read it from the environment
  // rather than hardcoding: the bucket has already moved hosts once, and a
  // literal here is the thing that gets missed next time.
  const mediaBaseUrl = env.PUBLIC_MEDIA_BASE_URL || 'https://media.7magicwedding.com';
  const R2 = `${mediaBaseUrl}/hotel-partners`;

  type Partner = { name: string; slug?: string };

  // Order is chosen for the strip, not taken from the partner list as supplied:
  // grouped as given, the wordmarks fall consecutively and a whole screen can be
  // nothing but text, which reads as broken artwork. At 19 logos to 10 wordmarks
  // a strict alternation is impossible, so the wordmarks are spread as evenly as
  // the counts allow — never more than two logos in a row, and never two
  // wordmarks adjacent. The list ends on a wordmark so the wrap point does not
  // create a third consecutive logo where the loop rejoins.
  // `slug` present => a logo exists in R2; no slug => wordmark fallback.
  const partners: Partner[] = [
    { name: 'The Ritz-Carlton', slug: 'ritz-carlton' },
    { name: 'Visesa Ubud', slug: 'visesa-ubud' },
    { name: 'JW Marriott' },
    { name: 'Aloft', slug: 'aloft' },
    { name: 'Hotel Tentrem', slug: 'tentrem' },
    { name: 'Vivere' },
    { name: 'The Westin', slug: 'westin' },
    { name: 'Titik Dua Ubud', slug: 'titik-dua-ubud' },
    { name: 'Shangri-La' },
    { name: 'Kempinski', slug: 'kempinski' },
    { name: 'Grand Hyatt', slug: 'grand-hyatt' },
    { name: 'Artotel' },
    { name: 'St. Regis', slug: 'st-regis' },
    { name: 'ibis Styles', slug: 'ibis-styles' },
    { name: 'JS Luwansa' },
    { name: 'Pullman', slug: 'pullman' },
    { name: 'Conrad', slug: 'conrad' },
    { name: 'Lumire' },
    { name: 'Four Points', slug: 'four-points' },
    { name: 'HARRIS' },
    { name: 'Vertu', slug: 'vertu' },
    { name: 'Mercure', slug: 'mercure' },
    { name: 'Ascott' },
    { name: 'Grand Mercure', slug: 'grand-mercure' },
    { name: 'Novotel', slug: 'novotel' },
    { name: 'Trembesi' },
    { name: 'The Oberoi', slug: 'oberoi-bali' },
    { name: 'Hilton', slug: 'hilton-bali' },
    { name: 'Atria' }
  ];

  // The track holds two identical copies and translates by exactly -50%, so the
  // second copy lands where the first began and the loop has no visible seam.
  const loop = [...partners, ...partners];
</script>

<section class="border-t border-border bg-background py-10" aria-labelledby="venue-partners-heading">
  <h2
    id="venue-partners-heading"
    class="px-5 text-center text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground lg:px-8"
  >
    {m.partners_title()}
  </h2>

  <div class="marquee mt-7">
    <ul class="track">
      {#each loop as partner, index}
        <!-- The second copy is presentational: screen readers would otherwise
             hear all 29 partners twice. -->
        <li class="item" aria-hidden={index >= partners.length ? 'true' : undefined}>
          {#if partner.slug}
            <img
              src="{R2}/{partner.slug}.png"
              alt={index >= partners.length ? '' : partner.name}
              loading="lazy"
              decoding="async"
              width="340"
              height="130"
              class="h-10 w-auto object-contain opacity-60 transition duration-300 hover:opacity-100 sm:h-11"
            />
          {:else}
            <!-- Deliberately quieter than a logo: a wordmark set at logo weight
                 out-shouts the real marks beside it. -->
            <span
              class="whitespace-nowrap font-display text-sm font-medium uppercase tracking-[0.14em] text-muted-foreground/55 transition duration-300 hover:text-foreground sm:text-[15px]"
            >
              {partner.name}
            </span>
          {/if}
        </li>
      {/each}
    </ul>
  </div>
</section>

<style>
  .marquee {
    overflow: hidden;
    /* Fade the strip into the page at both edges so logos enter and leave
       rather than being clipped mid-wordmark. */
    -webkit-mask-image: linear-gradient(
      to right,
      transparent,
      #000 6rem,
      #000 calc(100% - 6rem),
      transparent
    );
    mask-image: linear-gradient(
      to right,
      transparent,
      #000 6rem,
      #000 calc(100% - 6rem),
      transparent
    );
  }

  .track {
    display: flex;
    align-items: center;
    gap: 3.5rem;
    width: max-content;
    margin: 0;
    padding: 0 1.75rem;
    list-style: none;
    animation: marquee-scroll 70s linear infinite;
  }

  .item {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: none;
  }

  /* Hovering anything in the strip holds it still, so a logo can actually be
     read and the hover state on it is reachable. */
  .marquee:hover .track {
    animation-play-state: paused;
  }

  @keyframes marquee-scroll {
    from {
      transform: translate3d(0, 0, 0);
    }
    to {
      transform: translate3d(-50%, 0, 0);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .track {
      animation: none;
      /* Without the animation the second copy is unreachable, so let the strip
         be scrolled by hand instead. */
      width: 100%;
      overflow-x: auto;
      flex-wrap: nowrap;
    }
  }
</style>
