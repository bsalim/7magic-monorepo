<script lang="ts">
  import Compass from '@lucide/svelte/icons/compass';
  import SearchIcon from '@lucide/svelte/icons/search';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Select from '$lib/components/ui/select';
  import { m } from '$lib/paraglide/messages.js';
  import { localizeHref } from '$lib/paraglide/runtime';

  let {
    title,
    subtitle
  }: {
    title: string;
    subtitle: string;
  } = $props();

  // Jakarta and Bali are the two markets the hero has to sell hardest, so the
  // banner rotates between them rather than picking one over the other.
  const banners = ['/img/hero-jakarta.jpg', '/img/hero-bali.jpg'];
  let activeBanner = $state(0);

  $effect(() => {
    const id = setInterval(() => {
      activeBanner = (activeBanner + 1) % banners.length;
    }, 6000);
    return () => clearInterval(id);
  });

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

  const quickLinks = [
    { label: 'Jakarta venues', href: '/wedding-venue/search?city=jakarta' },
    { label: 'Bali venues', href: '/wedding-venue/search?city=bali' },
    { label: 'Batam venues', href: '/wedding-venue/search?city=batam' },
    { label: '5-star hotels', href: '/wedding-venue/search?stars_min=5' },
    { label: 'Ballroom packages', href: '/wedding-venue/search?q=ballroom' },
    { label: 'Chapel & garden', href: '/wedding-venue/search?q=chapel' }
  ];
</script>

<!-- The banners are pre-designed marketing posters (price, offer, feature
     icons all baked into the artwork), not photography meant to carry
     overlaid copy. The section is sized to the images' own 1920x1080 ratio
     so nothing in the artwork gets cropped, and the title/subtitle stay for
     SEO and screen readers without being drawn on top of it. -->
<section class="relative aspect-video w-full overflow-hidden bg-white">
  {#each banners as banner, index (banner)}
    <img
      src={banner}
      alt=""
      class="absolute inset-0 h-full w-full object-contain transition-opacity duration-1000"
      style:opacity={index === activeBanner ? 1 : 0}
    />
  {/each}
  <h1 class="sr-only">{title}</h1>
  <p class="sr-only">{subtitle}</p>
</section>

<!-- The search form and the quick-link shortcuts used to be two separate
     sections; combined here so the whole "act on the hero" block reads as
     one dark bar right under the banner instead of a white card followed by
     a second, visually unrelated strip. -->
<div class="bg-brand-ink px-5 py-6 text-white lg:px-8">
  <div class="mx-auto max-w-7xl">
    <!-- A form action is a navigation like any other, and this one is the main
         one on the site: a bare /wedding-venue/search dropped an English visitor
         onto the Indonesian results the moment they searched. -->
    <form
      action={localizeHref('/wedding-venue/search')}
      method="GET"
      class="rounded-md bg-card p-4 text-slate-900 shadow-2xl md:flex md:items-end md:gap-3 md:p-6"
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

    <div class="mt-5 flex flex-wrap items-center gap-3">
      <span class="inline-flex items-center gap-2 text-sm font-semibold text-white/72">
        <Compass size={16} />
        Browse fast
      </span>
      {#each quickLinks as item}
        <a
          href={localizeHref(item.href)}
          class="rounded-full border border-white/18 bg-white/8 px-4 py-2 text-sm font-semibold text-white/88 transition hover:bg-white hover:text-brand-ink"
        >
          {item.label}
        </a>
      {/each}
    </div>
  </div>
</div>
