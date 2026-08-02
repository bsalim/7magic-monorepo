<script lang="ts">
  import type { Component } from 'svelte';
  import MapPinIcon from '@lucide/svelte/icons/map-pin';
  import CircleCheckIcon from '@lucide/svelte/icons/circle-check';
  import PencilRulerIcon from '@lucide/svelte/icons/pencil-ruler';
  import FileTextIcon from '@lucide/svelte/icons/file-text';
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Separator } from '$lib/components/ui/separator';
  import PageHeader from '$lib/components/PageHeader.svelte';

  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const venuesTotal = $derived(data.summary?.venues.total ?? data.venues.length);
  const venuesActive = $derived(data.summary?.venues.active ?? 0);
  const venuesDraft = $derived(data.summary?.venues.draft ?? 0);
  const articlesTotal = $derived(data.summary?.totals.articles ?? data.articles.length);
  const recentActivity = $derived(data.summary?.recent_activity ?? []);

  type Stat = {
    label: string;
    value: number;
    hint: string;
    icon: Component;
    tone: string;
  };

  const stats = $derived<Stat[]>([
    {
      label: 'Venues',
      value: venuesTotal,
      hint: 'Total in catalog',
      icon: MapPinIcon,
      tone: 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200'
    },
    {
      label: 'Active',
      value: venuesActive,
      hint: 'Published venues',
      icon: CircleCheckIcon,
      tone: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400'
    },
    {
      label: 'Draft',
      value: venuesDraft,
      hint: 'Awaiting review',
      icon: PencilRulerIcon,
      tone: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400'
    },
    {
      label: 'Articles',
      value: articlesTotal,
      hint: 'Editorial records',
      icon: FileTextIcon,
      tone: 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-400'
    }
  ]);

  const formatDate = (value: string) =>
    new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(value));
</script>

<svelte:head>
  <title>Dashboard | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title="Dashboard"
  description="Monitor venue coverage, publishing status, and recent admin activity."
>
  {#snippet actions()}
    <Button href="/venues">
      Manage venues
      <ArrowRightIcon class="size-4" />
    </Button>
  {/snippet}
</PageHeader>

{#if data.error}
  <div
    class="mb-6 flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
  >
    <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
    <span>{data.error}</span>
  </div>
{/if}

<section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
  {#each stats as stat (stat.label)}
    {@const Icon = stat.icon}
    <Card.Root>
      <Card.Content class="flex items-start justify-between gap-3">
        <div>
          <p class="text-sm font-medium text-muted-foreground">{stat.label}</p>
          <p class="mt-2 text-3xl font-bold tracking-tight">{stat.value.toLocaleString('id-ID')}</p>
          <p class="mt-1 text-xs text-muted-foreground">{stat.hint}</p>
        </div>
        <span class={`flex size-10 items-center justify-center rounded-lg ${stat.tone}`}>
          <Icon class="size-5" />
        </span>
      </Card.Content>
    </Card.Root>
  {/each}
</section>

<section class="mt-6 grid gap-6 xl:grid-cols-[1.4fr_1fr]">
  <Card.Root>
    <Card.Header>
      <Card.Title>Venue coverage</Card.Title>
      <Card.Description>Breakdown of the venue catalog by status.</Card.Description>
    </Card.Header>
    <Card.Content class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-lg border p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-muted-foreground">Total</p>
        <p class="mt-2 text-2xl font-bold">{venuesTotal.toLocaleString('id-ID')}</p>
      </div>
      <div class="rounded-lg border p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-muted-foreground">Active</p>
        <p class="mt-2 text-2xl font-bold text-emerald-600">{venuesActive.toLocaleString('id-ID')}</p>
      </div>
      <div class="rounded-lg border p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-muted-foreground">Draft</p>
        <p class="mt-2 text-2xl font-bold text-amber-600">{venuesDraft.toLocaleString('id-ID')}</p>
      </div>
      <div class="rounded-lg border p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-muted-foreground">Archived</p>
        <p class="mt-2 text-2xl font-bold">
          {(data.summary?.venues.archived ?? 0).toLocaleString('id-ID')}
        </p>
      </div>
    </Card.Content>
    <Card.Footer>
      <Button variant="outline" href="/venues" class="w-full sm:w-auto">Open venue management</Button>
    </Card.Footer>
  </Card.Root>

  <Card.Root>
    <Card.Header>
      <Card.Title>Recent activity</Card.Title>
      <Card.Description>Latest admin events.</Card.Description>
    </Card.Header>
    <Card.Content>
      {#if recentActivity.length}
        <ul class="space-y-3">
          {#each recentActivity.slice(0, 6) as activity, index (activity.id)}
            {#if index > 0}<Separator />{/if}
            <li class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-sm font-medium capitalize">
                  {activity.action} <span class="text-muted-foreground">· {activity.entity}</span>
                </p>
                <p class="mt-0.5 text-xs text-muted-foreground">by {activity.actor}</p>
              </div>
              <time class="shrink-0 text-xs text-muted-foreground">{formatDate(activity.created_at)}</time>
            </li>
          {/each}
        </ul>
      {:else}
        <div
          class="rounded-lg border border-dashed px-4 py-8 text-center text-sm text-muted-foreground"
        >
          No recent activity.
        </div>
      {/if}
    </Card.Content>
  </Card.Root>
</section>
