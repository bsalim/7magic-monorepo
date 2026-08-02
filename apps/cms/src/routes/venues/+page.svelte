<script lang="ts">
  import {
    type ColumnDef,
    type ColumnFiltersState,
    type PaginationState,
    type SortingState,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel
  } from '@tanstack/table-core';
  import PlusIcon from '@lucide/svelte/icons/plus';
  import SearchIcon from '@lucide/svelte/icons/search';
  import XIcon from '@lucide/svelte/icons/x';
  import ChevronLeftIcon from '@lucide/svelte/icons/chevron-left';
  import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import type { AdminVenue } from '$lib/api';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Select from '$lib/components/ui/select';
  import * as Table from '$lib/components/ui/table';
  import {
    FlexRender,
    createSvelteTable,
    renderComponent,
    renderSnippet
  } from '$lib/components/ui/data-table';
  import ActionsCell from '$lib/components/venues/actions-cell.svelte';
  import CoverCell from '$lib/components/venues/cover-cell.svelte';
  import SortableHeader from '$lib/components/venues/sortable-header.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import Stars from '$lib/components/Stars.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';

  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const formatPrice = (value: number | null) =>
    value === null ? 'Contact us' : `Rp ${value.toLocaleString('id-ID')}`;

  // Distinct cities for the faceted city filter.
  const cities = $derived(
    Array.from(new Set(data.venues.map((v) => v.city))).sort((a, b) => a.localeCompare(b))
  );
  const ALL = '__all__';

  let sorting = $state<SortingState>([]);
  let pagination = $state<PaginationState>({ pageIndex: 0, pageSize: 12 });

  // Toolbar-bound values, derived straight into the table's column filters.
  let nameQuery = $state('');
  let cityValue = $state(ALL);
  let starsValue = $state(ALL);

  const columnFilters = $derived.by<ColumnFiltersState>(() => {
    const filters: ColumnFiltersState = [];
    if (nameQuery.trim() !== '') filters.push({ id: 'name', value: nameQuery.trim() });
    if (cityValue !== ALL) filters.push({ id: 'city', value: cityValue });
    if (starsValue !== ALL) filters.push({ id: 'stars', value: starsValue });
    return filters;
  });

  const hasFilters = $derived(nameQuery !== '' || cityValue !== ALL || starsValue !== ALL);

  function clearFilters() {
    nameQuery = '';
    cityValue = ALL;
    starsValue = ALL;
  }

  const columns: ColumnDef<AdminVenue>[] = [
    {
      id: 'cover',
      header: '',
      enableSorting: false,
      cell: ({ row }) =>
        renderComponent(CoverCell, {
          src: row.original.cover_photo?.small_url,
          alt: row.original.cover_photo?.alt ?? row.original.name
        })
    },
    {
      accessorKey: 'name',
      header: ({ column }) => renderComponent(SortableHeader, { column, label: 'Name' }),
      filterFn: (row, columnId, filterValue: string) =>
        String(row.getValue(columnId)).toLowerCase().includes(filterValue.toLowerCase()),
      cell: ({ row }) => renderSnippet(nameCell, row.original)
    },
    {
      accessorKey: 'city',
      header: 'City',
      filterFn: (row, columnId, filterValue: string) => row.getValue(columnId) === filterValue,
      cell: ({ row }) => renderSnippet(cityCell, row.original.city)
    },
    {
      accessorKey: 'stars',
      header: ({ column }) => renderComponent(SortableHeader, { column, label: 'Stars' }),
      filterFn: (row, columnId, filterValue: string) =>
        String(row.getValue(columnId)) === filterValue,
      cell: ({ row }) => renderComponent(Stars, { value: row.original.stars })
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => renderComponent(StatusBadge, { status: row.original.status })
    },
    {
      accessorKey: 'price_start_from',
      header: ({ column }) => renderComponent(SortableHeader, { column, label: 'Starting price' }),
      sortUndefined: 'last',
      cell: ({ row }) => renderSnippet(priceCell, row.original.price_start_from)
    },
    {
      id: 'actions',
      header: () => renderSnippet(actionsHeader, undefined),
      enableSorting: false,
      cell: ({ row }) =>
        renderComponent(ActionsCell, { id: row.original.id, name: row.original.name })
    }
  ];

  const table = createSvelteTable({
    get data() {
      return data.venues;
    },
    columns,
    getRowId: (row) => String(row.id),
    state: {
      get sorting() {
        return sorting;
      },
      get columnFilters() {
        return columnFilters;
      },
      get pagination() {
        return pagination;
      }
    },
    onSortingChange: (updater) => {
      sorting = typeof updater === 'function' ? updater(sorting) : updater;
    },
    onPaginationChange: (updater) => {
      pagination = typeof updater === 'function' ? updater(pagination) : updater;
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel()
  });

  const filteredCount = $derived(table.getFilteredRowModel().rows.length);
  const totalCount = $derived(data.venues.length);
</script>

<svelte:head>
  <title>Venues | 7Magic CMS</title>
</svelte:head>

{#snippet nameCell(venue: AdminVenue)}
  <div class="min-w-0">
    <a href={`/venues/${venue.id}`} class="font-medium hover:text-brand hover:underline">
      {venue.name}
    </a>
    <p class="text-xs text-muted-foreground">{venue.district}</p>
  </div>
{/snippet}

{#snippet cityCell(city: string)}
  <span class="capitalize">{city}</span>
{/snippet}

{#snippet priceCell(price: number | null)}
  {#if price === null}
    <span class="text-muted-foreground">Contact us</span>
  {:else}
    <span class="font-medium tabular-nums">{formatPrice(price)}</span>
  {/if}
{/snippet}

{#snippet actionsHeader()}
  <span class="sr-only">Actions</span>
{/snippet}

<PageHeader
  title="Venues"
  description="Search, filter, and manage the wedding-venue catalog."
>
  {#snippet actions()}
    <Button href="/venues/new">
      <PlusIcon class="size-4" />
      New venue
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

<!-- Toolbar -->
<div class="mb-4 flex flex-col gap-3 lg:flex-row lg:flex-wrap lg:items-end">
  <div class="grid gap-1.5 lg:w-72">
    <Label for="venue-search" class="text-xs text-muted-foreground">Search</Label>
    <div class="relative">
      <SearchIcon
        class="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
      />
      <Input
        id="venue-search"
        bind:value={nameQuery}
        placeholder="Search by name…"
        class="pl-8"
      />
    </div>
  </div>

  <div class="grid gap-1.5 lg:w-44">
    <Label class="text-xs text-muted-foreground">City</Label>
    <Select.Root type="single" bind:value={cityValue}>
      <Select.Trigger class="w-full">
        <span class="capitalize">{cityValue === ALL ? 'All cities' : cityValue}</span>
      </Select.Trigger>
      <Select.Content>
        <Select.Item value={ALL}>All cities</Select.Item>
        {#each cities as city (city)}
          <Select.Item value={city}><span class="capitalize">{city}</span></Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  </div>

  <div class="grid gap-1.5 lg:w-36">
    <Label class="text-xs text-muted-foreground">Stars</Label>
    <Select.Root type="single" bind:value={starsValue}>
      <Select.Trigger class="w-full">
        {starsValue === ALL ? 'All stars' : `${starsValue} ★`}
      </Select.Trigger>
      <Select.Content>
        <Select.Item value={ALL}>All stars</Select.Item>
        {#each [5, 4, 3, 2, 1] as n (n)}
          <Select.Item value={String(n)}>{n} ★</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  </div>

  {#if hasFilters}
    <Button variant="ghost" onclick={clearFilters} class="lg:mb-0">
      <XIcon class="size-4" />
      Clear filters
    </Button>
  {/if}
</div>

<!-- Table -->
<div class="overflow-hidden rounded-lg border bg-card">
  <div class="overflow-x-auto">
    <Table.Root>
      <Table.Header>
        {#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
          <Table.Row>
            {#each headerGroup.headers as header (header.id)}
              <Table.Head
                class={header.column.id === 'actions' ? 'text-right' : undefined}
              >
                {#if !header.isPlaceholder}
                  <FlexRender
                    content={header.column.columnDef.header}
                    context={header.getContext()}
                  />
                {/if}
              </Table.Head>
            {/each}
          </Table.Row>
        {/each}
      </Table.Header>
      <Table.Body>
        {#each table.getRowModel().rows as row (row.id)}
          <Table.Row>
            {#each row.getVisibleCells() as cell (cell.id)}
              <Table.Cell class={cell.column.id === 'actions' ? 'text-right' : undefined}>
                <FlexRender content={cell.column.columnDef.cell} context={cell.getContext()} />
              </Table.Cell>
            {/each}
          </Table.Row>
        {:else}
          <Table.Row>
            <Table.Cell colspan={columns.length} class="h-32 text-center text-muted-foreground">
              No venues match the current filters.
            </Table.Cell>
          </Table.Row>
        {/each}
      </Table.Body>
    </Table.Root>
  </div>
</div>

<!-- Footer / pagination -->
<div class="mt-4 flex flex-col items-center justify-between gap-3 sm:flex-row">
  <p class="text-sm text-muted-foreground">
    Showing {table.getRowModel().rows.length} of {filteredCount}
    {#if filteredCount !== totalCount}<span> (filtered from {totalCount})</span>{/if}
    venues
  </p>
  <div class="flex items-center gap-2">
    <span class="text-sm text-muted-foreground">
      Page {pagination.pageIndex + 1} of {Math.max(1, table.getPageCount())}
    </span>
    <Button
      variant="outline"
      size="icon-sm"
      onclick={() => table.previousPage()}
      disabled={!table.getCanPreviousPage()}
      aria-label="Previous page"
    >
      <ChevronLeftIcon class="size-4" />
    </Button>
    <Button
      variant="outline"
      size="icon-sm"
      onclick={() => table.nextPage()}
      disabled={!table.getCanNextPage()}
      aria-label="Next page"
    >
      <ChevronRightIcon class="size-4" />
    </Button>
  </div>
</div>
