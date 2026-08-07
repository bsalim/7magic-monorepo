<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import SearchIcon from '@lucide/svelte/icons/search';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import {
    breadcrumbList,
    graph,
    jsonLdScript,
    organization,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';

  /**
   * Acquisition landing page for Bali destination wedding planning.
   *
   * English only, copy hardcoded — same reasoning as /paket-sangjit and
   * /perjanjian-pranikah: the page changes as one piece, not one string at a
   * time, and the audience is single-language. This one is written for couples
   * abroad planning a Bali wedding remotely, which is why the legal, seasonal
   * and guest-logistics questions get as much room as the pretty parts.
   *
   * Keywords targeted: "bali wedding planner", "wedding planner bali",
   * "bali destination wedding", "plan a wedding in bali", "bali wedding
   * planning services", "bali wedding packages", "getting married in bali".
   *
   * The angle that separates us from the Bali-only planners is the venue
   * catalogue: they recommend from a shortlist, we recommend from a database
   * the couple can browse themselves before they ever write to us. The venue
   * section carries that argument and links into the real search.
   */

  // ---------------------------------------------------------------------------
  // PLACEHOLDER — the `fee` fields are empty on purpose. 7Magic is supplying the
  // planning fee per guest band; until every tier has both a fee and a crew
  // size, the section renders the "quoted on enquiry" panel instead of the
  // ladder, so no invented figure can reach production.
  //
  // When the numbers arrive, also update: the <title>, the meta description,
  // the WhatsApp prefill below, and the "What does the planning fee cover?"
  // FAQ answer — those are the other places a price would need to appear.
  // ---------------------------------------------------------------------------
  const feeTiers = [
    { guests: 'Up to 30 guests', crew: '', fee: '' },
    { guests: '31 – 60 guests', crew: '', fee: '' },
    { guests: '61 – 100 guests', crew: '', fee: '' },
    { guests: '101 – 150 guests', crew: '', fee: '' },
    { guests: '151 guests and over', crew: '', fee: '' }
  ];

  const feesPublished = feeTiers.every((tier) => tier.fee && tier.crew);

  // ---------------------------------------------------------------------------
  // PLACEHOLDER — deposit split, payment schedule, the bookkeeping exchange rate
  // and the refund policy are contract terms, not marketing copy. The section
  // stays hidden until 7Magic confirms them; a guessed term published here is a
  // term we would be held to.
  // ---------------------------------------------------------------------------
  const paymentTerms: string[] = [];

  // Real couples and quotes go here once 7Magic supplies them. Empty on purpose
  // — an invented testimonial on a live site is a fake review.
  const testimonials: { quote: string; names: string; detail: string }[] = [];

  // Figures match the ones published on 7magicwedding.com and /about.
  const stats = [
    { value: '18+', label: 'Years planning weddings' },
    { value: '1000+', label: 'Weddings organised' },
    { value: '100+', label: 'Vendor partners' },
    { value: 'Bali · Jakarta', label: 'Where we work' }
  ];

  const elements = [
    'Ceremony site and reception venue',
    'Catering, bar and tastings',
    'Styling, florals and decoration',
    'Photography and videography',
    'Hair, make-up and bridal preparation',
    'Entertainment, band and MC',
    'Sound, lighting and technical production',
    'Wedding cake and desserts',
    'Guest transport and accommodation',
    'Stationery, favours and the small details',
    'Legal and religious paperwork',
    'Welcome events, rehearsal dinner and recovery brunch'
  ];

  const journey = [
    {
      title: 'Choosing where',
      copy: 'We shortlist venues against your guest count, style and budget, arrange virtual or on-site inspections, pull quotations side by side and check real availability for your dates. You choose the setting knowing what each one is actually like to get married in — including the drawbacks.'
    },
    {
      title: 'Building the team',
      copy: 'Photographers, florists, caterers, bands, celebrants. We introduce the ones who suit your wedding rather than the ones paying for referrals, review every quotation line by line, handle the bookings and stay in the middle of every conversation from then on.'
    },
    {
      title: 'Designing the day',
      copy: 'Our in-house stylist works with you on decoration, florals, lighting, stationery and the way the day feels as your guests move through it. You see the design before it is built, not on the morning it goes up.'
    },
    {
      title: 'Looking after your guests',
      copy: 'Airport arrivals, villa and hotel blocks, transport between events, welcome bags, dietary needs and the family members who need a little more help. Your guests have flown a long way; the logistics should be invisible to them.'
    },
    {
      title: 'Timeline and paperwork',
      copy: 'Detailed run sheets, floor plans, seating charts, vendor call times, rehearsal coordination and the payment schedule that goes with them. Every legal and religious requirement is confirmed in writing well before the date.'
    },
    {
      title: 'The wedding itself',
      copy: 'Our crew is on site from the first delivery to the last guest, running the timeline, briefing vendors and quietly fixing whatever needs fixing. Nobody comes to you with a problem on your wedding day.'
    }
  ];

  const included = [
    'Unlimited planning support over email, WhatsApp, phone and video call',
    'Face-to-face meetings in Bali whenever they are useful',
    'Venue sourcing, inspections and side-by-side quotation comparison',
    'Vendor recommendations, quotations, bookings and coordination',
    'Budget planning and a payment schedule you can plan around',
    'Full wedding timeline and detailed run sheet',
    'Floor plans and seating arrangements',
    'Vendor meetings and all communication on your behalf',
    'Legal and religious document guidance for your nationality',
    'Ceremony rehearsal coordination',
    'Guest accommodation and transport assistance',
    'On-the-day coordination by our full planning crew'
  ];

  const consultation = [
    'A venue shortlist matched to your guest count, style and budget',
    'Preliminary cost estimates for the venues you like — real numbers, not a range',
    'Straight answers on legalities, seasons, logistics and anything you are unsure about',
    'Vendor suggestions where they genuinely help',
    'A second opinion on the ideas you already have'
  ];

  const faqs = [
    {
      q: 'How far ahead should we start planning a Bali wedding?',
      a: 'Twelve months is comfortable and eight is workable. The constraint is rarely us — it is the venue. The clifftop and beachfront properties release dates roughly a year out and the dry-season Saturdays go first. If your date is closer than that, tell us anyway; we will know within a day whether it is still possible and say so plainly.'
    },
    {
      q: 'Can we legally marry in Bali as foreign nationals?',
      a: 'Yes. Indonesian law requires the ceremony to be conducted according to a religion recognised by the state, and the marriage is then registered with the local Civil Registry office. Most foreign couples need a Certificate of No Impediment from their embassy in Indonesia, along with passports, birth certificates and, where relevant, divorce or death certificates. Requirements vary by nationality and by religion, so we confirm exactly what your two passports need in writing before you book anything. Couples who prefer to complete the legal marriage at home and hold a symbolic ceremony in Bali are common, and we plan that just as often.'
    },
    {
      q: 'When is the best time of year to get married in Bali?',
      a: 'The dry season runs roughly April to October and is the safest bet for an outdoor ceremony; July and August are the busiest and priciest months within it. The wet season, November to March, brings short heavy downpours rather than all-day rain, and it buys you better rates and far more availability — as long as the plan includes a covered alternative we can move to within twenty minutes. We build one into every outdoor wedding regardless of season.'
    },
    {
      q: 'Do you only work with the venues listed on this site?',
      a: 'No. The catalogue is where most couples start because it is faster than emailing twenty properties, but we book private villas, beach clubs and estates that are not listed as well. If you have already found somewhere you love, send it to us — we will tell you what we know about it.'
    },
    {
      q: 'Do we need to visit Bali before the wedding?',
      a: 'It helps, but it is not required, and plenty of our couples arrive for the first time a few days before the wedding. We run venue inspections on video call, send photographs and measurements rather than marketing shots, and taste menus on your behalf when you cannot be there. If you do come, we will put the whole trip together around the meetings that matter.'
    },
    {
      q: 'What does the planning fee cover, and what does it not?',
      a: 'The fee covers our planning team and everything we do: sourcing, coordination, design, timeline and the crew who run the wedding day. It does not cover the wedding itself — venue, catering, florals, photography, entertainment and the rest are billed by those vendors at their own rates, which we negotiate and present to you before anything is booked. You will always know which line is ours and which is theirs.'
    },
    {
      q: 'Can you plan a wedding outside Bali?',
      a: 'Yes. 7Magic is based in Jakarta and plans weddings across Indonesia, so a Jakarta reception paired with a Bali ceremony is one team rather than two. We also handle the Chinese-Indonesian pre-wedding traditions and the prenuptial agreement side of things, which most Bali-only planners will refer out.'
    },
    {
      q: 'What happens if we have to move the date?',
      a: 'Talk to us as early as you can. Whether a date can move without cost depends on the individual venue and vendor contracts, and those vary a great deal — some are generous, some are not. We will lay out exactly what each of your bookings allows before you commit to anything, and if the date does have to change we handle the renegotiation.'
    }
  ];

  const budgets = [
    'Under USD 15,000',
    'USD 15,000 – 30,000',
    'USD 30,000 – 60,000',
    'USD 60,000 – 100,000',
    'Over USD 100,000',
    'Still working it out'
  ];

  const weddingTypes = [
    'Intimate ceremony (under 30 guests)',
    'Villa or estate wedding',
    'Resort or hotel wedding',
    'Clifftop or chapel ceremony',
    'Multi-day destination celebration',
    'Symbolic ceremony (legally married elsewhere)',
    'Not sure yet'
  ];

  const waHref = whatsappHref(
    "Hi 7Magic, we're planning a wedding in Bali and would like to book the free consultation."
  );

  // The copy on this page is English whichever locale is active, but the header
  // and footer around it are not — Paraglide serves them in the visitor's
  // locale, and `id` is the base. So the canonical is the /en variant, where
  // the chrome matches the page. Without this, Google indexes an English page
  // wrapped in an Indonesian navigation.
  const CANONICAL_PATH = '/en/bali-wedding-planning';

  const metaTitle = 'Bali Wedding Planner — Full Planning for Destination Weddings | 7Magic';
  const metaDescription =
    'Bali wedding planning from a team with 18 years and 1,000+ weddings behind it. Venue sourcing from our own catalogue, vendor management, design, guest logistics and full wedding-day coordination. Two-week consultation free, no obligation.';

  const pageJsonLd = jsonLdScript(
    graph(
      organization(),
      website(),
      webPageNode({
        url: CANONICAL_PATH,
        name: metaTitle,
        description: metaDescription,
        locale: 'en',
        image: '/img/bali/karma-kandara-bali-wedding-bali2.jpg'
      }),
      breadcrumbList([
        { name: 'Home', path: '/en' },
        { name: 'Bali wedding planning' }
      ]),
      {
        '@type': 'Service',
        serviceType: 'Destination wedding planning',
        provider: { '@id': 'https://7magicwedding.com/#organization' },
        areaServed: { '@type': 'Place', name: 'Bali, Indonesia' },
        description:
          'Full-service wedding planning for couples marrying in Bali: venue sourcing, vendor management, design, guest logistics, timeline and on-the-day coordination.'
      },
      {
        '@type': 'FAQPage',
        mainEntity: faqs.map((faq) => ({
          '@type': 'Question',
          name: faq.q,
          acceptedAnswer: { '@type': 'Answer', text: faq.a }
        }))
      }
    )
  );

  let sending = $state(false);
  let submitted = $state(false);
  let errorMessage = $state('');

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (sending) return;

    const form = event.currentTarget as HTMLFormElement;
    const data = new FormData(form);
    const field = (key: string) => String(data.get(key) ?? '').trim();

    // The contact-lead schema has no wedding-specific columns, so the
    // qualifying answers are folded into the message body — same approach as
    // /bali-event-organizer. Sales reads them there.
    const message = [
      `Wedding type: ${field('wedding_type') || '—'}`,
      `Target date: ${field('wedding_date') || '—'}`,
      `Guests: ${field('guests') || '—'}`,
      `Budget: ${field('budget') || '—'}`,
      `Travelling from: ${field('country') || '—'}`,
      `Venue in mind: ${field('venue') || '—'}`,
      '',
      field('notes') || 'No extra notes.'
    ].join('\n');

    sending = true;
    errorMessage = '';

    try {
      const response = await fetch('/api/contact-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: field('name'),
          phone: field('phone'),
          email: field('email') || undefined,
          message,
          source_path: '/bali-wedding-planning'
        })
      });

      if (!response.ok) {
        errorMessage = 'That did not send. Try again, or message us on WhatsApp instead.';
        return;
      }

      submitted = true;
      form.reset();
    } catch {
      errorMessage = 'That did not send. Try again, or message us on WhatsApp instead.';
    } finally {
      sending = false;
    }
  }

  const inputClass =
    'rounded-md border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30';
</script>

<svelte:head>
  <title>{metaTitle}</title>
  <meta name="description" content={metaDescription} />
  <meta
    name="keywords"
    content="bali wedding planner, wedding planner bali, bali destination wedding, plan a wedding in bali, bali wedding planning services, getting married in bali, bali wedding venues"
  />
  <link rel="canonical" href="https://7magicwedding.com{CANONICAL_PATH}" />
  {@html pageJsonLd}
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[660px]">
    <img
      src="/img/bali/karma-kandara-bali-wedding-bali2.jpg"
      alt="A couple exchanging vows under a flower arch on a clifftop pool deck above the ocean in Bali"
      class="absolute inset-0 h-full w-full object-cover object-[58%_42%]"
      fetchpriority="high"
    />
    <!-- Contrast comes from a left-side gradient and a shadow on the text, not
         from dimming the whole photo — the ocean stays at full brightness. -->
    <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/40 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          Wedding planning · Bali
        </p>
        <!-- Each sentence is its own block so the line always breaks at the full
             stop. Left to wrap on its own the break lands after "We’ll". -->
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.4rem]">
          <span class="block">Get married in Bali.</span>
          <span class="block">We’ll handle the rest.</span>
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/90">
          Eighteen years, more than a thousand weddings, and a venue catalogue we built ourselves
          rather than borrowed. From the first call to the last song, one team carries every
          decision — you only have to say yes to the good ideas.
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a href="#consultation" class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
            Book a free consultation
          </a>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'border border-white/30 bg-white/10 px-7 text-white backdrop-blur hover:bg-white hover:text-brand-ink'
            )}
          >
            <MessageCircleIcon size={18} />
            Ask us on WhatsApp
          </a>
        </div>

        <p class="mt-5 text-sm text-white/90">
          Two weeks of real planning work before you pay anything. No deposit, no obligation.
        </p>
      </div>
    </div>
  </section>

  <!-- Trust strip -->
  <section class="border-b border-border bg-brand-ink px-5 py-6 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {#each stats as stat}
        <div>
          <p class="font-display text-2xl font-bold text-brand-dark-accent">{stat.value}</p>
          <p class="mt-1 text-sm text-white/72">{stat.label}</p>
        </div>
      {/each}
    </div>
  </section>

  <!-- Why us -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          Why couples hand it to us
        </p>
        <h2 class="mt-3 max-w-xl font-display text-3xl font-bold md:text-4xl">
          The planning year should be as good as the day itself
        </h2>
        <div class="mt-5 grid max-w-xl gap-5 text-[15px] leading-7 text-muted-foreground">
          <p>
            A destination wedding ought to be one of the best years of your life rather than the
            most stressful one. The stress almost always comes from the same place: you are making
            expensive decisions about somewhere you cannot walk around, with people you have never
            met, in a language you do not speak.
          </p>
          <p>
            That is the part we take off you. 7Magic has been planning weddings for eighteen years
            and more than a thousand couples, in Bali and across Indonesia. We know which lawns get
            the wind in August, which caterer serves what was on the tasting menu, and which villa
            says it seats a hundred and twenty but seats ninety comfortably. You get the honest
            answer early, while it can still change the outcome — not an apology afterwards.
          </p>
          <p>
            You will have one planner who knows your wedding, not a shared inbox. They answer in
            your waking hours, they tell you when an idea will not work, and they are standing at
            the back of the room on the day making sure it does.
          </p>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <img
          src="/img/bali/chaple-lawn-ritz-carlton-bali1.jpeg"
          alt="A glass chapel in Bali set up for a ceremony, looking out over the sea"
          loading="lazy"
          class="h-72 w-full rounded-md object-cover sm:col-span-2"
        />
        <img
          src="/img/bali/skybar-mulia-bali1.jpg"
          alt="A beachfront resort terrace in Bali, lounge seating between the pools and the sea"
          loading="lazy"
          class="h-56 w-full rounded-md object-cover"
        />
        <img
          src="/img/bali/merusaka-wedding-bali1.jpg"
          alt="A garden wedding reception in Bali being set up, blossom trees lining the aisle and banquet tables on the lawn"
          loading="lazy"
          class="h-56 w-full rounded-md object-cover"
        />
      </div>
    </div>
  </section>

  <!-- Everything we handle -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        Full-service planning
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Every part of the wedding, handled in one place
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        You can hand us the whole wedding or the parts you would rather not deal with. Either way
        the list below is ours to source, negotiate, book and run.
      </p>

      <div class="mt-10 grid gap-x-8 gap-y-3 sm:grid-cols-2 lg:grid-cols-3">
        {#each elements as element}
          <div class="flex gap-3 border-b border-border/70 pb-3 text-[15px] leading-7">
            <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
            <span>{element}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- The venue catalogue — the argument against a shortlist-based planner -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
      <img
        src="/img/bali/conrad-bali3.jpg"
        alt="A couple walking past an A-frame glass wedding chapel in Bali, mirrored in the reflecting pool in front of it"
        loading="lazy"
        class="h-[420px] w-full rounded-md object-cover"
      />

      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          Venue sourcing
        </p>
        <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
          We are not recommending venues from memory
        </h2>
        <div class="mt-5 grid gap-5 text-[15px] leading-7 text-muted-foreground">
          <p>
            Most planners work from a shortlist of the venues they happen to have worked with. We
            work from a catalogue. Every Bali property we book is published on this site with its
            real capacity, real photographs and current pricing, and you can go through it yourself
            before you ever write to us.
          </p>
          <p>
            Bring us the three you like. We will tell you which one photographs badly at four in
            the afternoon, which one charges separately for the things you assumed were included,
            and which one is worth the extra money. Then we check availability, put the quotations
            side by side and negotiate the contract.
          </p>
        </div>

        <a
          href="/wedding-venue/search?city=bali"
          class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'mt-7 px-6')}
        >
          <SearchIcon size={17} />
          Browse Bali wedding venues
        </a>
      </div>
    </div>
  </section>

  <!-- Planning journey -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        How we plan
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Six stages, from the first call to the last song
      </h2>

      <div class="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {#each journey as stage, index}
          <div class="rounded-md border border-border bg-background p-6">
            <span class="font-display text-3xl font-bold text-brand-warm-deep">
              {String(index + 1).padStart(2, '0')}
            </span>
            <h3 class="mt-3 font-display text-lg font-semibold">{stage.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{stage.copy}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Planning fee -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      Planning fee
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      One fee, scaled to the size of your wedding
    </h2>
    <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
      Our fee covers the planning from the day you engage us until the last guest leaves. Every
      wedding gets a dedicated planner, unlimited support, the full timeline and run sheet, vendor
      coordination throughout, and a crew on site for the day itself — the crew grows with your
      guest list.
    </p>

    {#if feesPublished}
      <div class="mt-10 overflow-x-auto">
        <table class="w-full min-w-[36rem] border-collapse text-left">
          <thead>
            <tr class="border-b border-border">
              <th class="py-3 pr-6 text-sm font-semibold uppercase tracking-widest text-muted-foreground">
                Guest count
              </th>
              <th class="py-3 pr-6 text-sm font-semibold uppercase tracking-widest text-muted-foreground">
                Crew on the day
              </th>
              <th class="py-3 text-sm font-semibold uppercase tracking-widest text-muted-foreground">
                Planning fee
              </th>
            </tr>
          </thead>
          <tbody>
            {#each feeTiers as tier}
              <tr class="border-b border-border/70">
                <td class="py-4 pr-6 text-[15px]">{tier.guests}</td>
                <td class="py-4 pr-6 text-[15px] text-muted-foreground">{tier.crew}</td>
                <td class="py-4 font-display text-lg font-semibold">{tier.fee}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="mt-10 rounded-md border border-border bg-secondary p-7">
        <h3 class="font-display text-xl font-semibold">Quoted on enquiry</h3>
        <p class="mt-3 max-w-2xl text-[15px] leading-7 text-muted-foreground">
          The fee is set by your guest count and the crew size the day needs. Tell us roughly how
          many people you expect and we will send the figure in writing during your free
          consultation, before you commit to anything — along with an estimate for the wedding
          itself, so you can see both numbers together.
        </p>
        <div class="mt-6 grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
          {#each feeTiers as tier}
            <div class="flex gap-3 text-[15px] leading-7">
              <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
              <span>{tier.guests}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <div class="mt-8 rounded-md border border-border bg-brand-gold-soft p-6">
      <h3 class="font-display text-base font-semibold">What the fee does not cover</h3>
      <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
        The wedding itself. Venue, catering, florals, photography, entertainment and the rest are
        billed by those vendors at their own rates, which we negotiate on your behalf and present
        to you before anything is booked. You will always be able to see which line is ours and
        which is theirs.
      </p>
    </div>
  </section>

  <!-- What's included -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <h2 class="max-w-2xl font-display text-3xl font-bold md:text-4xl">
        What the planning service includes
      </h2>

      <div class="mt-10 grid gap-x-8 gap-y-3 sm:grid-cols-2">
        {#each included as item}
          <div class="flex gap-3 text-[15px] leading-7">
            <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
            <span>{item}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Free consultation -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          Getting started
        </p>
        <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
          Two weeks to decide, before you pay anything
        </h2>
        <div class="mt-5 grid gap-5 text-[15px] leading-7 text-muted-foreground">
          <p>
            Choosing a planner is a big decision to make over email with someone on the other side
            of the world, so we do not ask for a deposit to start talking. Send us an enquiry and
            you get two weeks of real planning work, free and with nothing owed at the end of it.
          </p>
        </div>

        <div class="mt-7 grid gap-2.5">
          {#each consultation as item}
            <div class="flex gap-3 text-[15px] leading-7">
              <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
              <span>{item}</span>
            </div>
          {/each}
        </div>

        <p class="mt-7 max-w-xl text-[15px] leading-7 text-muted-foreground">
          At the end of the fortnight you will know what your Bali wedding actually looks like and
          roughly what it costs. If we are the right planner for you, we will take it from there.
          If we are not, the shortlist is yours to keep.
        </p>
      </div>

      <img
        src="/img/bali/arya-duta-chapel-bali.jpg"
        alt="A lit arched wedding chapel and reflecting pool at a Bali resort at dusk"
        loading="lazy"
        class="h-[440px] w-full rounded-md object-cover"
      />
    </div>
  </section>

  {#if paymentTerms.length}
    <section class="bg-secondary px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-4xl">
        <h2 class="font-display text-3xl font-bold md:text-4xl">Payment terms</h2>
        <div class="mt-8 grid gap-2.5">
          {#each paymentTerms as term}
            <div class="flex gap-3 text-[15px] leading-7">
              <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
              <span>{term}</span>
            </div>
          {/each}
        </div>
      </div>
    </section>
  {/if}

  {#if testimonials.length}
    <section class="bg-secondary px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <h2 class="font-display text-3xl font-bold md:text-4xl">Couples we have planned for</h2>
        <div class="mt-10 grid gap-5 md:grid-cols-3">
          {#each testimonials as item}
            <figure class="rounded-md border border-border bg-background p-6">
              <blockquote class="text-[15px] leading-7">{item.quote}</blockquote>
              <figcaption class="mt-4 text-sm font-semibold">
                {item.names}
                <span class="block font-normal text-muted-foreground">{item.detail}</span>
              </figcaption>
            </figure>
          {/each}
        </div>
      </div>
    </section>
  {/if}

  <!-- FAQ -->
  <section class="mx-auto max-w-4xl px-5 py-16 lg:px-8">
    <h2 class="font-display text-3xl font-bold md:text-4xl">Questions couples ask us first</h2>
    <div class="mt-8 grid gap-3">
      {#each faqs as faq}
        <details class="group rounded-md border border-border bg-background p-6">
          <summary class="cursor-pointer list-none font-display text-lg font-semibold marker:hidden">
            {faq.q}
          </summary>
          <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{faq.a}</p>
        </details>
      {/each}
    </div>
  </section>

  <!-- Lead form -->
  <section id="consultation" class="scroll-mt-20 bg-brand-ink px-5 py-16 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.85fr_1.15fr]">
      <div>
        <h2 class="font-display text-3xl font-bold md:text-4xl">Book your free consultation</h2>
        <p class="mt-4 text-[15px] leading-7 text-white/75">
          Tell us the date, the rough guest count and what you have in mind. A planner reads it —
          not a bot — and comes back with venue options and honest numbers. Nothing is owed for
          the first fortnight.
        </p>

        <div class="mt-8 rounded-md border border-white/15 bg-white/5 p-6">
          <p class="text-sm text-white/70">Would rather just chat?</p>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'mt-3 w-full bg-brand-success text-white hover:bg-brand-success-hover'
            )}
          >
            <MessageCircleIcon size={18} />
            WhatsApp {whatsappDisplay}
          </a>
        </div>
      </div>

      <div class="rounded-md bg-background p-7 text-foreground">
        {#if submitted}
          <div class="flex flex-col items-center gap-4 py-12 text-center">
            <span class="flex size-14 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover">
              <CheckIcon size={28} />
            </span>
            <h3 class="font-display text-xl font-semibold">Thank you — that reached us</h3>
            <p class="max-w-sm text-[15px] leading-7 text-muted-foreground">
              A planner will reply within one working day, usually sooner. If your date is close,
              message us on WhatsApp and we will move faster.
            </p>
            <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-2')}>
              <MessageCircleIcon size={17} />
              Message us on WhatsApp
            </a>
          </div>
        {:else}
          <form onsubmit={submit} class="grid gap-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="bw-type" class="text-[13px] font-medium">
                  What you have in mind <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <select id="bw-type" name="wedding_type" required class={inputClass}>
                  <option value="">Choose one</option>
                  {#each weddingTypes as type}
                    <option value={type}>{type}</option>
                  {/each}
                </select>
              </div>
              <div class="grid gap-1.5">
                <label for="bw-date" class="text-[13px] font-medium">
                  Wedding date <span class="text-muted-foreground">(a rough one is fine)</span>
                </label>
                <input id="bw-date" name="wedding_date" type="date" class={inputClass} />
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="bw-guests" class="text-[13px] font-medium">
                  Guests <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="bw-guests"
                  name="guests"
                  type="number"
                  min="1"
                  required
                  placeholder="e.g. 60"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="bw-budget" class="text-[13px] font-medium">Total wedding budget</label>
                <select id="bw-budget" name="budget" class={inputClass}>
                  <option value="">Prefer not to say</option>
                  {#each budgets as budget}
                    <option value={budget}>{budget}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="bw-name" class="text-[13px] font-medium">
                  Your name <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input id="bw-name" name="name" required autocomplete="name" class={inputClass} />
              </div>
              <div class="grid gap-1.5">
                <label for="bw-country" class="text-[13px] font-medium">Travelling from</label>
                <input
                  id="bw-country"
                  name="country"
                  autocomplete="country-name"
                  placeholder="e.g. Australia"
                  class={inputClass}
                />
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="bw-email" class="text-[13px] font-medium">
                  Email <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="bw-email"
                  name="email"
                  type="email"
                  required
                  autocomplete="email"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="bw-phone" class="text-[13px] font-medium">
                  WhatsApp <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="bw-phone"
                  name="phone"
                  required
                  autocomplete="tel"
                  placeholder="Include your country code"
                  class={inputClass}
                />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="bw-venue" class="text-[13px] font-medium">
                Venue in mind <span class="text-muted-foreground">(optional)</span>
              </label>
              <input
                id="bw-venue"
                name="venue"
                placeholder="A property from our catalogue, or somewhere you found yourself"
                class={inputClass}
              />
            </div>

            <div class="grid gap-1.5">
              <label for="bw-notes" class="text-[13px] font-medium">
                Anything else we should know?
              </label>
              <textarea
                id="bw-notes"
                name="notes"
                rows="3"
                placeholder="Legal or symbolic ceremony, religious requirements, guests needing extra help, ideas you already love"
                class={inputClass}
              ></textarea>
            </div>

            {#if errorMessage}
              <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
            {/if}

            <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending}>
              {sending ? 'Sending…' : 'Book my free consultation'}
            </Button>
            <p class="text-center text-xs text-muted-foreground">
              We use your details to answer this enquiry and nothing else.
            </p>
          </form>
        {/if}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
