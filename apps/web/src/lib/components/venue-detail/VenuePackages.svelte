<script lang="ts">
  import Check from '@lucide/svelte/icons/check';
  import ChevronRight from '@lucide/svelte/icons/chevron-right';
  import MessageCircle from '@lucide/svelte/icons/message-circle';
  import { m } from '$lib/paraglide/messages.js';

  type PackageCard = {
    id: string;
    name: string;
    sub: string;
    tag: string;
    blurb: string;
    featured: boolean;
    highlights: string[];
  };

  let {
    whatsappHref,
    onQuote
  }: {
    whatsappHref: string;
    onQuote: () => void;
  } = $props();

  const PACKAGES: PackageCard[] = $derived([
    {
      id: '4in1',
      name: '4 in 1',
      sub: m.vd_pkg_without_bridal(),
      tag: m.vd_pkg_tag_essential(),
      blurb: m.vd_pkg_blurb_4in1(),
      featured: false,
      highlights: [
        m.vd_pkg_4in1_h1(),
        m.vd_pkg_4in1_h2(),
        m.vd_pkg_4in1_h3(),
        m.vd_pkg_4in1_h4(),
        m.vd_pkg_4in1_h5()
      ]
    },
    {
      id: 'elegant',
      name: 'All in Elegant',
      sub: m.vd_pkg_with_bridal(),
      tag: m.vd_pkg_tag_most_chosen(),
      blurb: m.vd_pkg_blurb_elegant(),
      featured: true,
      highlights: [
        m.vd_pkg_eleg_h1(),
        m.vd_pkg_eleg_h2(),
        m.vd_pkg_eleg_h3(),
        m.vd_pkg_eleg_h4(),
        m.vd_pkg_eleg_h5()
      ]
    },
    {
      id: 'luxury',
      name: 'All in Luxury',
      sub: m.vd_pkg_with_bridal(),
      tag: m.vd_pkg_tag_signature(),
      blurb: m.vd_pkg_blurb_luxury(),
      featured: false,
      highlights: [
        m.vd_pkg_lux_h1(),
        m.vd_pkg_lux_h2(),
        m.vd_pkg_lux_h3(),
        m.vd_pkg_lux_h4(),
        m.vd_pkg_lux_h5()
      ]
    }
  ]);

  const COMPARE = $derived({
    cols: [
      { name: '4 in 1', sub: m.vd_compare_without_bridal(), featured: false },
      { name: 'All in Elegant', sub: m.vd_compare_with_bridal(), featured: false },
      { name: 'All in Luxury', sub: m.vd_compare_with_bridal(), featured: true }
    ],
    rows: [
      {
        feature: m.vd_cmp_gown(),
        values: [m.vd_cmp_none(), m.vd_cmp_standard_vendor(), m.vd_cmp_premium_vendor()]
      },
      {
        feature: m.vd_cmp_makeup(),
        values: [m.vd_cmp_none(), m.vd_cmp_inhouse_makeup(), m.vd_cmp_external_mua()]
      },
      {
        feature: m.vd_cmp_attire(),
        values: [m.vd_cmp_none(), m.vd_cmp_groom_tux(), m.vd_cmp_eleg_plus()]
      },
      {
        feature: m.vd_cmp_mc(),
        values: [m.vd_cmp_band_small(), m.vd_cmp_band_small(), m.vd_cmp_band_large()]
      },
      {
        feature: m.vd_cmp_decor(),
        values: [m.vd_cmp_up_to_7m(), m.vd_cmp_up_to_7m(), m.vd_cmp_up_to_10m()]
      },
      {
        feature: m.vd_cmp_photo(),
        values: [m.vd_cmp_photo_1(), m.vd_cmp_photo_1(), m.vd_cmp_photo_2()]
      },
      {
        feature: m.vd_cmp_prewed(),
        values: [m.vd_cmp_none(), m.vd_cmp_indoor(), m.vd_cmp_indoor()]
      },
      {
        feature: m.vd_cmp_organizer(),
        values: [m.vd_cmp_full_day_wo(), m.vd_cmp_full_day_wo(), m.vd_cmp_full_planner()]
      }
    ]
  });

  let compareOpen = $state(false);
</script>

<section class="section warm" id="packages">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">{m.vd_eyebrow_packages()}</span>
      <h2>{m.vd_packages_title()}</h2>
      <p>{m.vd_packages_intro()}</p>
    </div>

    <div class="pkgs">
      {#each PACKAGES as pkg (pkg.id)}
        <article class:feat={pkg.featured} class="pkg">
          <span class="pkg-tag">{pkg.tag}</span>
          <div class="pkg-sub">{pkg.sub}</div>
          <h3 class="pkg-name">{pkg.name}</h3>
          <p class="pkg-blurb">{pkg.blurb}</p>
          <ul class="pkg-feats">
            {#each pkg.highlights as highlight (highlight)}
              <li><span class="tick"><Check size={16} /></span>{highlight}</li>
            {/each}
          </ul>
          <button
            class:btn-gold={pkg.featured}
            class:btn-ghost={!pkg.featured}
            class="btn btn-block pkg-cta"
            type="button"
            onclick={onQuote}
          >
            {m.vd_see_pricing()} <ChevronRight size={17} />
          </button>
        </article>
      {/each}
    </div>

    <div class="compare-toggle">
      <button class="btn btn-ghost" type="button" onclick={() => (compareOpen = !compareOpen)}>
        {compareOpen ? m.vd_compare_hide() : m.vd_compare_show()}
      </button>
    </div>

    {#if compareOpen}
      <div class="compare-wrap">
        <table class="cmp">
          <thead>
            <tr>
              <th>{m.vd_compare_features()}</th>
              {#each COMPARE.cols as col (col.name)}
                <th class:on={col.featured} class="col-feat">{col.name}<span>{col.sub}</span></th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each COMPARE.rows as row (row.feature)}
              <tr>
                <th scope="row">{row.feature}</th>
                {#each row.values as value, index}
                  <td class:on={COMPARE.cols[index].featured} class="col-feat">{value}</td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}

    <div class="pkg-foot">
      <a class="btn btn-wa" href={whatsappHref}>
        <MessageCircle size={18} /> {m.vd_promo_cta()}
      </a>
    </div>
  </div>
</section>
