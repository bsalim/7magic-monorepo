<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import CheckIcon from '@lucide/svelte/icons/check';
  import { CONCIERGE_GROUPS, CONCIERGE_SERVICES, type ConciergeKey } from '$lib/bali-concierge';
  import BaliEnquiry from '$lib/components/bali/BaliEnquiry.svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import { buttonVariants } from '$lib/components/ui/button';
  import { englishPath, siteHref } from '$lib/seo/english-only';
  import { canonicalUrl, landingPageJsonLd } from '$lib/seo/schema';
  import { cn } from '$lib/utils';

  /**
   * The Bali wedding concierge: everything around the wedding that couples
   * planning from Australia, and their guests, need on the ground.
   *
   * Only the services 7Magic's Bali team confirmed it can deliver
   * (`$lib/bali-concierge`), and no prices: each is quoted on request. A couple
   * ticks what they want and the WhatsApp message and enquiry carry the list.
   */

  const PATH = '/bali-wedding-concierge';
  const path = englishPath(PATH);
  const title = 'Bali Wedding Concierge: Guest Transport, Villas, Spa & Paperwork | 7Magic';
  const description =
    'One team for everything around your Bali wedding: legal paperwork, airport pickups and guest shuttles, accommodation blocks, a private car and driver, Balinese massage, a private chef, babysitting and more.';

  // The English URL of the prewedding article, read from the live sitemap:
  // article slugs are translated content, not routing.
  const PREWEDDING_ARTICLE = '/en/articles/photography/unique-prewedding-locations-bali';

  let chosen = $state<ConciergeKey[]>([]);
  const chosenNames = $derived(
    CONCIERGE_SERVICES.filter((service) => chosen.includes(service.key)).map((s) => s.name)
  );
  const helpLine = $derived(
    chosenNames.length ? `I'd like help with: ${chosenNames.join(', ')}` : 'I’d like help with our Bali wedding'
  );
  const whatsappText = $derived(`Hi 7Magic, ${helpLine}.`);

  const faqs = [
    {
      q: 'What does a Bali wedding concierge do?',
      a: 'Everything around the wedding itself: the legal paperwork, getting your guests from the airport to their rooms and to the venue, villas or a block of hotel rooms, and the things that make the week easy, from a car and driver to an in-villa massage or a babysitter on the wedding night.'
    },
    {
      q: 'Do you only help couples who book their wedding with 7Magic?',
      a: 'Tell us what you need. The concierge is built around weddings we plan, and we will tell you straight away what we can arrange if your wedding is with someone else.'
    },
    {
      q: 'How much does the concierge cost?',
      a: 'Each service is quoted for your dates, group size and location. For typical market prices of the add-ons, see the Bali wedding cost calculator.'
    },
    {
      q: 'Can you look after our guests as well as us?',
      a: 'Yes, that is most of the work: airport pickups matched to flights, shuttles on the day, accommodation near the venue, an arrival guide, and activities for the days around the wedding.'
    }
  ];

  const jsonLd = landingPageJsonLd({
    path,
    title,
    description,
    locale: 'en',
    crumbs: [
      { name: 'Home', path: '/' },
      { name: 'Bali wedding planning', path: '/bali-wedding-planning' },
      { name: 'Bali wedding concierge' }
    ],
    service: {
      name: 'Bali wedding concierge',
      serviceType: 'Wedding concierge',
      description,
      areaServed: ['Bali']
    },
    faqs
  });

  const H2 = 'font-display text-2xl font-bold md:text-3xl';
</script>

<svelte:head>
  <title>{title}</title>
  <meta name="description" content={description} />
  <meta
    name="keywords"
    content="bali wedding concierge, bali wedding guest transport, private driver bali wedding, bali villa concierge wedding, bali wedding guest accommodation"
  />
  <link rel="canonical" href={canonicalUrl(path)} />
  {@html jsonLd}
</svelte:head>

<SocialMeta {title} {description} url={path} />

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <header class="bg-secondary px-5 pt-10 pb-12 lg:px-8">
    <div class="mx-auto max-w-4xl">
      <p class="text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase">
        Bali weddings · for Australian couples
      </p>
      <h1 class="mt-3 font-display text-3xl leading-tight font-bold md:text-5xl">
        Your Bali wedding concierge
      </h1>
      <p class="mt-4 max-w-2xl text-base leading-7 text-muted-foreground md:text-lg md:leading-8">
        One team on the ground for everything around the wedding: the paperwork, your guests, and
        the week itself. Tick what you'd like and send it to us; each service is quoted for your
        dates.
      </p>
    </div>
  </header>

  <section class="px-5 py-14 lg:px-8">
    <fieldset class="mx-auto grid max-w-6xl gap-10">
      <legend class="sr-only">Choose what you'd like help with</legend>
      {#each CONCIERGE_GROUPS as group (group.key)}
        <div>
          <h2 class={H2}>{group.title}</h2>
          <div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {#each CONCIERGE_SERVICES.filter((service) => service.group === group.key) as service (service.key)}
              <label
                class="relative flex cursor-pointer flex-col gap-1.5 rounded-xl border border-border bg-background p-5 transition hover:border-brand-gold/60 has-checked:border-brand-gold has-checked:bg-brand-gold-soft has-focus-visible:ring-3 has-focus-visible:ring-ring/40"
              >
                <input type="checkbox" value={service.key} bind:group={chosen} class="sr-only" />
                <span class="flex items-start justify-between gap-3 font-display font-semibold">
                  {service.name}
                  <span
                    class={cn(
                      'flex size-5 shrink-0 items-center justify-center rounded-full border',
                      chosen.includes(service.key)
                        ? 'border-brand-gold bg-brand-gold text-white'
                        : 'border-border text-transparent'
                    )}
                    aria-hidden="true"><CheckIcon size={13} /></span
                  >
                </span>
                <span class="text-[15px] leading-6 text-muted-foreground">{service.blurb}</span>
                {#if service.key === 'prewedding'}
                  <a href={PREWEDDING_ARTICLE} class="mt-1 text-sm text-brand-gold-hover underline underline-offset-2">
                    15 unique prewedding locations in Bali
                  </a>
                {:else if service.key === 'legal'}
                  <a href={siteHref('/legally-married-in-bali')} class="mt-1 text-sm text-brand-gold-hover underline underline-offset-2">
                    How a Bali wedding becomes legal
                  </a>
                {/if}
              </label>
            {/each}
          </div>
        </div>
      {/each}
    </fieldset>

    <div class="mx-auto mt-10 flex max-w-6xl flex-wrap items-center gap-4">
      <p class="text-sm text-muted-foreground" aria-live="polite">
        {chosenNames.length ? `${chosenNames.length} selected` : 'Nothing selected yet'}
      </p>
      <a
        href={siteHref('/wedding-tools/bali-wedding-cost-calculator')}
        class={cn(buttonVariants({ variant: 'outline' }))}
      >
        Add these to a cost estimate <ArrowRightIcon size={16} />
      </a>
    </div>
  </section>

  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-5xl">
      <BaliEnquiry
        sourcePath={PATH}
        heading="Tell us what you need"
        lead="Send your list and your dates. Our Bali team will come back with what we can arrange and a quote."
        context={[helpLine]}
        {whatsappText}
        event="Bali Concierge Requested"
      />
    </div>
  </section>

  <section class="px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-3xl">
      <h2 class={H2}>Questions couples ask</h2>
      <div class="mt-6 grid gap-3">
        {#each faqs as faq (faq.q)}
          <details class="rounded-xl border border-border p-5">
            <summary class="cursor-pointer font-display font-semibold">{faq.q}</summary>
            <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{faq.a}</p>
          </details>
        {/each}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
