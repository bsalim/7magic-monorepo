<script lang="ts">
  import { enhance } from '$app/forms';
  import { goto } from '$app/navigation';
  import PlusIcon from '@lucide/svelte/icons/plus';

  import type { AdminBranch, AdminEvent } from '$lib/api';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Table from '$lib/components/ui/table';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const events = $derived(data.events as AdminEvent[]);
  const branches = $derived(data.branches as AdminBranch[]);

  let showCreate = $state(false);

  // Branch is a filter, not a mode: the selection lives in the URL so a filtered
  // list can be linked and reloaded.
  function onFilterChange(event: Event) {
    const value = (event.currentTarget as HTMLSelectElement).value;
    goto(value ? `/events?branchId=${value}` : '/events', { keepFocus: true });
  }

  const formatWindow = (event: AdminEvent) =>
    event.registrationOpensAt && event.registrationClosesAt
      ? `${event.registrationOpensAt.slice(0, 10)} → ${event.registrationClosesAt.slice(0, 10)}`
      : 'Tanpa batas';
</script>

<PageHeader title="Acara" description="Book a Tour dan acara lain per cabang." />

{#if data.error}<p class="mb-4 text-sm text-destructive">{data.error}</p>{/if}
{#if form?.message}<p class="mb-4 text-sm text-destructive">{form.message}</p>{/if}

<div class="mb-4 flex items-end justify-between gap-4">
  <div class="grid gap-2">
    <Label for="branchFilter">Cabang</Label>
    <select
      id="branchFilter"
      class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
      value={data.branchId}
      onchange={onFilterChange}
    >
      <option value="">Semua cabang</option>
      {#each branches as branch (branch.id)}
        <!-- String, not number: branchId comes off the URL as a string, and a
             numeric option value never matches it, leaving the filter blank. -->
        <option value={String(branch.id)}>{branch.name}</option>
      {/each}
    </select>
  </div>

  <Button size="sm" onclick={() => (showCreate = !showCreate)}>
    <PlusIcon class="size-4" />
    Acara baru
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
      <Label for="name">Nama acara</Label>
      <Input id="name" name="name" required placeholder="Book a Tour" />
    </div>
    <div class="grid gap-2">
      <Label for="branchId">Cabang</Label>
      <select
        id="branchId"
        name="branchId"
        class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
      >
        <option value="">Semua cabang</option>
        {#each branches as branch (branch.id)}
          <option value={branch.id} selected={String(branch.id) === data.branchId}>
            {branch.name}
          </option>
        {/each}
      </select>
    </div>
    <div class="grid gap-2">
      <Label for="venue">Lokasi</Label>
      <Input id="venue" name="venue" />
    </div>
    <div class="grid gap-2">
      <Label for="capacity">Kapasitas</Label>
      <Input id="capacity" name="capacity" type="number" min="1" />
    </div>
    <div class="grid gap-2">
      <Label for="registrationOpensAt">Pendaftaran dibuka</Label>
      <Input id="registrationOpensAt" name="registrationOpensAt" type="datetime-local" />
    </div>
    <div class="grid gap-2">
      <Label for="registrationClosesAt">Pendaftaran ditutup</Label>
      <Input id="registrationClosesAt" name="registrationClosesAt" type="datetime-local" />
    </div>
    <div class="sm:col-span-2"><Button type="submit">Buat acara</Button></div>
  </form>
{/if}

<Table.Root>
  <Table.Header>
    <Table.Row>
      <Table.Head>Acara</Table.Head>
      <Table.Head>Cabang</Table.Head>
      <Table.Head>Pendaftaran</Table.Head>
      <Table.Head class="text-right">Pendaftar</Table.Head>
      <Table.Head class="text-right">Tamu</Table.Head>
      <Table.Head>Status</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {#each events as event (event.id)}
      <Table.Row>
        <Table.Cell>
          <a class="font-medium hover:underline" href={`/events/${event.id}`}>{event.name}</a>
        </Table.Cell>
        <Table.Cell>{event.branchName ?? 'Semua cabang'}</Table.Cell>
        <Table.Cell class="text-sm text-muted-foreground">{formatWindow(event)}</Table.Cell>
        <Table.Cell class="text-right">{event.registrationCount}</Table.Cell>
        <Table.Cell class="text-right">
          {event.headCount}{event.capacity ? ` / ${event.capacity}` : ''}
        </Table.Cell>
        <Table.Cell>{event.isActive ? 'Aktif' : 'Nonaktif'}</Table.Cell>
      </Table.Row>
    {:else}
      <Table.Row>
        <Table.Cell colspan={6} class="text-center text-sm text-muted-foreground">
          Belum ada acara untuk filter ini.
        </Table.Cell>
      </Table.Row>
    {/each}
  </Table.Body>
</Table.Root>
