<script lang="ts">
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';

  const vendors = [
    { name: 'Venue Partners', image: '/img/kempinski-hotel-jakpus.jpg', detail: 'Hotel ballrooms and destination venues' },
    { name: 'Editorial Partners', image: '/img/wedding-venue-deal-768.jpg', detail: 'Planning guides and package explainers' },
    { name: 'Celebration Partners', image: '/img/hero-home.jpg', detail: 'Wedding support across shortlisted cities' }
  ];
</script>

<svelte:head>
  <title>Our Vendors | 7Magic Wedding</title>
  <meta name="description" content="7Magic Wedding vendor and venue partner gallery." />
</svelte:head>

<main class="min-h-screen bg-background text-slate-900">
  <PublicHeader />
  <section class="mx-auto max-w-7xl px-5 py-12 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Vendor network</p>
    <h1 class="mt-3 text-4xl font-semibold md:text-5xl">Venue and wedding partners</h1>
    <p class="mt-4 max-w-2xl leading-7 text-slate-600">
      A simple public gallery surface for partners while detailed vendor CRM remains outside this migration pass.
    </p>

    <div class="mt-8 grid gap-5 md:grid-cols-3">
      {#each vendors as vendor}
        <article class="overflow-hidden rounded-md border border-border bg-white shadow-sm">
          <img src={vendor.image} alt={vendor.name} class="h-56 w-full object-cover" />
          <div class="p-5">
            <h2 class="text-xl font-semibold">{vendor.name}</h2>
            <p class="mt-2 text-sm leading-6 text-slate-600">{vendor.detail}</p>
          </div>
        </article>
      {/each}
    </div>
  </section>
  <PublicFooter />
</main>
