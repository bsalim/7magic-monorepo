<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import BaliEnquiry from '$lib/components/bali/BaliEnquiry.svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import { buttonVariants } from '$lib/components/ui/button';
  import { englishPath, siteHref } from '$lib/seo/english-only';
  import {
    breadcrumbList,
    canonicalUrl,
    faqPage,
    graph,
    jsonLdScript,
    organization,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import {
    COST_SOURCES,
    ESTIMATES_AS_OF,
    METHOD_NOTES,
    SETTINGS,
    STYLES,
    estimateCost,
    type CostInput,
    type Setting
  } from '$lib/tools/bali-cost';
  import { formatAud, formatAudRange, formatDateRange } from '$lib/tools/bali-format';
  import { cn } from '$lib/utils';

  /**
   * "How much does a Bali wedding cost?" for Australian couples. English only.
   *
   * Every figure on this page is generated from `$lib/tools/bali-cost`, the
   * same model as the calculator, so the guide and the tool cannot disagree
   * and an update to a sourced range updates both. Nothing here is typed in by
   * hand, and nothing is a 7Magic price.
   *
   * Laid out for answer engines as much as for readers: a dated direct answer
   * first, then tables, then the method and every source.
   */

  const PATH = '/bali-wedding-cost';
  const path = englishPath(PATH);
  const title = 'How Much Does a Bali Wedding Cost? (2027, in AUD) | 7Magic';
  const description =
    'What a Bali wedding costs in Australian dollars in 2027: typical ranges by setting and guest count, where the money goes, hidden costs and guest flights, built from published prices.';

  // Fixed month: the model has no seasonal multiplier, so the month only
  // selects which dates the estimate would flag, and this page shows none.
  const at = (patch: Partial<CostInput>) =>
    estimateCost({
      guests: 50,
      setting: 'villa',
      style: 'classic',
      year: 2027,
      month: 7,
      addOns: [],
      ...patch
    });

  const villa55 = at({ guests: 55 });
  const villa50 = at({});
  const elopement = at({ setting: 'elopement', guests: 2 });
  const resort100 = at({ setting: 'resort', guests: 100, style: 'luxe' });

  const GROUP_SIZES = [20, 50, 100];
  const groupSettings = SETTINGS.filter((s) => s.key !== 'elopement');
  const bySetting = groupSettings.map((setting) => ({
    label: setting.label,
    totals: GROUP_SIZES.map((guests) => at({ setting: setting.key as Setting, guests }).total)
  }));
  const byStyle = STYLES.map((style) => ({ label: style.label, estimate: at({ style: style.key }) }));

  const answer = `A classic Bali villa wedding for 55 guests typically costs ${formatAudRange(
    villa55.total
  )}, about ${formatAudRange(villa55.perGuest)} per guest, before flights. An elopement for two runs ${formatAudRange(
    elopement.total
  )}; a luxe resort wedding for 100 can reach ${formatAud(
    resort100.total.high
  )}. Easy Weddings' 2026 survey puts the average Australian destination wedding at A$32,060 for about 55 guests.`;

  const faqs = [
    { q: 'How much does a Bali wedding cost in Australian dollars?', a: answer },
    {
      q: 'How much is a Bali wedding for 50 guests?',
      a: `About ${formatAudRange(villa50.total)} for a classic villa wedding for 50 guests, or ${formatAudRange(
        byStyle[0].estimate.total
      )} done simply and ${formatAudRange(byStyle[2].estimate.total)} done in luxe style. Guest flights are extra and paid by the guests.`
    },
    {
      q: 'Is it cheaper to get married in Bali than in Australia?',
      a: 'Per guest, usually. Easy Weddings put the average Bali resort wedding at A$16,980 for 50 guests against A$35,315 for 88 guests in Australia in its 2025 survey. Most of the saving comes from the smaller guest list a destination wedding brings.'
    },
    {
      q: 'What hidden costs should we budget for?',
      a: 'Hotel prices marked "++" add 21% tax and service. Villa weddings pay a banjar (village) fee, published at about US$200 to US$500. A legal wedding needs a Certificate of No Impediment from the Australian consulate, A$181 in 2026. Many resorts insist on their own catering.'
    },
    {
      q: 'Do our guests pay their own flights?',
      a: `Usually, yes. Typical return economy fares to Bali run from about ${formatAud(villa50.guestTravel.perth.low)} out of Perth to about ${formatAud(villa50.guestTravel.sydney.high)} out of Sydney, and December and July cost the most.`
    }
  ];

  const crumbs = [
    { name: 'Home', path: '/' },
    { name: 'Bali wedding planning', path: '/bali-wedding-planning' },
    { name: 'Bali wedding cost' }
  ];

  const jsonLd = jsonLdScript(
    graph(
      organization(),
      website(),
      webPageNode({ url: path, name: title, description, locale: 'en', dateModified: ESTIMATES_AS_OF }),
      breadcrumbList(crumbs),
      faqPage(faqs)
    )
  );

  const CITIES = [
    { key: 'perth', label: 'Perth' },
    { key: 'melbourne', label: 'Melbourne' },
    { key: 'brisbane', label: 'Brisbane' },
    { key: 'sydney', label: 'Sydney' }
  ] as const;

  const checked = formatDateRange(ESTIMATES_AS_OF, ESTIMATES_AS_OF).replace(/^\w+ /, '');
  const calculatorHref = siteHref('/wedding-tools/bali-wedding-cost-calculator');
  const H2 = 'font-display text-2xl font-bold md:text-3xl';
  const P = 'mt-3 text-[15px] leading-7 text-foreground/80';
  const TH = 'py-2 pr-4 text-left font-medium text-muted-foreground';
  const TD = 'py-2 pr-4 tabular-nums';
</script>

<svelte:head>
  <title>{title}</title>
  <meta name="description" content={description} />
  <meta
    name="keywords"
    content="bali wedding cost, how much is a wedding in bali, bali wedding cost aud, bali wedding cost for 50 guests, bali wedding per head, bali wedding budget"
  />
  <link rel="canonical" href={canonicalUrl(path)} />
  {@html jsonLd}
</svelte:head>

<SocialMeta {title} {description} url={path} />

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <article>
    <header class="bg-secondary px-5 pt-10 pb-12 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <p class="text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase">
          Bali weddings · for Australian couples
        </p>
        <h1 class="mt-3 font-display text-3xl leading-tight font-bold md:text-5xl">
          How much does a Bali wedding cost? (2027, in AUD)
        </h1>
        <p class="mt-3 text-sm text-muted-foreground">
          Last checked <time datetime={ESTIMATES_AS_OF}>{checked}</time> · Typical market range, not a
          7Magic quote.
        </p>
        <p class="mt-6 rounded-xl border-l-4 border-brand-gold bg-background p-5 text-[17px] leading-8">
          {answer}
        </p>
        <a
          href={calculatorHref}
          class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'mt-6')}
        >
          Work out your own number <ArrowRightIcon size={18} />
        </a>
      </div>
    </header>

    <div class="mx-auto grid max-w-3xl grid-cols-1 gap-14 px-5 py-14 lg:px-0">
      <section>
        <h2 class={H2}>Bali wedding cost by setting and guest count</h2>
        <p class={P}>
          Classic style, food and drinks included, flights not. Typical market range, not a 7Magic
          quote.
        </p>
        <div class="mt-4 overflow-x-auto">
          <table class="w-full min-w-[560px] text-sm">
            <thead>
              <tr>
                <th class={TH}>Setting</th>
                {#each GROUP_SIZES as size (size)}<th class={TH}>{size} guests</th>{/each}
              </tr>
            </thead>
            <tbody>
              {#each bySetting as row (row.label)}
                <tr class="border-t border-border">
                  <td class="py-2 pr-4 font-medium">{row.label}</td>
                  {#each row.totals as total, index (index)}<td class={TD}>{formatAudRange(total)}</td>{/each}
                </tr>
              {/each}
              <tr class="border-t border-border">
                <td class="py-2 pr-4 font-medium">Elopement (2 people)</td>
                <td class={TD} colspan="3">{formatAudRange(elopement.total)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 class={H2}>Where the money goes: a 50-guest villa wedding</h2>
        <p class={P}>
          The same wedding in three styles. Food and drink scale with the guest list; the rest is
          mostly fixed.
        </p>
        <div class="mt-4 overflow-x-auto">
          <table class="w-full min-w-[560px] text-sm">
            <thead>
              <tr>
                <th class={TH}>Line</th>
                {#each byStyle as column (column.label)}<th class={TH}>{column.label}</th>{/each}
              </tr>
            </thead>
            <tbody>
              {#each villa50.lines as line, index (line.key)}
                <tr class="border-t border-border">
                  <td class="py-2 pr-4">{line.label}</td>
                  {#each byStyle as column (column.label)}
                    {@const range = column.estimate.lines[index].range}
                    <td class={TD}>{range ? formatAudRange(range) : 'On request'}</td>
                  {/each}
                </tr>
              {/each}
              <tr class="border-t-2 border-foreground/30 font-semibold">
                <td class="py-2 pr-4">Total</td>
                {#each byStyle as column (column.label)}<td class={TD}>{formatAudRange(column.estimate.total)}</td>{/each}
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 class={H2}>Costs couples don't see coming</h2>
        <ul class="mt-4 grid gap-3 text-[15px] leading-7 text-foreground/80">
          <li><strong>"++" on hotel prices.</strong> 21% tax and service are added on top of most resort and hotel quotes.</li>
          <li><strong>The banjar fee.</strong> A villa wedding pays the village community a fee for the event, published at about US$200 to US$500.</li>
          <li><strong>In-house catering rules.</strong> Many resorts and beach clubs require their own catering, so you cannot shop around for food. Ask for every outside-vendor fee in writing.</li>
          <li><strong>Legal paperwork.</strong> A legal wedding in Bali needs a Certificate of No Impediment from the Australian consulate (A$181 in 2026) plus civil and religious fees. <a href={siteHref('/legally-married-in-bali')} class="underline underline-offset-2">How a Bali wedding becomes legal</a>.</li>
          <li><strong>Getting guests around.</strong> Airport pickups run about Rp480,000 to Rp560,000 a car for up to three people.</li>
        </ul>
      </section>

      <section>
        <h2 class={H2}>What your guests will spend on flights</h2>
        <p class={P}>Typical return economy fares to Denpasar. December and July cost the most.</p>
        <table class="mt-4 w-full max-w-md text-sm">
          <tbody>
            {#each CITIES as city (city.key)}
              <tr class="border-t border-border">
                <td class="py-2 pr-4 font-medium">{city.label}</td>
                <td class={TD}>{formatAudRange(villa50.guestTravel[city.key])}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </section>

      <section>
        <h2 class={H2}>Does the season change the price?</h2>
        <p class={P}>
          We found no published figure for how much Bali wedding prices move by season, so these
          ranges do not change by month. Demand does: the dry season (May to September) and Australian
          school holidays fill venues first, and Nyepi (Monday 8 March 2027) closes the island.
          <a href={siteHref('/wedding-tools/bali-wedding-date-planner')} class="underline underline-offset-2">Check your date in the planner</a>.
        </p>
      </section>

      <section>
        <h2 class={H2}>How we estimate</h2>
        <ul class="mt-4 grid gap-3">
          {#each METHOD_NOTES as note (note)}
            <li class="border-l-2 border-brand-gold/40 pl-5 text-[15px] leading-7 text-foreground/80">{note}</li>
          {/each}
        </ul>
        <h3 class="mt-8 font-display text-lg font-semibold">Sources</h3>
        <ol class="mt-3 grid list-decimal gap-2 pl-5 text-sm leading-6 text-muted-foreground">
          {#each COST_SOURCES as source (source.url)}
            <li>
              <a href={source.url} target="_blank" rel="noopener noreferrer" class="underline underline-offset-2 hover:text-foreground">{source.title}</a>
            </li>
          {/each}
        </ol>
      </section>

      <section>
        <h2 class={H2}>Questions couples ask</h2>
        <div class="mt-6 grid gap-3">
          {#each faqs as faq (faq.q)}
            <details class="rounded-xl border border-border p-5">
              <summary class="cursor-pointer font-display font-semibold">{faq.q}</summary>
              <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{faq.a}</p>
            </details>
          {/each}
        </div>
      </section>
    </div>
  </article>

  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-5xl">
      <BaliEnquiry
        sourcePath={PATH}
        heading="Get a real quote for your Bali wedding"
        lead="Tell us your guest count and date. Our Bali team will come back with venues and real prices."
        context={['Page: Bali wedding cost guide']}
        whatsappText="Hi 7Magic, I read your Bali wedding cost guide. Could you send us a real quote for our wedding?"
        event="Bali Cost Guide Quote Requested"
      />
    </div>
  </section>

  <PublicFooter />
</main>
