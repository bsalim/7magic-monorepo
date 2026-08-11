<script lang="ts">
  import { enhance } from '$app/forms';
  import PlusIcon from '@lucide/svelte/icons/plus';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import type { AdminBranch } from '$lib/api';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Table from '$lib/components/ui/table';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  let showCreate = $state(false);
  const branches = $derived(data.branches as AdminBranch[]);
</script>

<PageHeader title="Cabang" description="Lokasi 7Magic yang menerima kunjungan dan acara." />

{#if data.error}
  <p class="mb-4 flex items-center gap-2 text-sm text-destructive">
    <TriangleAlertIcon class="size-4" />
    {data.error}
  </p>
{/if}

{#if form?.message}
  <p class="mb-4 text-sm" class:text-destructive={form.ok === false}>{form.message}</p>
{/if}

<div class="mb-4 flex justify-end">
  <Button size="sm" onclick={() => (showCreate = !showCreate)}>
    <PlusIcon class="size-4" />
    Cabang baru
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
      <Label for="name">Nama</Label>
      <Input id="name" name="name" required placeholder="7Magic Bali" />
    </div>
    <div class="grid gap-2">
      <Label for="slug">Slug</Label>
      <Input id="slug" name="slug" required placeholder="bali" />
    </div>
    <div class="grid gap-2">
      <Label for="city">Kota</Label>
      <Input id="city" name="city" value="jakarta" />
    </div>
    <div class="grid gap-2">
      <Label for="addressLine1">Alamat</Label>
      <Input id="addressLine1" name="addressLine1" />
    </div>
    <div class="grid gap-2">
      <Label for="timezone">Zona waktu</Label>
      <Input id="timezone" name="timezone" value="Asia/Jakarta" />
    </div>
    <div class="flex items-end">
      <Button type="submit">Simpan</Button>
    </div>
  </form>
{/if}

<Table.Root>
  <Table.Header>
    <Table.Row>
      <Table.Head>Cabang</Table.Head>
      <Table.Head>Kota</Table.Head>
      <Table.Head>Slug</Table.Head>
      <Table.Head>Status</Table.Head>
      <Table.Head class="text-right">Aksi</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {#each branches as branch (branch.id)}
      <Table.Row>
        <Table.Cell>
          <a class="font-medium hover:underline" href={`/branches/${branch.id}`}>{branch.name}</a>
          {#if branch.isDefault}
            <span class="ml-2 rounded bg-muted px-1.5 py-0.5 text-xs">Default</span>
          {/if}
        </Table.Cell>
        <Table.Cell>{branch.city}</Table.Cell>
        <Table.Cell class="font-mono text-xs">{branch.slug}</Table.Cell>
        <Table.Cell>
          {branch.active ? 'Aktif' : 'Nonaktif'}{branch.bookable ? '' : ' · tutup kunjungan'}
        </Table.Cell>
        <Table.Cell class="text-right">
          <form method="POST" action="?/delete" use:enhance class="inline">
            <input type="hidden" name="id" value={branch.id} />
            <Button type="submit" variant="ghost" size="sm">Hapus</Button>
          </form>
        </Table.Cell>
      </Table.Row>
    {:else}
      <Table.Row>
        <Table.Cell colspan={5} class="text-center text-sm text-muted-foreground">
          Belum ada cabang.
        </Table.Cell>
      </Table.Row>
    {/each}
  </Table.Body>
</Table.Root>
