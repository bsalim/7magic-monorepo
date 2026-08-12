<script lang="ts">
  // English only for now, hardcoded rather than in Paraglide -- the same shape as
  // perjanjian-pranikah, paket-sangjit and bali-wedding-planning. The Indonesian
  // pass comes after the copy settles; moving it into messages/{id,en}.json before
  // then would mean translating wording that is still changing.
  //
  // Every claim here is either already published elsewhere on the site (the visit
  // is free and carries no obligation) or a property of the booking system itself
  // (you choose the venue and the day, and say how many are coming). Nothing
  // asserts a duration, an inclusion or a discount that nobody has confirmed.
  import CalendarCheckIcon from '@lucide/svelte/icons/calendar-check';
  import CheckIcon from '@lucide/svelte/icons/check';
  import MapPinIcon from '@lucide/svelte/icons/map-pin';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import UsersIcon from '@lucide/svelte/icons/users';

  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { buttonVariants } from '$lib/components/ui/button';
  import { localizeHref } from '$lib/paraglide/runtime';
  import { cityImage } from '$lib/tour';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';

  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const branches = $derived(data.branches);
  const waHref = whatsappHref('Hi 7Magic, I would like to book a free venue tour.');

  // Cities, deduplicated and in the order the API returned them, so the intro
  // sentence and the strip below never claim a city with no bookable branch.
  const cities = $derived([...new Set(branches.map((branch) => branch.city))]);

  const cityList = $derived(
    cities
      .map((city) => city.charAt(0).toUpperCase() + city.slice(1))
      .reduce(
        (text, city, index, all) =>
          index === 0 ? city : index === all.length - 1 ? `${text} and ${city}` : `${text}, ${city}`,
        ''
      )
  );

  // Built here rather than with an inline {#if}: Svelte trims the whitespace at the
  // start of a block, so `visit{#if ...} in {cityList}{/if}` renders as "visitin".
  const heroPlaces = $derived(cityList ? ` in ${cityList}` : '');

  // localizeHref, not a bare '/tour': the rest of the site uses plain links, which
  // drop an English visitor back to the Indonesian page. This funnel is the point
  // of an English landing page, so it keeps the locale.
  const tourHref = $derived(localizeHref('/tour'));

  const expectations = [
    {
      icon: MapPinIcon,
      title: 'See the space in person',
      body: 'Photos flatten a room. Walk it, stand where your guests will sit, and see how the light falls at the hour you are considering.'
    },
    {
      icon: UsersIcon,
      title: 'Meet the team',
      body: 'Talk to the people who would actually run your day, not a call centre. Ask what they have done before and how they work.'
    },
    {
      icon: CalendarCheckIcon,
      title: 'Talk dates and packages',
      body: 'Bring the dates you are weighing up and the questions you have not had answered yet. You will get straight answers.'
    }
  ];

  const steps = [
    {
      n: '1',
      title: 'Choose the venue',
      body: 'Pick from the venues we work with, grouped by city so you can find yours quickly.'
    },
    {
      n: '2',
      title: 'Pick a day',
      body: 'Tell us the day that suits you and how many are coming. We confirm the time with you.'
    },
    {
      n: '3',
      title: 'Come and look around',
      body: 'You get a confirmation by email, and we are in touch with the details before you go.'
    }
  ];

  const faqs = [
    {
      q: 'Is it really free?',
      a: 'Yes. The visit is free and there is no commitment — you are not signing anything by coming to look.'
    },
    {
      q: 'Do I have to decide on the day?',
      a: 'No. Plenty of couples visit more than one venue before deciding, and we would rather you were sure.'
    },
    {
      q: 'Can I bring family?',
      a: 'Please do. Put the total number of people in the booking so we know how many to expect.'
    },
    {
      q: 'What if the day I want does not work?',
      a: 'Ask for the day that suits you and we will confirm the time, or tell you the nearest we can manage. If you would rather sort it in a message, WhatsApp us.'
    }
  ];
</script>

<svelte:head>
  <title>Book a Free Venue Tour | 7Magic Wedding</title>
  <meta
    name="description"
    content="Visit a 7Magic wedding venue in person, free and with no obligation. Choose the venue you want to see, pick a day that suits you, and meet the team who would run your day."
  />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[640px]">
    <img
      src="/img/hero-home.jpg"
      alt="A styled wedding reception ready for guests"
      class="absolute inset-0 h-full w-full object-cover object-[50%_42%]"
      fetchpriority="high"
    />
    <div class="absolute inset-0 bg-gradient-to-r from-black/60 via-black/20 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          Free venue tour
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.4rem]">
          See your wedding venue before you commit to it
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/85">
          Book a free, no-obligation visit{heroPlaces}. Walk the space, meet the team, and ask the
          questions a brochure never answers.
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a href={tourHref} class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
            Book your free tour
          </a>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'border border-white/30 bg-white/10 px-7 text-white backdrop-blur hover:bg-white hover:text-brand-ink'
            )}
          >
            <MessageCircleIcon size={18} />
            Ask on WhatsApp
          </a>
        </div>

        <p class="mt-5 text-sm text-white/90">
          Free · No obligation · You choose the venue and the day
        </p>
      </div>
    </div>
  </section>

  <!-- What the visit is -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      What to expect
    </p>
    <!-- No duration claimed anywhere on this page: nobody has told us how long a
         visit runs, and a number here would be invented. -->
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      One visit answers what weeks of browsing cannot
    </h2>

    <div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {#each expectations as item (item.title)}
        <div class="rounded-xl border border-border bg-card p-6">
          <item.icon class="size-6 text-brand-dark-accent" />
          <h3 class="mt-4 font-display text-xl font-semibold">{item.title}</h3>
          <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{item.body}</p>
        </div>
      {/each}
    </div>
  </section>

  <!-- How booking works -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        How it works
      </p>
      <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">Three steps, about a minute</h2>

      <div class="mt-10 grid gap-5 sm:grid-cols-3">
        {#each steps as step (step.n)}
          <div class="rounded-xl border border-border bg-background p-6">
            <p
              class="flex size-9 items-center justify-center rounded-full bg-brand-ink font-display text-lg font-bold text-brand-dark-accent"
            >
              {step.n}
            </p>
            <h3 class="mt-4 font-display text-lg font-semibold">{step.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{step.body}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Branches, live from the API -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Where</p>
    <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">Choose the branch nearest you</h2>

    {#if branches.length === 0}
      <p class="mt-6 max-w-2xl text-muted-foreground">
        We are not taking visit bookings this moment. Message us on WhatsApp at {whatsappDisplay}
        and we will arrange one for you.
      </p>
      <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-6')}>
        <MessageCircleIcon size={18} />
        Ask on WhatsApp
      </a>
    {:else}
      <div class="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {#each branches as branch (branch.id)}
          <article class="overflow-hidden rounded-xl border border-border bg-card">
            <img
              src={cityImage(branch.city)}
              alt={`Wedding venue in ${branch.name}`}
              class="h-44 w-full object-cover"
              loading="lazy"
            />
            <div class="p-6">
              <h3 class="font-display text-xl font-semibold">{branch.name}</h3>
              <a
                href={localizeHref(`/tour/${branch.slug}`)}
                class={cn(buttonVariants({ variant: 'gold' }), 'mt-5 w-full')}
              >
                Book a tour here
              </a>
            </div>
          </article>
        {/each}
      </div>
    {/if}
  </section>

  <!-- FAQ -->
  <section class="mx-auto max-w-4xl px-5 py-16 lg:px-8">
    <h2 class="font-display text-3xl font-bold md:text-4xl">Questions couples ask us</h2>
    <div class="mt-8 divide-y divide-border">
      {#each faqs as faq (faq.q)}
        <details class="group py-5">
          <summary class="cursor-pointer list-none font-medium marker:content-none">
            <span class="flex items-start gap-3">
              <CheckIcon class="mt-1 size-4 shrink-0 text-brand-dark-accent" />
              {faq.q}
            </span>
          </summary>
          <p class="mt-3 pl-7 text-[15px] leading-7 text-muted-foreground">{faq.a}</p>
        </details>
      {/each}
    </div>
  </section>

  <!-- Closing CTA -->
  <section class="bg-brand-ink px-5 py-16 text-white lg:px-8">
    <div class="mx-auto max-w-3xl text-center">
      <h2 class="font-display text-3xl font-bold md:text-4xl">Come and see it for yourself</h2>
      <p class="mt-4 text-lg leading-8 text-white/80">
        Free, no obligation, and you pick the time. The hardest part is deciding which day.
      </p>
      <div class="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
        <a href={tourHref} class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
          Book your free tour
        </a>
        <a
          href={waHref}
          class={cn(
            buttonVariants({ size: 'lg' }),
            'border border-white/30 bg-white/10 px-7 text-white backdrop-blur hover:bg-white hover:text-brand-ink'
          )}
        >
          <MessageCircleIcon size={18} />
          {whatsappDisplay}
        </a>
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
