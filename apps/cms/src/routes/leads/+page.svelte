<script lang="ts">
  import DownloadIcon from '@lucide/svelte/icons/download';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import type { AdminLead } from '$lib/api';
  import DateField from '$lib/components/DateField.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Table from '$lib/components/ui/table';
  import { formatDateTime } from '$lib/format-date';

  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const leads = $derived(data.leads.items);
  const pagination = $derived(data.leads.pagination);

  // The stored `source` values. A new wedding tool adds its `tool_<key>` here.
  const SOURCES = [
    { value: 'contact_form', label: 'Contact form' },
    { value: 'venue_pricing', label: 'Venue pricing' },
    { value: 'tool_mahar', label: 'Mahar tool' },
    { value: 'tool_hashtag', label: 'Hashtag tool' },
    { value: 'tool_bazi', label: 'Ba Zi tool' }
  ];
  const sourceLabel = (source: string) =>
    SOURCES.find((item) => item.value === source)?.label ?? source;

  // Re-seeded from the URL on every load, not only at mount: SvelteKit reuses this
  // component across /leads?… navigations, so "Reset" would otherwise keep the
  // previous dates in the pickers.
  let dateFrom = $state('');
  let dateTo = $state('');
  $effect(() => {
    dateFrom = data.filters.date_from;
    dateTo = data.filters.date_to;
  });

  function hrefWith(page: number | null, base = '/leads'): string {
    const query = new URLSearchParams();
    for (const [name, value] of Object.entries(data.filters)) {
      if (value) query.set(name, value);
    }
    if (page && page > 1) query.set('page', String(page));
    const search = query.toString();
    return search ? `${base}?${search}` : base;
  }

  // Already shown in their own columns, or bookkeeping the team does not act on.
  const HIDDEN_KEYS = new Set(['source_path', 'tool', 'consent_at']);

  /** The extras each source stores, flattened to "key: value" pairs for one cell. */
  function details(lead: AdminLead): string[] {
    const pairs: string[] = [];
    for (const [key, value] of Object.entries(lead.metadata ?? {})) {
      if (HIDDEN_KEYS.has(key) || value === null || value === '') continue;
      if (typeof value === 'object') {
        for (const [innerKey, innerValue] of Object.entries(value as Record<string, unknown>)) {
          if (innerValue !== null && innerValue !== '') pairs.push(`${innerKey}: ${innerValue}`);
        }
      } else {
        pairs.push(`${key.replaceAll('_', ' ')}: ${value}`);
      }
    }
    return pairs;
  }
</script>

<PageHeader
  title="Leads"
  description="Contact form, venue pricing and wedding-tool leads. Read-only."
>
  {#snippet actions()}
    <!-- Proxied through the CMS: the session token lives in a server-side cookie,
         so a link straight at the API origin would download a 401. -->
    <Button variant="outline" size="sm" href={hrefWith(null, '/leads/export')} data-sveltekit-reload>
      <DownloadIcon class="size-4" />
      Export CSV
    </Button>
  {/snippet}
</PageHeader>

<!-- A GET form: the filters live in the URL, so a filtered list can be linked and
     reloaded, and the export link above carries the same query. -->
<form method="GET" class="mb-4 grid gap-4 rounded-xl border border-border/60 bg-background p-4 sm:grid-cols-2 lg:grid-cols-5">
  <div class="grid gap-2">
    <Label for="source">Source</Label>
    <select
      id="source"
      name="source"
      class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
      value={data.filters.source}
    >
      <option value="">All sources</option>
      {#each SOURCES as source (source.value)}
        <option value={source.value}>{source.label}</option>
      {/each}
    </select>
  </div>
  <div class="grid gap-2">
    <Label for="q">Search</Label>
    <Input id="q" name="q" value={data.filters.q} placeholder="Name, email, phone, message" />
  </div>
  <div class="grid gap-2">
    <Label for="date_from">From</Label>
    <DateField name="date_from" bind:value={dateFrom} />
  </div>
  <div class="grid gap-2">
    <Label for="date_to">To</Label>
    <DateField name="date_to" bind:value={dateTo} min={dateFrom} />
  </div>
  <div class="flex items-end gap-2">
    <Button type="submit">Filter</Button>
    <Button variant="ghost" href="/leads">Reset</Button>
  </div>
</form>

{#if data.error}
  <div
    class="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
  >
    <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
    <span>{data.error}</span>
  </div>
{:else}
  <p class="mb-4 text-sm text-muted-foreground">
    {pagination.total} lead{pagination.total === 1 ? '' : 's'} · dates in Jakarta time
  </p>

  <Card.Root>
    <Card.Content class="p-0">
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.Head>Date</Table.Head>
            <Table.Head>Source</Table.Head>
            <Table.Head>Name</Table.Head>
            <Table.Head>Email</Table.Head>
            <Table.Head>Phone</Table.Head>
            <Table.Head>Page</Table.Head>
            <Table.Head>Details</Table.Head>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {#each leads as lead (lead.id)}
            <Table.Row class="align-top">
              <Table.Cell class="text-sm whitespace-nowrap text-muted-foreground">
                {formatDateTime(lead.created_at)}
              </Table.Cell>
              <Table.Cell class="text-sm whitespace-nowrap">{sourceLabel(lead.source)}</Table.Cell>
              <Table.Cell class="font-medium">{lead.full_name ?? '—'}</Table.Cell>
              <Table.Cell class="text-sm">
                {#if lead.email}
                  <a href={`mailto:${lead.email}`} class="hover:underline">{lead.email}</a>
                {:else}—{/if}
              </Table.Cell>
              <Table.Cell class="text-sm whitespace-nowrap">{lead.mobile ?? '—'}</Table.Cell>
              <Table.Cell class="max-w-48 truncate text-xs text-muted-foreground" title={lead.source_path ?? ''}>
                {lead.source_path ?? '—'}
              </Table.Cell>
              <Table.Cell class="max-w-md text-xs whitespace-normal">
                {#if lead.message}
                  <p class="line-clamp-3" title={lead.message}>{lead.message}</p>
                {/if}
                {#each details(lead) as pair (pair)}
                  <p class="text-muted-foreground">{pair}</p>
                {/each}
              </Table.Cell>
            </Table.Row>
          {:else}
            <Table.Row>
              <Table.Cell colspan={7} class="text-center text-sm text-muted-foreground">
                No leads match these filters.
              </Table.Cell>
            </Table.Row>
          {/each}
        </Table.Body>
      </Table.Root>
    </Card.Content>
  </Card.Root>

  {#if pagination.total_pages > 1}
    <div class="mt-4 flex items-center justify-between">
      <Button
        variant="outline"
        size="sm"
        href={pagination.page > 1 ? hrefWith(pagination.page - 1) : undefined}
        disabled={pagination.page <= 1}
      >
        Previous
      </Button>
      <span class="text-sm text-muted-foreground">
        Page {pagination.page} of {pagination.total_pages}
      </span>
      <Button
        variant="outline"
        size="sm"
        href={pagination.page < pagination.total_pages ? hrefWith(pagination.page + 1) : undefined}
        disabled={pagination.page >= pagination.total_pages}
      >
        Next
      </Button>
    </div>
  {/if}
{/if}
