<script lang="ts">
  import SearchIcon from '@lucide/svelte/icons/search';
  import SparklesIcon from '@lucide/svelte/icons/sparkles';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Select from '$lib/components/ui/select';
  import { m } from '$lib/paraglide/messages.js';

  let {
    title,
    subtitle,
    image = '/img/wedding-venue-deal-1920.webp'
  }: {
    title: string;
    subtitle: string;
    image?: string;
  } = $props();

  const cities = $derived([
    { value: '', label: m.search_all_cities() },
    { value: 'jakarta', label: m.city_jakarta() },
    { value: 'tangerang', label: m.city_tangerang() },
    { value: 'bali', label: m.city_bali() },
    { value: 'batam', label: m.city_batam() },
    { value: 'singapore', label: m.city_singapore() }
  ]);

  const ratings = $derived([
    { value: '', label: m.search_any() },
    { value: '5', label: m.stars_5() },
    { value: '4', label: m.stars_4_plus() },
    { value: '3', label: m.stars_3_plus() }
  ]);

  let cityValue = $state('');
  let starsValue = $state('');

  let cityLabel = $derived(cities.find((item) => item.value === cityValue)?.label ?? m.search_all_cities());
  let starsLabel = $derived(ratings.find((item) => item.value === starsValue)?.label ?? m.search_any());
</script>

<section class="relative flex min-h-[660px] items-center overflow-hidden">
  <picture class="absolute inset-0">
    <source media="(min-width: 1280px)" srcset={image} type="image/webp" />
    <source media="(min-width: 768px)" srcset="/img/wedding-venue-deal-1024.webp" type="image/webp" />
    <img
      src="/img/wedding-venue-deal-768.jpg"
      alt="Wedding venue table setting"
      class="h-full w-full object-cover"
    />
  </picture>
  <div class="absolute inset-0 bg-slate-950/35"></div>
  <div class="absolute inset-0 bg-gradient-to-t from-black via-black/35 to-transparent"></div>

  <!-- Padding has to be symmetric: the section centers this block and clips at
       min-height, so a top-only pad pushes the last line out of view once the
       heading wraps to an extra line. -->
  <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-24 lg:px-8">
    <div class="max-w-4xl text-white">
      <div class="inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-2 text-sm backdrop-blur">
        <SparklesIcon size={16} />
        {m.hero_badge()}
      </div>
      <h1 class="mt-6 max-w-4xl text-4xl font-semibold leading-tight md:text-6xl">
        {title}
      </h1>
      <p class="mt-5 max-w-2xl text-lg leading-8 text-white/80">{subtitle}</p>
    </div>

    <form
      action="/wedding-venue/search"
      method="GET"
      class="mt-10 max-w-5xl rounded-md bg-card p-4 shadow-2xl md:flex md:items-end md:gap-3 md:p-6"
    >
      <div class="grid flex-1 gap-2">
        <Label for="hero-q">{m.search_venue_name()}</Label>
        <Input id="hero-q" name="q" placeholder={m.search_venue_placeholder()} />
      </div>

      <div class="mt-4 grid gap-2 md:mt-0 md:w-56">
        <Label>{m.search_city()}</Label>
        <Select.Root type="single" name="city" bind:value={cityValue}>
          <Select.Trigger class="w-full">{cityLabel}</Select.Trigger>
          <Select.Content>
            {#each cities as option (option.label)}
              <Select.Item value={option.value} label={option.label}>{option.label}</Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

      <div class="mt-4 grid gap-2 md:mt-0 md:w-44">
        <Label>{m.search_stars()}</Label>
        <Select.Root type="single" name="stars_min" bind:value={starsValue}>
          <Select.Trigger class="w-full">{starsLabel}</Select.Trigger>
          <Select.Content>
            {#each ratings as option (option.label)}
              <Select.Item value={option.value} label={option.label}>{option.label}</Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

      <Button type="submit" class="mt-5 w-full font-semibold hover:bg-brand-gold-hover md:mt-0 md:w-auto">
        <SearchIcon size={18} />
        {m.search_submit()}
      </Button>
    </form>
  </div>
</section>
