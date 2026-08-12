<script lang="ts">
  import { m } from '$lib/paraglide/messages.js';

  import { VENDORS, VENDOR_CATS } from './vendors';

  let {
    /** `h1` when this section *is* the page, as on /our-vendors; `h2` when it sits
     * inside one, as on a venue's detail page. Wrong either way costs a level in
     * the document outline. */
    heading = 'h2'
  }: { heading?: 'h1' | 'h2' } = $props();

  // Category values stay canonical for filtering; only their labels are translated.
  const CAT_LABELS: Record<string, () => string> = {
    All: m.vd_cat_all,
    'Photo & Video': m.vd_cat_photo,
    Decoration: m.vd_cat_decor,
    Cakes: m.vd_cat_cakes,
    Entertainment: m.vd_cat_entertainment,
    'Bridal & Suit': m.vd_cat_bridal_suit,
    Extra: m.vd_cat_extra
  };
  const catLabel = (cat: string) => CAT_LABELS[cat]?.() ?? cat;

  let vendorCat = $state('All');
  let visibleVendors = $derived(
    vendorCat === 'All' ? VENDORS : VENDORS.filter((vendor) => vendor.cat === vendorCat)
  );
</script>

<section class="vsec" id="vendors">
  <div class="vwrap">
    <div class="vhead">
      <span class="veyebrow">{m.vd_eyebrow_partners()}</span>
      <svelte:element this={heading}>{m.vd_vendors_title()}</svelte:element>
      <p>{m.vd_vendors_intro({ count: VENDORS.length })}</p>
    </div>
    <div class="vfilter">
      {#each VENDOR_CATS as cat (cat)}
        <button
          class:on={vendorCat === cat}
          class="vchip"
          type="button"
          onclick={() => (vendorCat = cat)}
        >
          {catLabel(cat)}
        </button>
      {/each}
    </div>
    <div class="vgrid">
      {#each visibleVendors as vendor (vendor.name)}
        <div class="vcard">
          <div class="vlogo-wrap">
            <img
              class="vlogo"
              src={vendor.logo}
              alt={`${vendor.name} logo`}
              loading="lazy"
              decoding="async"
            />
          </div>
          <div class="vn">{vendor.name}</div>
          <div class="vc">{catLabel(vendor.cat)}</div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!--
  Self-contained on purpose. These rules used to live in the venue page's
  venue-detail.css scoped `.venue-detail .vgrid`, so the section only rendered
  correctly inside that one page's wrapper -- which is why it could not simply be
  dropped onto /our-vendors, where it is now the whole page.

  The layout classes are prefixed rather than reusing the page's generic
  `.section`/`.wrap`/`.sec-head`: those still exist in venue-detail.css for the
  neighbouring sections, and a same-named copy here would sit at equal specificity
  and resolve by source order. The tokens are redeclared for the same reason the
  classes are -- they are defined in venue-detail.css, not app.css, so a page that
  does not import it would otherwise render this unstyled.
-->
<style>
  .vsec {
    --line: #ece3d4;
    --gold: #b0823c;
    --gold-soft: #f2e6cc;
    --gold-deep: #8a6526;
    --surface: #ffffff;
    --ink: #241f19;
    --ink-soft: #5c5247;
    --muted: #8c8173;
    --shadow: 0 8px 30px rgba(72, 52, 18, 0.08);

    padding: 56px 0;
  }

  .vwrap {
    max-width: 1180px;
    margin: 0 auto;
    padding: 0 24px;
  }

  .vhead {
    max-width: 640px;
    margin: 0 auto 36px;
    text-align: center;
  }

  .veyebrow {
    color: var(--gold-deep);
    font-size: 12.5px;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
  }

  /* Both levels: the heading is an h1 when this section is the page. */
  .vhead :global(h1),
  .vhead :global(h2) {
    margin-top: 10px;
    font-family: var(--font-display);
    font-size: 40px;
    font-weight: 600;
  }

  .vhead p {
    margin-top: 12px;
    color: var(--ink-soft);
    font-size: 16px;
  }

  .vfilter {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    justify-content: center;
    margin-bottom: 28px;
  }

  .vchip {
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 9px 16px;
    color: var(--ink-soft);
    background: var(--surface);
    font-size: 13.5px;
    font-weight: 600;
    transition: all 0.15s;
  }

  .vchip:hover {
    border-color: var(--gold);
  }

  .vchip.on {
    color: #fff;
    background: var(--ink);
    border-color: var(--ink);
  }

  .vgrid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
  }

  .vcard {
    display: flex;
    min-height: 204px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 22px 18px;
    background: var(--surface);
    text-align: center;
    transition:
      transform 0.15s,
      box-shadow 0.15s,
      border-color 0.15s;
  }

  .vcard:hover {
    border-color: var(--gold-soft);
    transform: translateY(-3px);
    box-shadow: var(--shadow);
  }

  .vlogo-wrap {
    display: flex;
    width: 100%;
    height: 156px;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: #fff;
  }

  /* The vendor artwork is portrait (200x284 with whitespace baked in), so
     max-height is the constraint that actually binds -- at the old 82px every
     logo rendered 58px wide inside a 235px card and read as a thumbnail. Both
     caps are raised together so a landscape logo is not clipped instead. */
  .vlogo {
    max-width: 300px;
    max-height: 140px;
    object-fit: contain;
  }

  .vcard .vn {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 600;
    line-height: 1.12;
  }

  .vcard .vc {
    color: var(--muted);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  @media (max-width: 980px) {
    .vgrid {
      grid-template-columns: repeat(3, 1fr);
    }

    .vhead :global(h1),
    .vhead :global(h2) {
      font-size: 30px;
    }
  }

  @media (max-width: 720px) {
    .vwrap {
      padding: 0 16px;
    }
  }

  @media (max-width: 640px) {
    .vgrid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
