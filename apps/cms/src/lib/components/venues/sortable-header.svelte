<script lang="ts">
  import ArrowUpIcon from '@lucide/svelte/icons/arrow-up';
  import ArrowDownIcon from '@lucide/svelte/icons/arrow-down';
  import ChevronsUpDownIcon from '@lucide/svelte/icons/chevrons-up-down';
  import type { Column } from '@tanstack/table-core';

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let { column, label }: { column: Column<any, unknown>; label: string } = $props();

  const sorted = $derived(column.getIsSorted());
</script>

<button
  type="button"
  class="-ml-2 inline-flex h-8 items-center gap-1.5 rounded-md px-2 text-sm font-medium hover:bg-muted"
  onclick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
>
  {label}
  {#if sorted === 'asc'}
    <ArrowUpIcon class="size-3.5" />
  {:else if sorted === 'desc'}
    <ArrowDownIcon class="size-3.5" />
  {:else}
    <ChevronsUpDownIcon class="size-3.5 text-muted-foreground/60" />
  {/if}
</button>
