<script lang="ts">
  import AwardIcon from '@lucide/svelte/icons/award';
  import HeartIcon from '@lucide/svelte/icons/heart';
  import SparklesIcon from '@lucide/svelte/icons/sparkles';
  import UsersIcon from '@lucide/svelte/icons/users';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { buttonVariants } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { cn } from '$lib/utils';
  import { localizeHref } from '$lib/paraglide/runtime';

  // Copy ported from the production site at https://7magicwedding.com/about
  const pillars = [
    {
      icon: AwardIcon,
      title: '18+ Years of Excellence',
      body: 'With almost 2 decades of experience, we bring unmatched expertise to your special day.'
    },
    {
      icon: UsersIcon,
      title: 'Dedicated Team',
      body: 'Our passionate experts handle every detail with precision and personalized attention.'
    },
    {
      icon: SparklesIcon,
      title: 'Magical Experiences',
      body: 'We create unforgettable moments that you and your guests will cherish forever.'
    }
  ];

  const stats = [
    { value: '18+', label: 'Years of Excellence' },
    { value: '1000+', label: 'Weddings Organized' },
    { value: '100+', label: 'Premium Vendors' },
    { value: '13K', label: 'Instagram Followers' }
  ];
</script>

<svelte:head>
  <title>About 7Magic Wedding | Crafting Magical Moments since 2007</title>
  <meta
    name="description"
    content="Since 2007, 7Magic Organizer has been crafting unforgettable wedding experiences throughout Indonesia and Singapore."
  />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="border-b border-border bg-brand-warm px-5 py-16 lg:px-8 lg:py-20">
    <div class="mx-auto max-w-4xl text-center">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">About</p>
      <h1 class="mt-4 text-4xl font-semibold leading-tight md:text-5xl">
        Crafting Magical Moments since 2007
      </h1>
      <p class="mt-5 text-lg leading-8 text-muted-foreground">
        Your dream wedding, expertly planned and flawlessly executed
      </p>
    </div>
  </section>

  <!-- Story -->
  <section class="px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-3xl">
      <h2 class="text-3xl font-semibold md:text-4xl">Create Your Magical Wedding</h2>
      <div class="mt-6 grid gap-5 leading-8 text-muted-foreground">
        <p>
          Since 2007, 7Magic Organizer has been crafting unforgettable wedding experiences
          throughout Indonesia and Singapore. With thousands of successful celebrations behind us,
          we've established ourselves as the premier wedding planning partner for couples who demand
          excellence.
        </p>
        <p>
          Our dedicated team of experienced planners transforms your vision into reality, handling
          every detail with precision and care. From grand ballroom celebrations with thousands of
          guests to intimate ceremonies for your closest loved ones, we bring the same level of
          passion and professionalism to every event.
        </p>
      </div>
      <a
        href={localizeHref('/contact')}
        class={cn(buttonVariants({ size: 'lg' }), 'mt-8 font-semibold hover:bg-brand-gold-hover')}
      >
        <HeartIcon size={18} />
        Start Planning Your Dream Wedding!
      </a>
    </div>
  </section>

  <!-- Why choose -->
  <section class="border-y border-border bg-brand-warm px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-6xl">
      <h2 class="text-center text-3xl font-semibold md:text-4xl">Why Choose 7Magic Organizer?</h2>
      <div class="mt-10 grid gap-6 md:grid-cols-3">
        {#each pillars as pillar (pillar.title)}
          <Card.Root class="gap-0 py-0 shadow-sm">
            <Card.Content class="p-6">
              <span
                class="flex size-11 items-center justify-center rounded-md bg-brand-warm-deep text-accent-foreground"
              >
                <pillar.icon size={22} />
              </span>
              <h3 class="mt-5 text-xl font-semibold">{pillar.title}</h3>
              <p class="mt-3 text-sm leading-7 text-muted-foreground">{pillar.body}</p>
            </Card.Content>
          </Card.Root>
        {/each}
      </div>
    </div>
  </section>

  <!-- Stats -->
  <section class="px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-6xl text-center">
      <h2 class="text-3xl font-semibold md:text-4xl">Trusted by Over 1,000 Couples</h2>
      <p class="mt-3 text-muted-foreground">
        Numbers that speak for our excellence and commitment
      </p>
      <div class="mt-10 grid grid-cols-2 gap-6 md:grid-cols-4">
        {#each stats as stat (stat.label)}
          <div class="rounded-md border border-border bg-card p-6 shadow-sm">
            <p class="text-3xl font-semibold text-accent-foreground md:text-4xl">{stat.value}</p>
            <p class="mt-2 text-sm text-muted-foreground">{stat.label}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
