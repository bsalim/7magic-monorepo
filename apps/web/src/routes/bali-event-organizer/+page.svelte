<script lang="ts">
  import CalendarIcon from '@lucide/svelte/icons/calendar-days';
  import CheckIcon from '@lucide/svelte/icons/check';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';

  /**
   * Landing page for the corporate / outing side of the business.
   *
   * Deliberately not translated: this is an English-only acquisition page,
   * separate from the bilingual wedding marketplace. Copy is hardcoded for the
   * same reason /about is — it changes as a unit, not per-string.
   */

  // ---------------------------------------------------------------------------
  // Day Programme rate and the 20-person floor are confirmed by 7Magic.
  // The Two Nights figure is still a PLACEHOLDER — replace before publishing.
  // ---------------------------------------------------------------------------
  const packages = [
    {
      name: 'Day Programme',
      from: 'Rp 500.000',
      unit: '/ person',
      minimum: 'from 20 people',
      summary: 'One activity day. Your team is already staying somewhere in Bali.',
      includes: [
        'Half or full day of games with our facilitator team',
        'Sound system, MC, and all game equipment',
        'Coordinator on site from setup to pack-down',
        'Mineral water, ice, and a first-aid kit',
        'Bus transfer within South Bali'
      ]
    },
    {
      name: 'Two Nights, Three Days',
      from: 'Rp 2.450.000',
      unit: '/ person',
      minimum: 'from 40 people',
      summary: 'The standard company outing. Hotel, activities, and one big dinner.',
      featured: true,
      includes: [
        'Two nights, twin share, 4-star hotel in Nusa Dua or Kuta',
        'Airport pickup and drop-off, both directions',
        'One team building day and one cultural or beach afternoon',
        'Gala dinner with Balinese performance and a live band',
        'All meals as itemised, bus and driver throughout',
        'Two of our coordinators with your group the whole time'
      ]
    },
    {
      name: 'Conference & Incentive',
      from: 'On quote',
      unit: '',
      minimum: 'from 80 people',
      summary: 'Meeting rooms, production, and a programme that runs to the minute.',
      includes: [
        'Hotel and ballroom sourcing, with rates we negotiate for you',
        'Stage, LED screen, lighting, and audio production',
        'Registration desk, name tags, and rooming list management',
        'Awards night or gala with full run-down and rehearsal',
        'Airport handling for arrivals spread across several flights',
        'A named project manager from the first call to the final invoice'
      ]
    }
  ];

  const services = [
    {
      image: '/img/bali-event/outing.jpg',
      alt: 'A group walking together along a beach in Bali',
      title: 'Company outing',
      copy: 'Two to four days, hotel to airport. The version most companies book.'
    },
    {
      image: '/img/bali-event/teambuilding.jpg',
      alt: 'A team cheering during an outdoor team building game',
      title: 'Team building',
      copy: 'Beach games, amazing race, rafting, or a quieter facilitated session indoors.'
    },
    {
      image: '/img/bali-event/gathering.jpg',
      alt: 'Colleagues celebrating with confetti at a company party',
      title: 'Gathering & anniversary',
      copy: 'Family day, year-end party, or a company birthday with entertainment.'
    },
    {
      image: '/img/bali-event/gala.jpg',
      alt: 'Long banquet tables set with candles for a gala dinner',
      title: 'Gala dinner & awards',
      copy: 'Stage, run-down, MC, band, and a rehearsal so the awards do not drag.'
    },
    {
      image: '/img/bali-event/conference.jpg',
      alt: 'An audience watching a speaker on stage at a conference',
      title: 'Meetings & conference',
      copy: 'Ballroom, breakout rooms, AV, registration, and the coffee breaks on time.'
    },
    {
      image: '/img/bali-event/incentive.jpg',
      alt: 'Aerial view of a Bali resort pool surrounded by villas',
      title: 'Incentive trip',
      copy: 'A reward trip for top performers, with the logistics kept out of sight.'
    }
  ];

  const itinerary = [
    {
      day: 'Day 1',
      title: 'Arrive and settle',
      items: [
        'Airport pickup at Ngurah Rai, our staff waiting at the arrival gate',
        'Check in at the hotel, welcome drink, rooming list already sorted',
        'Seafood dinner on the sand at Jimbaran, sunset seating'
      ]
    },
    {
      day: 'Day 2',
      title: 'The main day',
      items: [
        'Morning team building at Pandawa Beach — five to six games, one facilitator per group',
        'Lunch on site, then the afternoon free or a short trip to Uluwatu',
        'Gala dinner: Balinese dance opening, awards, live band, closing at 22:30'
      ]
    },
    {
      day: 'Day 3',
      title: 'Wrap and fly',
      items: [
        'Late checkout arranged where the hotel allows it',
        'Stop for oleh-oleh, then straight to the airport',
        'Drop-off timed to each flight, not one bus for everyone'
      ]
    }
  ];

  const steps = [
    {
      title: 'Tell us the shape of it',
      copy: 'Headcount, rough dates, and the budget per person. Five minutes on WhatsApp is enough.',
      time: 'Day 1'
    },
    {
      title: 'We send a real proposal',
      copy: 'Named hotels, a day-by-day run-down, and a price per person you can take to finance.',
      time: 'Within 2 working days'
    },
    {
      title: 'You pick, we lock it',
      copy: 'We hold the rooms and the venue, issue the invoice, and start building the run-down.',
      time: 'After your approval'
    },
    {
      title: 'We run it in Bali',
      copy: 'Our coordinators are with your group from the airport to the departure gate.',
      time: 'Event week'
    }
  ];

  const faqs = [
    {
      q: 'What is the smallest group you will take?',
      a: '20 people for an activity day, 40 for a full outing with hotel. Below that the per-person cost climbs fast because the bus, the sound system, and the facilitators cost the same whether you bring 12 or 40.'
    },
    {
      q: 'How far ahead should we book?',
      a: 'Six to eight weeks is comfortable. Hotel rates in July, August, and December move early, so a group of 100 in peak season is better started three months out. We have turned around a 60-person outing in eleven days before, but it costs more.'
    },
    {
      q: 'Can you work to a fixed budget per person?',
      a: 'Yes, and it is the easiest way to start. Give us the number and the headcount and we will show you what fits, including what we would cut first if the budget is tight.'
    },
    {
      q: 'What happens if it rains?',
      a: 'Every outdoor programme gets a wet-weather version written into the run-down before you arrive. Beach games move to the hotel function room or a covered area we have already checked. We do not improvise this on the day.'
    },
    {
      q: 'Do you handle flights?',
      a: 'No. Companies almost always book their own flights through a corporate travel agent or a tender. We take over from the moment your group lands.'
    },
    {
      q: 'Who is actually on site during the event?',
      a: 'A project manager who has been on your account since the first call, plus coordinators scaled to group size. You get their mobile numbers before you fly.'
    }
  ];

  const budgets = [
    'Under Rp 1 million per person',
    'Rp 1 – 2.5 million per person',
    'Rp 2.5 – 5 million per person',
    'Above Rp 5 million per person',
    'Not decided yet'
  ];

  const eventTypes = [
    'Company outing',
    'Team building',
    'Gathering / family day',
    'Gala dinner / awards',
    'Meeting / conference',
    'Incentive trip',
    'Something else'
  ];

  // Real client logos and quotes go here once 7Magic supplies them. Left empty
  // on purpose — an invented testimonial on a live site is a fake review.
  const testimonials: { quote: string; name: string; role: string }[] = [];

  const waHref = whatsappHref(
    'Hi 7Magic, I want to ask about a corporate event in Bali. Here are our details:'
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

    // The API's contact-lead schema has no event-specific columns, so the
    // qualifying answers are folded into the message body. Sales reads them
    // there; a dedicated schema is the follow-up, not a blocker for launch.
    const message = [
      `Event type: ${field('event_type') || '—'}`,
      `Target date: ${field('event_date') || '—'}`,
      `Headcount: ${field('pax') || '—'}`,
      `Budget: ${field('budget') || '—'}`,
      `Company: ${field('company') || '—'}`,
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
          source_path: '/bali-event-organizer'
        })
      });

      if (!response.ok) {
        errorMessage = 'That did not go through. Please try again, or message us on WhatsApp.';
        return;
      }

      submitted = true;
      form.reset();
    } catch {
      errorMessage = 'That did not go through. Please try again, or message us on WhatsApp.';
    } finally {
      sending = false;
    }
  }

  const inputClass =
    'rounded-md border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30';
</script>

<svelte:head>
  <title>Bali Event Organizer | Company Outing, Team Building & Gala Dinner — 7Magic</title>
  <meta
    name="description"
    content="Bali event organizer for company outings, team building, gatherings, gala dinners and conferences. Per-person pricing, a proposal in two working days, and coordinators with your group from the airport onwards."
  />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[640px]">
    <img
      src="/img/bali-event/hero-temple.jpg"
      alt="Tanah Lot temple in Bali at sunset"
      class="absolute inset-0 h-full w-full object-cover object-[50%_38%]"
      fetchpriority="high"
    />
    <!-- No flat dimming layer — the sunset stays at full brightness. Contrast
         for the headline comes from a soft left-side gradient plus a shadow on
         the text itself, rather than from darkening the whole photo. -->
    <div class="absolute inset-0 bg-gradient-to-r from-black/55 via-black/15 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          Bali event organizer
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.4rem]">
          Your company outing in Bali, run by people who are already here
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/85">
          Outings, team building, gatherings, gala dinners, and conferences. We quote per person,
          send a day-by-day run-down before you commit, and put our coordinators with your group
          from the arrival gate to the departure gate.
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a href="#proposal" class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
            Get a proposal
          </a>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'border border-white/30 bg-white/10 px-7 text-white backdrop-blur hover:bg-white hover:text-brand-ink'
            )}
          >
            <MessageCircleIcon size={18} />
            WhatsApp us
          </a>
        </div>

        <p class="mt-5 text-sm text-white/90">
          Tell us headcount, dates, and budget per person. Proposal back within two working days.
        </p>
      </div>
    </div>
  </section>

  <!-- Trust strip. Figures match the ones published on 7magicwedding.com. -->
  <section class="border-b border-border bg-brand-ink px-5 py-6 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {#each [{ value: '18+', label: 'Years organising events' }, { value: '1000+', label: 'Events delivered' }, { value: '100+', label: 'Vendors on our books' }, { value: 'Bali', label: 'Team on the ground, not remote' }] as stat}
        <div>
          <p class="font-display text-2xl font-bold text-brand-dark-accent">{stat.value}</p>
          <p class="mt-1 text-sm text-white/72">{stat.label}</p>
        </div>
      {/each}
    </div>
  </section>

  <!-- Services -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">What we run</p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      Six formats, and most companies book one of the first two
    </h2>

    <div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {#each services as service}
        <article class="group relative h-[340px] overflow-hidden rounded-md">
          <img
            src={service.image}
            alt={service.alt}
            loading="lazy"
            class="absolute inset-0 h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
          <div
            class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/45 to-black/10"
          ></div>
          <div class="absolute inset-x-0 bottom-0 p-6 text-white">
            <h3 class="font-display text-xl font-semibold">{service.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-white/85">{service.copy}</p>
          </div>
        </article>
      {/each}
    </div>
  </section>

  <!-- Sample itinerary -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
        <div>
          <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
            A real programme
          </p>
          <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
            What three days in Bali actually looks like
          </h2>
          <p class="mt-4 max-w-xl text-[15px] leading-7 text-muted-foreground">
            This is the shape of the outing we run most often, for groups of 40 to 120. Yours will
            differ — but this is the level of detail you get in the proposal, not a list of
            adjectives.
          </p>

          <div class="mt-8 grid gap-4">
            {#each itinerary as block}
              <div class="rounded-md border border-border bg-background p-6">
                <div class="flex items-baseline gap-3">
                  <span class="rounded-full bg-brand-gold-soft px-3 py-1 text-xs font-semibold uppercase tracking-widest text-brand-gold-hover">
                    {block.day}
                  </span>
                  <h3 class="font-display text-lg font-semibold">{block.title}</h3>
                </div>
                <ul class="mt-4 grid gap-2.5">
                  {#each block.items as item}
                    <li class="flex gap-3 text-[15px] leading-7 text-muted-foreground">
                      <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                      <span>{item}</span>
                    </li>
                  {/each}
                </ul>
              </div>
            {/each}
          </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
          <img
            src="/img/bali-event/teambuilding.jpg"
            alt="A team celebrating during an outdoor team building game"
            loading="lazy"
            class="h-64 w-full rounded-md object-cover"
          />
          <img
            src="/img/bali-event/kecak.jpg"
            alt="Balinese Kecak dancers performing at sunset"
            loading="lazy"
            class="h-64 w-full rounded-md object-cover"
          />
          <img
            src="/img/bali-event/gala.jpg"
            alt="Long banquet tables set with candles for a gala dinner"
            loading="lazy"
            class="h-64 w-full rounded-md object-cover sm:col-span-2 lg:col-span-1"
          />
        </div>
      </div>
    </div>
  </section>

  <!-- Packages -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Starting points</p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      Roughly what it costs, before we quote you properly
    </h2>
    <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
      Real prices depend on the season, the hotel, and how far your group spreads across arrival
      times. These are honest starting points so you can sanity-check your budget today.
    </p>

    <div class="mt-10 grid gap-5 lg:grid-cols-3">
      {#each packages as pkg}
        <div
          class={cn(
            'flex flex-col rounded-md border bg-background p-7',
            pkg.featured ? 'border-brand-gold shadow-lg ring-1 ring-brand-gold/20' : 'border-border'
          )}
        >
          {#if pkg.featured}
            <span class="mb-4 w-fit rounded-full bg-brand-gold px-3 py-1 text-xs font-semibold uppercase tracking-widest text-white">
              Most booked
            </span>
          {/if}
          <h3 class="font-display text-xl font-semibold">{pkg.name}</h3>
          <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{pkg.summary}</p>

          <div class="mt-5 flex items-baseline gap-1.5">
            {#if pkg.unit}
              <span class="text-sm text-muted-foreground">from</span>
            {/if}
            <span class="font-display text-2xl font-bold">{pkg.from}</span>
            <span class="text-sm text-muted-foreground">{pkg.unit}</span>
          </div>
          <p class="mt-1 text-sm text-muted-foreground">{pkg.minimum}</p>

          <ul class="mt-6 grid flex-1 content-start gap-2.5 border-t border-border pt-6">
            {#each pkg.includes as item}
              <li class="flex gap-3 text-[15px] leading-7">
                <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>

          <a
            href="#proposal"
            class={cn(
              buttonVariants({ variant: pkg.featured ? 'gold' : 'outline' }),
              'mt-7 w-full'
            )}
          >
            Get this quoted
          </a>
        </div>
      {/each}
    </div>

    <div class="mt-8 rounded-md border border-border bg-secondary p-6">
      <h3 class="font-display text-base font-semibold">What is not in the price</h3>
      <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
        Flights to Bali, personal spending, and anything your team adds on the day. If a hotel
        charges a surcharge for a peak date we tell you in the quotation rather than after it.
      </p>
    </div>
  </section>

  <!-- How it works -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">How it works</p>
      <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">Four steps, and two are ours</h2>

      <div class="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        {#each steps as step, index}
          <div class="rounded-md border border-border bg-background p-6">
            <span class="font-display text-3xl font-bold text-brand-warm-deep">
              {String(index + 1).padStart(2, '0')}
            </span>
            <h3 class="mt-3 font-display text-lg font-semibold">{step.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{step.copy}</p>
            <p class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand-gold-hover">
              <CalendarIcon size={15} />
              {step.time}
            </p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  {#if testimonials.length}
    <section class="bg-secondary px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <h2 class="font-display text-3xl font-bold md:text-4xl">What clients said afterwards</h2>
        <div class="mt-10 grid gap-5 md:grid-cols-3">
          {#each testimonials as item}
            <figure class="rounded-md border border-border bg-background p-6">
              <blockquote class="text-[15px] leading-7">{item.quote}</blockquote>
              <figcaption class="mt-4 text-sm font-semibold">
                {item.name}
                <span class="block font-normal text-muted-foreground">{item.role}</span>
              </figcaption>
            </figure>
          {/each}
        </div>
      </div>
    </section>
  {/if}

  <!-- FAQ -->
  <section class="mx-auto max-w-4xl px-5 py-16 lg:px-8">
    <h2 class="font-display text-3xl font-bold md:text-4xl">Questions we get every week</h2>
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
  <section id="proposal" class="scroll-mt-20 bg-brand-ink px-5 py-16 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.85fr_1.15fr]">
      <div>
        <h2 class="font-display text-3xl font-bold md:text-4xl">Tell us what you are planning</h2>
        <p class="mt-4 text-[15px] leading-7 text-white/75">
          Four answers is enough to start. We come back within two working days with named hotels, a
          day-by-day run-down, and a price per person — not a brochure.
        </p>

        <div class="mt-8 rounded-md border border-white/15 bg-white/5 p-6">
          <p class="text-sm text-white/70">Prefer to just talk?</p>
          <a
            href={waHref}
            class={cn(buttonVariants({ size: 'lg' }), 'mt-3 w-full bg-brand-success text-white hover:bg-brand-success-hover')}
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
            <h3 class="font-display text-xl font-semibold">Got it</h3>
            <p class="max-w-sm text-[15px] leading-7 text-muted-foreground">
              We will come back within two working days. If your date is tighter than that, message
              us on WhatsApp and say so.
            </p>
            <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-2')}>
              <MessageCircleIcon size={17} />
              Message us now
            </a>
          </div>
        {:else}
          <form onsubmit={submit} class="grid gap-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="ev-type" class="text-[13px] font-medium">
                  Event type <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <select id="ev-type" name="event_type" required class={inputClass}>
                  <option value="">Choose one</option>
                  {#each eventTypes as type}
                    <option value={type}>{type}</option>
                  {/each}
                </select>
              </div>
              <div class="grid gap-1.5">
                <label for="ev-date" class="text-[13px] font-medium">
                  Target date <span class="text-muted-foreground">(rough is fine)</span>
                </label>
                <input id="ev-date" name="event_date" type="date" class={inputClass} />
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="ev-pax" class="text-[13px] font-medium">
                  How many people <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="ev-pax"
                  name="pax"
                  type="number"
                  min="1"
                  required
                  placeholder="e.g. 60"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="ev-budget" class="text-[13px] font-medium">Budget per person</label>
                <select id="ev-budget" name="budget" class={inputClass}>
                  <option value="">Prefer not to say</option>
                  {#each budgets as budget}
                    <option value={budget}>{budget}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="ev-name" class="text-[13px] font-medium">
                  Your name <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="ev-name"
                  name="name"
                  required
                  autocomplete="name"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="ev-company" class="text-[13px] font-medium">Company</label>
                <input id="ev-company" name="company" autocomplete="organization" class={inputClass} />
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="ev-phone" class="text-[13px] font-medium">
                  WhatsApp <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="ev-phone"
                  name="phone"
                  required
                  autocomplete="tel"
                  placeholder="08xx xxxx xxxx"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="ev-email" class="text-[13px] font-medium">
                  Work email <span class="text-muted-foreground">(optional)</span>
                </label>
                <input
                  id="ev-email"
                  name="email"
                  type="email"
                  autocomplete="email"
                  class={inputClass}
                />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="ev-notes" class="text-[13px] font-medium">
                Anything we should know
              </label>
              <textarea
                id="ev-notes"
                name="notes"
                rows="3"
                placeholder="Hotel already booked, awards night on the last evening, two vegetarians…"
                class={inputClass}
              ></textarea>
            </div>

            {#if errorMessage}
              <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
            {/if}

            <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending}>
              {sending ? 'Sending…' : 'Send and get a proposal'}
            </Button>
            <p class="text-center text-xs text-muted-foreground">
              We use these details to quote your event. Nothing else.
            </p>
          </form>
        {/if}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
