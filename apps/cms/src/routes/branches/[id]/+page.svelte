<script lang="ts">
  import { enhance } from '$app/forms';

  import type { AdminBranch } from '$lib/api';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Table from '$lib/components/ui/table';
  import { Textarea } from '$lib/components/ui/textarea';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const branch = $derived(data.branch as AdminBranch);

  const DAYS = [
    { iso: 1, label: 'Senin' },
    { iso: 2, label: 'Selasa' },
    { iso: 3, label: 'Rabu' },
    { iso: 4, label: 'Kamis' },
    { iso: 5, label: 'Jumat' },
    { iso: 6, label: 'Sabtu' },
    { iso: 7, label: 'Minggu' }
  ];

  // "10:00:00" -> "10:00" for <input type="time">
  const toTimeInput = (value: string | undefined) => (value ? value.slice(0, 5) : '');
  const hourFor = (iso: number) => branch.openingHours.find((row) => row.dayOfWeek === iso);

  let tab = $state<'details' | 'settings' | 'hours' | 'closures'>('details');
  const tabs = [
    { key: 'details', label: 'Detail' },
    { key: 'settings', label: 'Pengaturan' },
    { key: 'hours', label: 'Jam buka' },
    { key: 'closures', label: 'Tanggal tutup' }
  ] as const;
</script>

<PageHeader
  title={branch.name}
  description={`/tour/${branch.slug}`}
  backHref="/branches"
  backLabel="Cabang"
/>

{#if form?.message}
  <p class="mb-4 text-sm" class:text-destructive={form.ok === false}>{form.message}</p>
{/if}

<div class="mb-6 flex gap-2 border-b border-border/60">
  {#each tabs as item (item.key)}
    <button
      type="button"
      class="border-b-2 px-3 py-2 text-sm"
      class:border-primary={tab === item.key}
      class:border-transparent={tab !== item.key}
      onclick={() => (tab = item.key)}
    >
      {item.label}
    </button>
  {/each}
</div>

{#if tab === 'details'}
  <form method="POST" action="?/details" use:enhance class="grid gap-4 sm:grid-cols-2">
    <div class="grid gap-2">
      <Label for="name">Nama</Label>
      <Input id="name" name="name" value={branch.name} required />
    </div>
    <div class="grid gap-2">
      <Label for="slug">Slug</Label>
      <Input id="slug" name="slug" value={branch.slug} required />
    </div>
    <div class="grid gap-2">
      <Label for="addressLine1">Alamat</Label>
      <Input id="addressLine1" name="addressLine1" value={branch.addressLine1} />
    </div>
    <div class="grid gap-2">
      <Label for="addressLine2">Alamat (baris 2)</Label>
      <Input id="addressLine2" name="addressLine2" value={branch.addressLine2 ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="city">Kota</Label>
      <Input id="city" name="city" value={branch.city} />
    </div>
    <div class="grid gap-2">
      <Label for="postalCode">Kode pos</Label>
      <Input id="postalCode" name="postalCode" value={branch.postalCode ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="timezone">Zona waktu</Label>
      <Input id="timezone" name="timezone" value={branch.timezone} />
    </div>
    <div class="grid gap-2">
      <Label for="publicPhone">Telepon</Label>
      <Input id="publicPhone" name="publicPhone" value={branch.publicPhone ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="publicEmail">Email</Label>
      <Input id="publicEmail" name="publicEmail" value={branch.publicEmail ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="whatsappNumber">WhatsApp</Label>
      <Input id="whatsappNumber" name="whatsappNumber" value={branch.whatsappNumber ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="websiteUrl">Website khusus cabang</Label>
      <Input id="websiteUrl" name="websiteUrl" value={branch.websiteUrl ?? ''} />
    </div>
    <div class="flex flex-col gap-2 pt-6 text-sm">
      <label><input type="checkbox" name="active" checked={branch.active} /> Aktif</label>
      <label>
        <input type="checkbox" name="bookable" checked={branch.bookable} /> Terima kunjungan
      </label>
      <label>
        <input type="checkbox" name="isDefault" checked={branch.isDefault} /> Cabang default
      </label>
    </div>
    <div class="sm:col-span-2">
      <Button type="submit">Simpan detail</Button>
    </div>
  </form>
{/if}

{#if tab === 'settings'}
  <form method="POST" action="?/settings" use:enhance class="grid max-w-2xl gap-4">
    <div class="grid gap-2">
      <Label for="senderDisplayName">Nama pengirim email</Label>
      <Input
        id="senderDisplayName"
        name="senderDisplayName"
        value={branch.settings?.senderDisplayName ?? ''}
      />
    </div>
    <div class="grid gap-2">
      <Label for="replyToEmail">Balas ke</Label>
      <Input id="replyToEmail" name="replyToEmail" value={branch.settings?.replyToEmail ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="tourNotificationRecipients">Notifikasi pendaftaran (satu email per baris)</Label>
      <Textarea
        id="tourNotificationRecipients"
        name="tourNotificationRecipients"
        rows={4}
        value={(branch.settings?.tourNotificationRecipients ?? []).join('\n')}
      />
    </div>
    <div class="grid gap-2">
      <Label for="tourIntroHtml">Pengantar halaman kunjungan</Label>
      <Textarea
        id="tourIntroHtml"
        name="tourIntroHtml"
        rows={4}
        value={branch.settings?.tourIntroHtml ?? ''}
      />
    </div>
    <div class="grid gap-2">
      <Label for="arrivalInstructions">Petunjuk kedatangan</Label>
      <Textarea
        id="arrivalInstructions"
        name="arrivalInstructions"
        rows={3}
        value={branch.settings?.arrivalInstructions ?? ''}
      />
    </div>
    <div class="grid gap-2">
      <Label for="parkingNotes">Catatan parkir</Label>
      <Textarea
        id="parkingNotes"
        name="parkingNotes"
        rows={3}
        value={branch.settings?.parkingNotes ?? ''}
      />
    </div>
    <div><Button type="submit">Simpan pengaturan</Button></div>
  </form>
{/if}

{#if tab === 'hours'}
  <form method="POST" action="?/hours" use:enhance class="grid max-w-xl gap-3">
    {#each DAYS as day (day.iso)}
      {@const hour = hourFor(day.iso)}
      <div class="flex items-center gap-3">
        <label class="w-32 text-sm">
          <input type="checkbox" name={`day-${day.iso}-active`} checked={Boolean(hour)} />
          {day.label}
        </label>
        <Input
          type="time"
          name={`day-${day.iso}-opens`}
          value={toTimeInput(hour?.opensAtLocal) || '10:00'}
          class="w-32"
        />
        <span class="text-sm text-muted-foreground">sampai</span>
        <Input
          type="time"
          name={`day-${day.iso}-closes`}
          value={toTimeInput(hour?.closesAtLocal) || '18:00'}
          class="w-32"
        />
      </div>
    {/each}
    <div><Button type="submit">Simpan jam buka</Button></div>
  </form>
{/if}

{#if tab === 'closures'}
  <form
    method="POST"
    action="?/addClosure"
    use:enhance
    class="mb-6 grid max-w-xl gap-3 sm:grid-cols-2"
  >
    <div class="grid gap-2">
      <Label for="startDate">Mulai</Label>
      <Input id="startDate" name="startDate" type="date" required />
    </div>
    <div class="grid gap-2">
      <Label for="endDate">Sampai</Label>
      <Input id="endDate" name="endDate" type="date" />
    </div>
    <div class="grid gap-2">
      <Label for="publicLabel">Label publik</Label>
      <Input id="publicLabel" name="publicLabel" placeholder="Libur Lebaran" />
    </div>
    <div class="grid gap-2">
      <Label for="reason">Catatan internal</Label>
      <Input id="reason" name="reason" />
    </div>
    <div class="sm:col-span-2"><Button type="submit">Tambah tanggal tutup</Button></div>
  </form>

  <Table.Root>
    <Table.Header>
      <Table.Row>
        <Table.Head>Mulai</Table.Head>
        <Table.Head>Sampai</Table.Head>
        <Table.Head>Label publik</Table.Head>
        <Table.Head class="text-right">Aksi</Table.Head>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {#each branch.closures as closure (closure.id)}
        <Table.Row>
          <Table.Cell>{closure.startsAtLocal.slice(0, 10)}</Table.Cell>
          <Table.Cell>{closure.endsAtLocal.slice(0, 10)}</Table.Cell>
          <Table.Cell>{closure.publicLabel ?? '—'}</Table.Cell>
          <Table.Cell class="text-right">
            <form method="POST" action="?/deleteClosure" use:enhance class="inline">
              <input type="hidden" name="closureId" value={closure.id} />
              <Button type="submit" variant="ghost" size="sm">Hapus</Button>
            </form>
          </Table.Cell>
        </Table.Row>
      {:else}
        <Table.Row>
          <Table.Cell colspan={4} class="text-center text-sm text-muted-foreground">
            Belum ada tanggal tutup.
          </Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>
{/if}
