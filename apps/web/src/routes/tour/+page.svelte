<script lang="ts">
  import MapPinIcon from '@lucide/svelte/icons/map-pin';

  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import * as m from '$lib/paraglide/messages';

  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<svelte:head>
  <title>{m.tour_meta_title()}</title>
  <meta name="description" content={m.tour_meta_description()} />
</svelte:head>

<PublicHeader />

<main class="mx-auto w-full max-w-5xl px-4 py-12">
  <h1 class="text-3xl font-semibold">{m.tour_title()}</h1>
  <p class="mt-3 max-w-2xl text-muted-foreground">{m.tour_intro()}</p>

  <h2 class="mt-10 mb-4 text-lg font-medium">{m.tour_branch_pick()}</h2>

  {#if data.branches.length === 0}
    <p class="text-muted-foreground">{m.tour_empty()}</p>
  {:else}
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each data.branches as branch (branch.id)}
        <Card.Root>
          <Card.Header>
            <Card.Title>{branch.name}</Card.Title>
            <Card.Description class="flex items-center gap-1">
              <MapPinIcon class="size-4" />
              {branch.city}
            </Card.Description>
          </Card.Header>
          <Card.Content class="text-sm text-muted-foreground">
            <p>{branch.addressLine1}</p>
            {#if branch.addressLine2}<p>{branch.addressLine2}</p>{/if}
          </Card.Content>
          <Card.Footer>
            <Button href={`/tour/${branch.slug}`}>{m.tour_branch_pick()}</Button>
          </Card.Footer>
        </Card.Root>
      {/each}
    </div>
  {/if}
</main>

<PublicFooter />
