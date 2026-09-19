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
  import { localizeHref } from '$lib/paraglide/runtime';

  /**
   * Acquisition landing page for Singapore weddings, and the first page that
   * introduces the ALL Access partnership — same shape as
   * /bali-wedding-planning, English only, for the same reason: the page
   * changes as one piece, not one string at a time.
   *
   * Keywords targeted: "wedding planner singapore", "wedding planning
   * singapore", "singapore wedding planner", "plan a wedding in singapore",
   * "wedding day concierge singapore".
   *
   * The angle: 7Magic plans the wedding, the way it always has. ALL Access —
   * a separate Singapore company, our technology partner — runs the day
   * itself: guest check-in, the seating plan, the dietary list the kitchen
   * works from. Two companies, named as two companies, nowhere implied to be
   * one.
   */

  // Figures match the ones published on 7magicwedding.com and /about.
  const stats = [
    { value: '18+', label: 'Years of experience' },
    { value: '1000+', label: 'Weddings organised' },
    { value: '100+', label: 'Vendor partners' },
    { value: 'Jakarta · Bali · Singapore', label: 'Where we work' }
  ];

  const included = [
    'Unlimited planning support over email, WhatsApp, phone and video call',
    'Face-to-face meetings at our Singapore office whenever they are useful',
    'Venue sourcing, inspections and side-by-side quotation comparison',
    'Vendor recommendations, quotations, bookings and coordination',
    'Budget planning and a payment schedule you can plan around',
    'Full wedding timeline and detailed run sheet',
    'Floor plans and seating arrangements',
    'Vendor meetings and all communication on your behalf',
    'Marriage paperwork guidance, including the Registry of Marriages notice',
    'Ceremony rehearsal coordination',
    'Your wedding day run on the ALL Access concierge platform, arranged as part of your planning',
    'On-the-day coordination by our full planning crew'
  ];

  const journey = [
    {
      title: 'Choosing where',
      copy: 'We shortlist venues against your guest count, style and budget, arrange inspections, pull quotations side by side and check real availability for your date. You choose the setting knowing what each one is actually like to get married in.'
    },
    {
      title: 'Building the team',
      copy: 'Photographers, florists, caterers, celebrants. We introduce the ones who suit your wedding, review every quotation line by line, handle the bookings and stay in the middle of every conversation from then on.'
    },
    {
      title: 'Designing the day',
      copy: 'Our in-house stylist works with you on decoration, florals, lighting, stationery and the way the day feels as your guests move through it. You see the design before anything is built.'
    },
    {
      title: 'Looking after your guests',
      copy: 'Transport between the ceremony and the reception, welcome details, dietary needs and the out-of-town family who need a little more help. Give us the guest list and we work out who needs what.'
    },
    {
      title: 'Timeline and paperwork',
      copy: 'Detailed run sheets, floor plans, seating charts, vendor call times, rehearsal coordination and the payment schedule that goes with them. We help you plan around the Registry of Marriages notice period well ahead of the date.'
    },
    {
      title: 'The wedding itself',
      copy: 'Our crew is on site from the first delivery to the last guest, running the timeline and briefing vendors. Guests check themselves in from their phone on the ALL Access platform, your team watches the room fill in real time, and problems go to us, not to you.'
    }
  ];

  const consultation = [
    'A venue shortlist matched to your guest count, style and budget',
    'Preliminary cost estimates for the venues you like, with real numbers rather than a range',
    'Straight answers on paperwork, timelines, logistics and anything you are unsure about',
    'Vendor suggestions where they genuinely help',
    'A second opinion on the ideas you already have'
  ];

  // Subset of ALL Access's own feature list (allaccess.sg), described as what
  // changes on the wedding day once a 7Magic wedding runs on their platform.
  const dayOfFeatures = [
    {
      num: 'I',
      title: 'Self check-in',
      body: 'Guests find their name, confirm and see their table on their own phone. No queue, no clipboard, no one asking where to sit.'
    },
    {
      num: 'II',
      title: 'Live arrivals',
      body: 'Your planner and the venue staff watch the room fill by the minute: who is in, who is late, who never replied.'
    },
    {
      num: 'III',
      title: 'Seating that holds',
      body: 'Move a guest and the floor plan, the guest’s phone and the printed place card all update.'
    },
    {
      num: 'IV',
      title: 'Dietary, counted',
      body: 'Allergies and preferences tally themselves into a kitchen list your caterer can actually read.'
    },
    {
      num: 'V',
      title: 'Place cards',
      body: 'Folded tent cards, printed straight from the seated list. No retyping a single name the night before.'
    }
  ];

  // Real Singapore-dollar pricing from ALL Access's own brochure
  // (apps/website-sg/src/lib/content/shared.ts, PRICES). Billed by ALL
  // Access, not by 7Magic — arranged as part of your wedding by your 7Magic
  // planner, same as any other vendor booking.
  const conciergePackages = [
    {
      tier: 'Essential Access',
      price: 'S$199',
      lead: 'Everything a guest touches between the door and their seat.',
      specs: [
        'Self check-in from the guest’s own phone',
        'Live arrivals dashboard for your planner and the desk',
        'Seating plan, place cards and dietary list, all reading from one list'
      ]
    },
    {
      tier: 'Ultimate Luxury',
      price: 'S$499',
      lead: 'Everything in Essential Access, plus the room’s big screen.',
      specs: [
        'All Essential Access features',
        'Interactive screen for wishes and photos as guests send them',
        'Guest photos and videos synced to your Google Drive that night'
      ]
    }
  ];

  // ALL Access's own add-on catalogue and its Singapore-dollar pricing
  // (apps/website-sg/src/lib/content/en.ts, addOnGroups). Each sits on top of
  // whichever core platform tier is booked above; billed by ALL Access, same
  // as the core tiers.
  const addOnGroups = [
    {
      title: 'Afterparty & entertainment',
      items: [
        {
          name: 'Afterparty live DJ performance',
          price: '+ S$600 to S$999',
          detail: 'A two-to-three-hour live DJ set with professional sound, for a gala or wedding party.'
        },
        {
          name: 'Live song request integration',
          price: '+ S$150',
          detail: 'Guests send their favourite tracks straight to the DJ’s screen from their phone.'
        }
      ]
    },
    {
      title: 'Visuals, décor & galleries',
      items: [
        {
          name: 'Digital pre-wedding & story gallery',
          price: '+ S$79',
          detail: 'An aesthetic photo gallery and the couple’s love story, browsable on every guest’s phone.'
        },
        {
          name: 'Frosted acrylic QR standee',
          price: '+ S$89 to S$149',
          detail: 'A luxury frosted acrylic master QR board, with a custom bride and groom illustration.'
        },
        {
          name: 'Custom monogram & UI theme',
          price: '+ S$99',
          detail: 'The guest app styled entirely to your event’s theme and colour palette.'
        }
      ]
    },
    {
      title: 'Crowd engagement & experience',
      items: [
        {
          name: 'Live trivia, games & voting hub',
          price: '+ S$99 to S$149',
          detail: 'An interactive quiz, best-dressed voting and live polls on the main screen.'
        },
        {
          name: 'Digital lucky draw & souvenir drop',
          price: '+ S$79 to S$129',
          detail: 'A digital door-prize spin wheel, with thank-you cards and vouchers sent automatically.'
        },
        {
          name: 'VIP table butler call',
          price: '+ S$120 to S$199',
          detail: 'A dedicated VVIP table service call, routed straight to the planner’s team on their phones.'
        }
      ]
    },
    {
      title: 'Corporate & analytics',
      items: [
        {
          name: 'Post-event data & engagement report',
          price: '+ S$149 to S$250',
          detail: 'A full PDF report: peak entry times, guest demographics and engagement metrics.'
        }
      ]
    }
  ];

  const bundle = {
    heading: 'The ultimate all-in-one bundle',
    lead: 'The complete package: the Ultimate Luxury platform with a live DJ set, song requests, the digital gallery, the games hub and a custom frosted standee.',
    includes: ['Ultimate Luxury', 'Live DJ set', 'Song request', 'Digital gallery', 'Games hub', 'Custom standee'],
    price: 'S$1,399++',
    saving: 'Save up to S$300'
  };

  const faqs: { q: string; a: string; sources?: { label: string; href: string }[] }[] = [
    {
      q: 'Do you plan weddings in Singapore, or only Bali and Jakarta?',
      a: 'Yes, we plan Singapore weddings. We work from our Singapore office alongside the Jakarta and Bali team. For the wedding day itself we partner with ALL Access, a Singapore concierge technology company, for guest check-in and seating.'
    },
    {
      q: 'Is your Singapore team licensed to work in Singapore?',
      a: 'Yes. Everyone on the 7Magic team who works on Singapore weddings is licensed and legally authorised to work in Singapore.'
    },
    {
      q: 'What is ALL Access, and is it part of 7Magic?',
      a: 'ALL Access is a separate Singapore company that makes concierge software for weddings and events. It is not part of 7Magic. We partner with them for what guests use on the day: self check-in, table reveal, live arrivals, and seating and dietary lists that stay in sync. Planning stays with 7Magic throughout.'
    },
    {
      q: 'What does the planning fee cover, and is ALL Access included in it?',
      a: 'The planning fee covers our team’s work up to the day: sourcing, coordination, design and the timeline. ALL Access is billed separately by ALL Access, at S$199 for Essential Access or S$499 for Ultimate Luxury. Your 7Magic planner arranges it for you, the way we arrange a photographer or a florist.'
    },
    {
      q: 'How does the legal side of getting married in Singapore work?',
      a: 'A civil marriage starts with a Notice of Marriage filed with the Registry of Marriages, followed by a minimum waiting period before the solemnisation. The rules are set out in the Women’s Charter. We build the notice into your run sheet early. Nationality, earlier marriages and religious ceremonies can each add a step, so confirm the current requirements with the Registry.',
      sources: [
        { label: 'Registry of Marriages', href: 'https://www.rom.gov.sg' },
        { label: 'Women’s Charter 1961, Singapore Statutes Online', href: 'https://sso.agc.gov.sg/act/wc1961' }
      ]
    },
    {
      q: 'How far ahead should we start planning?',
      a: 'Twelve months is comfortable and six is workable for most Singapore weddings. The limit is usually the venue, since popular ballrooms and gardens can be booked out for Saturdays well ahead. Tell us your date anyway and we will say quickly whether it is still possible.'
    },
    {
      q: 'Can 7Magic still plan a Bali wedding for us if we live in Singapore?',
      a: 'Yes. A Singapore reception with a Bali ceremony, or the whole wedding in one city, is handled by one planning team. See our Bali wedding planning page for that side of it.'
    },
    {
      q: 'What happens if we have guests flying in from out of town?',
      a: 'We coordinate transport between events and flag anyone who needs extra help. With ALL Access your planner also sees who has arrived, so a delayed flight shows up as a late check-in rather than an empty seat.'
    }
  ];

  const budgets = [
    'Under S$30,000',
    'S$30,000 – 60,000',
    'S$60,000 – 100,000',
    'S$100,000 – 150,000',
    'Over S$150,000',
    'Still working it out'
  ];

  const weddingTypes = [
    'Hotel ballroom wedding',
    'Garden or outdoor ceremony',
    'Restaurant or private-dining reception',
    'Church or temple ceremony, with reception after',
    'Solemnisation only',
    'Multi-day celebration',
    'Not sure yet'
  ];

  const waHref = whatsappHref(
    "Hi 7Magic, we're planning a wedding in Singapore and would like to book the free consultation."
  );

  // English is the only copy this page carries, but the chrome around it is
  // not — same reasoning, and the same fix, as /bali-wedding-planning.
  const CANONICAL_PATH = '/en/wedding-planning-singapore';

  const metaTitle = 'Wedding Planning Singapore — Planning + Day-Of Concierge | 7Magic';
  const metaDescription =
    'Plan your Singapore wedding with 7Magic: 18 years of experience, a Singapore office, and ALL Access running check-in and seating on the day. Free consultation.';

  // Bump when the copy or the ALL Access prices are re-checked. Shown on the
  // page and in the schema, since AI answers weight recency.
  const LAST_UPDATED = '2026-09-19';
  const lastUpdatedLabel = '19 September 2026';

  const pageJsonLd = jsonLdScript(
    graph(
      organization(),
      website(),
      {
        ...webPageNode({
          url: CANONICAL_PATH,
          name: metaTitle,
          description: metaDescription,
          locale: 'en'
        }),
        dateModified: LAST_UPDATED
      },
      breadcrumbList([
        { name: 'Home', path: '/en' },
        { name: 'Wedding planning Singapore' }
      ]),
      {
        '@type': 'Service',
        serviceType: 'Wedding planning',
        provider: { '@id': 'https://7magicwedding.com/#organization' },
        areaServed: { '@type': 'Place', name: 'Singapore' },
        description:
          'Full-service wedding planning for couples marrying in Singapore: venue sourcing, vendor management, design, guest logistics, timeline and on-the-day coordination, run with ALL Access as the day-of concierge technology partner.'
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

    const message = [
      `Wedding type: ${field('wedding_type') || '—'}`,
      `Target date: ${field('wedding_date') || '—'}`,
      `Guests: ${field('guests') || '—'}`,
      `Budget: ${field('budget') || '—'}`,
      `Interested in ALL Access: ${field('concierge_interest') || '—'}`,
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
          source_path: '/wedding-planning-singapore'
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
    content="wedding planner singapore, wedding planning singapore, singapore wedding planner, plan a wedding in singapore, wedding day concierge singapore, wedding check-in app singapore"
  />
  <link rel="canonical" href="https://7magicwedding.com{CANONICAL_PATH}" />
  {@html pageJsonLd}
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[660px]">
    <!-- Marina Bay Sands Hotel and Shopping Complex, Singapore" by Mustang Joe,
         1 November 2024, CC0 (no attribution required), via Wikimedia
         Commons. Copied from apps/website-sg's own hero, where it carries
         the full source note. -->
    <img
      src="/img/marina-bay-sands-singapore.jpg"
      alt="Marina Bay Sands and the Singapore skyline across the bay at dusk"
      class="absolute inset-0 h-full w-full object-cover object-[50%_60%]"
      fetchpriority="high"
    />
    <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/40 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          Wedding planning · Singapore
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.4rem]">
          <span class="block">Plan your wedding in Singapore.</span>
          <span class="block">We run the day, too.</span>
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/90">
          7Magic has planned weddings for eighteen years and now has an office in Singapore. ALL
          Access, our technology partner, handles guest check-in, seating and the dietary list on
          the day. One enquiry covers both.
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
    <div class="max-w-3xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        Why couples hand it to us
      </p>
      <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
        One planner for the year, one system for the day
      </h2>
      <div class="mt-5 grid gap-5 text-[15px] leading-7 text-muted-foreground">
        <p class="text-base font-medium text-foreground">
          Wedding planning in Singapore with 7Magic covers venue sourcing, vendor bookings, design,
          budget, the timeline and the marriage paperwork, run by a team with eighteen years of
          experience and a Singapore office. ALL Access, a separate company, runs guest check-in and
          seating on the day, billed separately from S$199.
        </p>
        <p>
          A Singapore wedding means a year of decisions about venues, vendors and contracts, plus a
          guest list that changes every week. Most couples run out of time before they run out of
          ideas.
        </p>
        <p>
          7Magic has planned weddings for eighteen years, more than a thousand of them across
          Jakarta, Bali and now Singapore. We have an office here, and the team knows the
          paperwork, the timelines and what to ask a venue before you sign.
        </p>
        <p>
          On the day, we work with ALL Access, a Singapore company that makes concierge software
          for events. Guests check themselves in from their phones and your planner sees the room
          fill up live. The seating plan, the place cards and the caterer's dietary list all come
          from one guest list, so they cannot disagree.
        </p>
        <p class="text-sm">Last updated {lastUpdatedLabel}.</p>
      </div>
    </div>
  </section>

  <!-- Venue sourcing -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        Venue sourcing
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Start with the venues we already know
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Bring us a shortlist or start from ours. We check real availability for your date, put the
        quotations side by side and give you the honest read on each one before you commit to
        anything.
      </p>

      <a
        href={localizeHref('/wedding-venue/search?city=singapore')}
        class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'mt-7 px-6')}
      >
        <SearchIcon size={17} />
        Browse Singapore wedding venues
      </a>
    </div>
  </section>

  <!-- The partnership -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      The partnership
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      7Magic plans it. ALL Access runs it.
    </h2>
    <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
      Two companies, one wedding day. 7Magic is your planner from the first call to the final
      booking. ALL Access is the technology your guests actually touch on the day. Your 7Magic
      planner arranges it as part of your wedding, the same way they arrange your photographer or
      your florist. There is nothing for you or your guests to install.
    </p>

    <div class="mt-10 grid gap-5 md:grid-cols-2">
      <div class="rounded-md border border-border bg-background p-7">
        <img src="/img/7magic-logo.png" alt="7Magic Wedding" class="h-9 w-auto object-contain" />
        <h3 class="mt-4 font-display text-lg font-semibold">Plans your wedding</h3>
        <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
          Venue, vendors, design, guest logistics, timeline and paperwork: the year of decisions
          before the day arrives.
        </p>
      </div>
      <div class="rounded-md border border-border bg-background p-7">
        <!-- ALL Access has no image logo — their own brand carries this exact
             typographic lockup (Wordmark.svelte on allaccess.sg): caps, wide
             tracking on "ALL", gold italic on "Access", set larger. Matched
             here in 7Magic's own type rather than importing their font. -->
        <span
          class="font-display inline-flex h-9 items-baseline gap-[7px] text-lg tracking-[0.16em]"
        >
          <span>ALL</span>
          <span class="text-brand-gold italic" style="font-size: 1.15em; letter-spacing: 0.02em"
            >Access</span
          >
        </span>
        <h3 class="mt-4 font-display text-lg font-semibold">Runs your day</h3>
        <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
          Guest check-in, the seating plan, the dietary list and the place cards: the software your
          guests and your planner both rely on once the day begins.
        </p>
      </div>
    </div>
  </section>

  <!-- What ALL Access adds -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        What ALL Access adds
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        What ALL Access does on the wedding day
      </h2>

      <div class="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {#each dayOfFeatures as feature (feature.title)}
          <div class="rounded-md border border-border bg-background p-6">
            <span class="font-display text-2xl font-bold text-brand-warm-deep">{feature.num}</span>
            <h3 class="mt-3 font-display text-lg font-semibold">{feature.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{feature.body}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- ALL Access pricing -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      ALL Access pricing
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      Priced by ALL Access, booked through your planner
    </h2>
    <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
      Billed separately from the 7Magic planning fee, at ALL Access's own published Singapore-dollar
      pricing. Tell your planner which tier you want and they arrange it. There is no separate account
      and no extra vendor to manage yourself.
    </p>

    <div class="mt-10 grid gap-5 md:grid-cols-2">
      {#each conciergePackages as pkg (pkg.tier)}
        <div class="rounded-md border border-border bg-background p-7">
          <h3 class="font-display text-xl font-semibold">{pkg.tier}</h3>
          <p class="mt-2 font-display text-3xl font-bold">{pkg.price}</p>
          <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{pkg.lead}</p>
          <div class="mt-5 grid gap-2.5">
            {#each pkg.specs as spec}
              <div class="flex gap-3 text-[15px] leading-7">
                <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                <span>{spec}</span>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  </section>

  <!-- ALL Access add-ons -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div>
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        Add-ons
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Add only what your wedding needs
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Each one sits on top of whichever ALL Access tier you choose, priced per event, and your
        7Magic planner adds it to the same booking.
      </p>

      <div class="mt-10 grid gap-5 md:grid-cols-2">
        {#each addOnGroups as group (group.title)}
          <div class="rounded-md border border-border bg-background p-6">
            <h3 class="font-display text-lg font-semibold">{group.title}</h3>
            <div class="mt-4 grid gap-4">
              {#each group.items as item (item.name)}
                <div class="border-t border-border/70 pt-4 first:border-t-0 first:pt-0">
                  <div class="flex items-baseline justify-between gap-3">
                    <p class="text-[15px] font-medium">{item.name}</p>
                    <p class="shrink-0 text-sm font-semibold text-brand-gold">{item.price}</p>
                  </div>
                  <p class="mt-1 text-sm leading-6 text-muted-foreground">{item.detail}</p>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </div>

      <div class="mt-8 rounded-md border border-brand-gold/40 bg-brand-gold-soft p-7">
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          Best value
        </p>
        <h3 class="mt-2 font-display text-xl font-semibold">{bundle.heading}</h3>
        <p class="mt-2 max-w-2xl text-[15px] leading-7 text-muted-foreground">{bundle.lead}</p>
        <div class="mt-4 flex flex-wrap gap-2">
          {#each bundle.includes as item}
            <span class="rounded-full border border-border bg-background px-3 py-1 text-xs">
              {item}
            </span>
          {/each}
        </div>
        <div class="mt-5 flex items-baseline gap-3">
          <p class="font-display text-2xl font-bold">{bundle.price}</p>
          <p class="text-sm font-semibold text-brand-gold">{bundle.saving}</p>
        </div>
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

  <!-- What's included -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
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
  </section>

  <!-- Free consultation -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        Getting started
      </p>
      <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
        Two weeks to decide, before you pay anything
      </h2>
      <p class="mt-5 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Choosing a planner is a big decision, so we do not ask for a deposit to start talking. Send
        us an enquiry and you get two weeks of real planning work, free and with nothing owed at
        the end of it.
      </p>

      <div class="mt-7 grid max-w-2xl gap-2.5">
        {#each consultation as item}
          <div class="flex gap-3 text-[15px] leading-7">
            <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
            <span>{item}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

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
          {#if faq.sources}
            <p class="mt-2 text-sm text-muted-foreground">
              Sources:
              {#each faq.sources as source, i}
                {#if i > 0}, {/if}<a
                  href={source.href}
                  rel="noopener"
                  class="underline underline-offset-2 hover:text-foreground">{source.label}</a
                >
              {/each}
            </p>
          {/if}
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
          Tell us the date, the rough guest count and what you have in mind. A planner reads every
          enquiry and replies with venue options and honest numbers. Nothing is owed for the first
          fortnight.
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
            <h3 class="font-display text-xl font-semibold">Thank you, that reached us</h3>
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
                <label for="sg-type" class="text-[13px] font-medium">
                  What you have in mind <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <select id="sg-type" name="wedding_type" required class={inputClass}>
                  <option value="">Choose one</option>
                  {#each weddingTypes as type}
                    <option value={type}>{type}</option>
                  {/each}
                </select>
              </div>
              <div class="grid gap-1.5">
                <label for="sg-date" class="text-[13px] font-medium">
                  Wedding date <span class="text-muted-foreground">(a rough one is fine)</span>
                </label>
                <input id="sg-date" name="wedding_date" type="date" class={inputClass} />
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sg-guests" class="text-[13px] font-medium">
                  Guests <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="sg-guests"
                  name="guests"
                  type="number"
                  min="1"
                  required
                  placeholder="e.g. 150"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="sg-budget" class="text-[13px] font-medium">Total wedding budget</label>
                <select id="sg-budget" name="budget" class={inputClass}>
                  <option value="">Prefer not to say</option>
                  {#each budgets as budget}
                    <option value={budget}>{budget}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sg-name" class="text-[13px] font-medium">
                  Your name <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input id="sg-name" name="name" required autocomplete="name" class={inputClass} />
              </div>
              <div class="grid gap-1.5">
                <label for="sg-concierge" class="text-[13px] font-medium">
                  Interested in the ALL Access platform?
                </label>
                <select id="sg-concierge" name="concierge_interest" class={inputClass}>
                  <option value="Not sure yet">Not sure yet</option>
                  <option value="Yes, Essential Access">Yes, Essential Access</option>
                  <option value="Yes, Ultimate Luxury">Yes, Ultimate Luxury</option>
                  <option value="No thanks">No thanks</option>
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sg-email" class="text-[13px] font-medium">
                  Email <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="sg-email"
                  name="email"
                  type="email"
                  required
                  autocomplete="email"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="sg-phone" class="text-[13px] font-medium">
                  WhatsApp <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="sg-phone"
                  name="phone"
                  required
                  autocomplete="tel"
                  placeholder="Include your country code"
                  class={inputClass}
                />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="sg-venue" class="text-[13px] font-medium">
                Venue in mind <span class="text-muted-foreground">(optional)</span>
              </label>
              <input
                id="sg-venue"
                name="venue"
                placeholder="A property in Singapore, or somewhere you found yourself"
                class={inputClass}
              />
            </div>

            <div class="grid gap-1.5">
              <label for="sg-notes" class="text-[13px] font-medium">
                Anything else we should know?
              </label>
              <textarea
                id="sg-notes"
                name="notes"
                rows="3"
                placeholder="Religious requirements, guests needing extra help, ideas you already love"
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

  <!-- Page-specific attribution: only this page names ALL Access, so the
       note lives here rather than in the shared PublicFooter every other
       page renders too. -->
  <p class="mx-auto max-w-7xl px-5 py-6 text-xs text-muted-foreground lg:px-8">
    ALL Access® is a registered trademark of ALL Access. ALL Access is 7Magic Wedding's technology
    partner for guest check-in, seating and day-of concierge services on weddings we plan in
    Singapore.
  </p>

  <PublicFooter />
</main>
