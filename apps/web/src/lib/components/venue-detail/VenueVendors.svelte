<script lang="ts">
  import { VENDORS, VENDOR_CATS } from './vendors';
  import { m } from '$lib/paraglide/messages.js';

  // Category values stay canonical for filtering; only their labels are translated.
  const CAT_LABELS: Record<string, () => string> = {
    All: m.vd_cat_all,
    'Photo & Video': m.vd_cat_photo,
    Decoration: m.vd_cat_decor,
    Cakes: m.vd_cat_cakes,
    Entertainment: m.vd_cat_entertainment,
    'Beauty & Bridal': m.vd_cat_beauty,
    'Attire & Extras': m.vd_cat_attire
  };
  const catLabel = (cat: string) => CAT_LABELS[cat]?.() ?? cat;

  let vendorCat = $state('All');
  let visibleVendors = $derived(
    vendorCat === 'All' ? VENDORS : VENDORS.filter((vendor) => vendor.cat === vendorCat)
  );
</script>

<section class="section" id="vendors">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">{m.vd_eyebrow_partners()}</span>
      <h2>{m.vd_vendors_title()}</h2>
      <p>{m.vd_vendors_intro({ count: VENDORS.length })}</p>
    </div>
    <div class="vfilter">
      {#each VENDOR_CATS as cat (cat)}
        <button class:on={vendorCat === cat} class="vchip" type="button" onclick={() => (vendorCat = cat)}>
          {catLabel(cat)}
        </button>
      {/each}
    </div>
    <div class="vgrid">
      {#each visibleVendors as vendor (vendor.name)}
        <div class="vcard">
          <div class="vlogo-wrap">
            <img class="vlogo" src={vendor.logo} alt={`${vendor.name} logo`} loading="lazy" decoding="async" />
          </div>
          <div class="vn">{vendor.name}</div>
          <div class="vc">{catLabel(vendor.cat)}</div>
        </div>
      {/each}
    </div>
  </div>
</section>
