<script lang="ts">
  import ArrowLeftIcon from '@lucide/svelte/icons/arrow-left';
  import type { Snippet } from 'svelte';

  let {
    title,
    description = '',
    backHref = '',
    backLabel = '',
    actions
  }: {
    title: string;
    description?: string;
    backHref?: string;
    backLabel?: string;
    actions?: Snippet;
  } = $props();
</script>

<div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
  <div class="min-w-0">
    {#if backHref}
      <a
        href={backHref}
        class="mb-2 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition hover:text-foreground"
      >
        <ArrowLeftIcon class="size-4" />
        {backLabel}
      </a>
    {/if}
    <h1 class="text-2xl font-bold tracking-tight sm:text-3xl">{title}</h1>
    {#if description}
      <p class="mt-1.5 max-w-2xl text-sm text-muted-foreground">{description}</p>
    {/if}
  </div>

  {#if actions}
    <div class="flex shrink-0 flex-wrap items-center gap-2">
      {@render actions()}
    </div>
  {/if}
</div>
