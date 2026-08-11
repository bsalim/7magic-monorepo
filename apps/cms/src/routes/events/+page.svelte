<script lang="ts">
  import { enhance } from '$app/forms';
  import { goto } from '$app/navigation';
  import PlusIcon from '@lucide/svelte/icons/plus';

  import type { AdminBranch, AdminEvent } from '$lib/api';
  import DateTimeField from '$lib/components/DateTimeField.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Table from '$lib/components/ui/table';
  import { formatDateRange } from '$lib/format-date';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const events = $derived(data.events as AdminEvent[]);
  const branches = $derived(data.branches as AdminBranch[]);

  let showCreate = $state(false);
  let opensAt = $state('');
  let closesAt = $state('');

  // Branch is a filter, not a mode: the selection lives in the URL so a filtered
  // list can be linked and reloaded.
  function onFilterChange(event: Event) {
    const value = (event.currentTarget as HTMLSelectElement).value;
    goto(value ? `/events?branch_id=${value}` : '/events', { keepFocus: true });
  }
</script>

<PageHeader title="Events" description="Book a Tour and other events, per branch." />

{#if data.error}<p class="mb-4 text-sm text-destructive">{data.error}</p>{/if}
{#if form?.message}<p class="mb-4 text-sm text-destructive">{form.message}</p>{/if}

<div class="mb-4 flex items-end justify-between gap-4">
  <div class="grid gap-2">
    <Label for="branchFilter">Branch</Label>
    <select
      id="branchFilter"
      class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
      value={data.branchId}
      onchange={onFilterChange}
    >
      <option value="">All branches</option>
      {#each branches as branch (branch.id)}
        <!-- String, not number: branch_id comes off the URL as a string, and a
             numeric option value never matches it, leaving the filter blank. -->
        <option value={String(branch.id)}>{branch.name}</option>
      {/each}
    </select>
  </div>

  <Button size="sm" onclick={() => (showCreate = !showCreate)}>
    <PlusIcon class="size-4" />
    New event
  </Button>
</div>

{#if showCreate}
  <form
    method="POST"
    action="?/create"
    use:enhance
    class="mb-6 grid gap-4 rounded-xl border border-border/60 p-4 sm:grid-cols-2"
  >
    <div class="grid gap-2">
      <Label for="name">Event name</Label>
      <Input id="name" name="name" required placeholder="Book a Tour" />
    </div>
    <div class="grid gap-2">
      <Label for="branch_id">Branch</Label>
      <select
        id="branch_id"
        name="branch_id"
        class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
      >
        <option value="">All branches</option>
        {#each branches as branch (branch.id)}
          <option value={branch.id} selected={String(branch.id) === data.branchId}>
            {branch.name}
          </option>
        {/each}
      </select>
    </div>
    <div class="grid gap-2">
      <Label for="venue">Location</Label>
      <Input id="venue" name="venue" />
    </div>
    <div class="grid gap-2">
      <Label for="capacity">Capacity</Label>
      <Input id="capacity" name="capacity" type="number" min="1" />
    </div>
    <div class="grid gap-2">
      <Label for="registration_opens_at">Registration opens</Label>
      <DateTimeField name="registration_opens_at" bind:value={opensAt} />
    </div>
    <div class="grid gap-2">
      <Label for="registration_closes_at">Registration closes</Label>
      <DateTimeField name="registration_closes_at" bind:value={closesAt} />
    </div>
    <div class="sm:col-span-2"><Button type="submit">Create event</Button></div>
  </form>
{/if}

<Table.Root>
  <Table.Header>
    <Table.Row>
      <Table.Head>Event</Table.Head>
      <Table.Head>Branch</Table.Head>
      <Table.Head>Registration</Table.Head>
      <Table.Head class="text-right">Registrations</Table.Head>
      <Table.Head class="text-right">Guests</Table.Head>
      <Table.Head>Status</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {#each events as event (event.id)}
      <Table.Row>
        <Table.Cell>
          <a class="font-medium hover:underline" href={`/events/${event.id}`}>{event.name}</a>
        </Table.Cell>
        <Table.Cell>{event.branch_name ?? 'All branches'}</Table.Cell>
        <Table.Cell class="text-sm text-muted-foreground">
          {formatDateRange(event.registration_opens_at, event.registration_closes_at, 'No limit')}
        </Table.Cell>
        <Table.Cell class="text-right">{event.registration_count}</Table.Cell>
        <Table.Cell class="text-right">
          {event.head_count}{event.capacity ? ` / ${event.capacity}` : ''}
        </Table.Cell>
        <Table.Cell>{event.is_active ? 'Active' : 'Inactive'}</Table.Cell>
      </Table.Row>
    {:else}
      <Table.Row>
        <Table.Cell colspan={6} class="text-center text-sm text-muted-foreground">
          No events match this filter.
        </Table.Cell>
      </Table.Row>
    {/each}
  </Table.Body>
</Table.Root>
