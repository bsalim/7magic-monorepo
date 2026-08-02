<script lang="ts">
  import { untrack } from 'svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Select from '$lib/components/ui/select';
  import { m } from '$lib/paraglide/messages.js';
  import { cn } from '$lib/utils';

  let {
    q = '',
    city = '',
    starsMin = '',
    stars = []
  }: {
    q?: string;
    city?: string;
    starsMin?: string;
    stars?: string[];
  } = $props();

  const cities = $derived([
    { value: '', label: m.search_all_cities() },
    { value: 'jakarta', label: m.city_jakarta() },
    { value: 'tangerang', label: m.city_tangerang() },
    { value: 'bali', label: m.city_bali() },
    { value: 'batam', label: m.city_batam() },
    { value: 'singapore', label: m.city_singapore() }
  ]);

  // Exact ratings, not "and above": each box is independent, so 5 and 3 can be
  // ticked without dragging 4 along. Only 3-5 are offered because that is what
  // the catalogue actually holds beyond a handful of unrated rows.
  const ratings = $derived([
    { value: '5', label: m.stars_5() },
    { value: '4', label: m.stars_4() },
    { value: '3', label: m.stars_3() }
  ]);

  // Props seed the initial selection only; the user's choice owns it from then on.
  let cityValue = $state(untrack(() => city));
  // A legacy ?stars_min=N link has no tick-boxes of its own, so pre-tick every
  // rating that link would have matched. Otherwise arriving from the hero search
  // shows a filtered list with nothing ticked.
  let starsValues = $state(
    untrack(() => {
      if (stars.length) return [...stars];
      const min = Number(starsMin);
      return min ? ['5', '4', '3'].filter((value) => Number(value) >= min) : [];
    })
  );

  let cityLabel = $derived(cities.find((item) => item.value === cityValue)?.label ?? m.search_all_cities());

  function toggleStar(value: string, checked: boolean) {
    starsValues = checked
      ? [...starsValues, value]
      : starsValues.filter((entry) => entry !== value);
  }
</script>

<form
  method="GET"
  action="/wedding-venue/search"
  class="rounded-md border border-border bg-card p-5 shadow-sm"
>
  <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">{m.filter_title()}</p>

  <div class="mt-5 grid gap-2">
    <Label for="filter-q">{m.search_venue_name()}</Label>
    <Input id="filter-q" name="q" value={q} placeholder={m.filter_search_placeholder()} />
  </div>

  <div class="mt-4 grid gap-2">
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

  <fieldset class="mt-4 grid gap-2">
    <legend class="mb-2 text-sm font-medium">{m.filter_stars()}</legend>
    <!-- Plain checkboxes rather than a JS-managed control: a GET form submits
         one ?stars= entry per ticked box on its own, so the filter still works
         with JavaScript unavailable and the URL stays shareable. -->
    {#each ratings as option (option.value)}
      <label
        class="flex cursor-pointer items-center gap-3 rounded-md px-1 py-1.5 text-[15px] transition hover:bg-muted"
      >
        <input
          type="checkbox"
          name="stars"
          value={option.value}
          checked={starsValues.includes(option.value)}
          onchange={(event) => toggleStar(option.value, event.currentTarget.checked)}
          class="size-4 shrink-0 accent-brand-gold"
        />
        <span>{option.label}</span>
      </label>
    {/each}
    <p class="mt-1 text-xs text-muted-foreground">{m.filter_stars_hint()}</p>
  </fieldset>

  <Button type="submit" class="mt-5 w-full font-semibold hover:bg-brand-gold-hover">
    {m.filter_apply()}
  </Button>
  <a
    href="/wedding-venue/search"
    class={cn(buttonVariants({ variant: 'link' }), 'mt-1 w-full text-accent-foreground')}
  >
    {m.filter_reset()}
  </a>
</form>
