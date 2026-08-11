<script lang="ts">
  import { enhance } from '$app/forms';
  import { goto } from '$app/navigation';
  import DownloadIcon from '@lucide/svelte/icons/download';

  import type { AdminBranch, AdminEmailTemplate, AdminEvent, AdminRegistration } from '$lib/api';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Table from '$lib/components/ui/table';
  import { Textarea } from '$lib/components/ui/textarea';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const event = $derived(data.event as AdminEvent);
  const registrations = $derived(data.registrations as AdminRegistration[]);
  const templates = $derived(data.templates as AdminEmailTemplate[]);
  const branches = $derived(data.branches as AdminBranch[]);

  let tab = $state<'details' | 'registrations' | 'emails'>('registrations');
  const tabs = [
    { key: 'registrations', label: 'Pendaftar' },
    { key: 'details', label: 'Detail acara' },
    { key: 'emails', label: 'Email' }
  ] as const;

  const STATUS_LABELS: Record<AdminRegistration['status'], string> = {
    registered: 'Terdaftar',
    attended: 'Hadir',
    no_show: 'Tidak hadir',
    cancelled: 'Batal'
  };

  const TEMPLATE_LABELS: Record<AdminEmailTemplate['kind'], string> = {
    thank_you: 'Terima kasih',
    no_show: 'Tidak hadir',
    cancel: 'Pembatalan'
  };

  // datetime-local wants "YYYY-MM-DDTHH:mm"; the API returns full ISO strings.
  const toLocalInput = (value: string | null) => (value ? value.slice(0, 16) : '');

  function applyStatusFilter(target: Event) {
    const value = (target.currentTarget as HTMLSelectElement).value;
    const params = new URLSearchParams(window.location.search);
    if (value) params.set('status', value);
    else params.delete('status');
    goto(`?${params.toString()}`, { keepFocus: true, noScroll: true });
  }
</script>

<PageHeader
  title={event.name}
  description={event.branchName ?? 'Semua cabang'}
  backHref="/events"
  backLabel="Acara"
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

{#if tab === 'registrations'}
  <div class="mb-4 flex items-end justify-between gap-4">
    <div class="grid gap-2">
      <Label for="statusFilter">Status</Label>
      <select
        id="statusFilter"
        class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
        value={data.statusFilter}
        onchange={applyStatusFilter}
      >
        <option value="">Semua</option>
        <option value="registered">Terdaftar</option>
        <option value="attended">Hadir</option>
        <option value="no_show">Tidak hadir</option>
        <option value="cancelled">Batal</option>
      </select>
    </div>

    <!-- Proxied through the CMS: the session token lives in a server-side cookie,
         so a link straight at the API origin would download a 401. -->
    <Button variant="outline" size="sm" href={`/events/${event.id}/export`} data-sveltekit-reload>
      <DownloadIcon class="size-4" />
      Ekspor CSV
    </Button>
  </div>

  <form
    method="POST"
    action="?/addRegistration"
    use:enhance
    class="mb-6 grid gap-4 rounded-xl border border-border/60 p-4 sm:grid-cols-3"
  >
    <div class="grid gap-2">
      <Label for="name">Nama tamu</Label>
      <Input id="name" name="name" required />
    </div>
    <div class="grid gap-2">
      <Label for="email">Email</Label>
      <Input id="email" name="email" type="email" required />
    </div>
    <div class="grid gap-2">
      <Label for="mobile">HP</Label>
      <Input id="mobile" name="mobile" />
    </div>
    <div class="grid gap-2">
      <Label for="visitDate">Tanggal kunjungan</Label>
      <Input id="visitDate" name="visitDate" type="date" />
    </div>
    <div class="grid gap-2">
      <Label for="visitSlot">Jam</Label>
      <Input id="visitSlot" name="visitSlot" placeholder="10:00" />
    </div>
    <div class="flex items-end"><Button type="submit">Tambah pendaftar</Button></div>
  </form>

  <Table.Root>
    <Table.Header>
      <Table.Row>
        <Table.Head>Tamu</Table.Head>
        <Table.Head>Cabang</Table.Head>
        <Table.Head>Kunjungan</Table.Head>
        <Table.Head class="text-right">Tamu</Table.Head>
        <Table.Head>Status</Table.Head>
        <Table.Head>Sumber</Table.Head>
        <Table.Head class="text-right">Aksi</Table.Head>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {#each registrations as registration (registration.id)}
        <Table.Row>
          <Table.Cell>
            <div class="font-medium">{registration.guestName}</div>
            <div class="text-xs text-muted-foreground">{registration.email}</div>
          </Table.Cell>
          <Table.Cell>{registration.branchName ?? '—'}</Table.Cell>
          <Table.Cell class="text-sm">
            {registration.visitDate ?? '—'}{registration.visitSlot
              ? ` · ${registration.visitSlot}`
              : ''}
          </Table.Cell>
          <Table.Cell class="text-right">{registration.partySize}</Table.Cell>
          <Table.Cell>{STATUS_LABELS[registration.status]}</Table.Cell>
          <Table.Cell class="text-xs text-muted-foreground">{registration.source}</Table.Cell>
          <Table.Cell class="text-right">
            <form method="POST" action="?/updateRegistration" use:enhance class="inline">
              <input type="hidden" name="registrationId" value={registration.id} />
              <input type="hidden" name="status" value="attended" />
              <Button type="submit" variant="ghost" size="sm">Hadir</Button>
            </form>
            <form method="POST" action="?/updateRegistration" use:enhance class="inline">
              <input type="hidden" name="registrationId" value={registration.id} />
              <input type="hidden" name="status" value="no_show" />
              <Button type="submit" variant="ghost" size="sm">Tidak hadir</Button>
            </form>
            <form method="POST" action="?/updateRegistration" use:enhance class="inline">
              <input type="hidden" name="registrationId" value={registration.id} />
              <input type="hidden" name="followUp" value={String(!registration.followUp)} />
              <Button type="submit" variant="ghost" size="sm">
                {registration.followUp ? 'Batal tindak lanjut' : 'Tindak lanjut'}
              </Button>
            </form>
          </Table.Cell>
        </Table.Row>
      {:else}
        <Table.Row>
          <Table.Cell colspan={7} class="text-center text-sm text-muted-foreground">
            Belum ada pendaftar.
          </Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>
{/if}

{#if tab === 'details'}
  <form method="POST" action="?/details" use:enhance class="grid max-w-3xl gap-4 sm:grid-cols-2">
    <div class="grid gap-2">
      <Label for="name">Nama acara</Label>
      <Input id="name" name="name" value={event.name} required />
    </div>
    <div class="grid gap-2">
      <Label for="branchId">Cabang</Label>
      <select
        id="branchId"
        name="branchId"
        class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
      >
        <option value="" selected={event.branchId === null}>Semua cabang</option>
        {#each branches as branch (branch.id)}
          <option value={branch.id} selected={branch.id === event.branchId}>{branch.name}</option>
        {/each}
      </select>
    </div>
    <div class="grid gap-2 sm:col-span-2">
      <Label for="descriptionHtml">Deskripsi</Label>
      <Textarea
        id="descriptionHtml"
        name="descriptionHtml"
        rows={6}
        value={event.descriptionHtml}
      />
      <p class="text-xs text-muted-foreground">
        Tag yang diizinkan: p, br, strong, em, ul, ol, li, h2, h3, h4, a. Sisanya dibuang saat
        disimpan.
      </p>
    </div>
    <div class="grid gap-2">
      <Label for="venue">Lokasi</Label>
      <Input id="venue" name="venue" value={event.venue ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="capacity">Kapasitas</Label>
      <Input id="capacity" name="capacity" type="number" min="1" value={event.capacity ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="registrationOpensAt">Pendaftaran dibuka</Label>
      <Input
        id="registrationOpensAt"
        name="registrationOpensAt"
        type="datetime-local"
        value={toLocalInput(event.registrationOpensAt)}
      />
    </div>
    <div class="grid gap-2">
      <Label for="registrationClosesAt">Pendaftaran ditutup</Label>
      <Input
        id="registrationClosesAt"
        name="registrationClosesAt"
        type="datetime-local"
        value={toLocalInput(event.registrationClosesAt)}
      />
    </div>
    <div class="grid gap-2">
      <Label for="eventStartAt">Acara mulai</Label>
      <Input
        id="eventStartAt"
        name="eventStartAt"
        type="datetime-local"
        value={toLocalInput(event.eventStartAt)}
      />
    </div>
    <div class="grid gap-2">
      <Label for="eventEndAt">Acara selesai</Label>
      <Input
        id="eventEndAt"
        name="eventEndAt"
        type="datetime-local"
        value={toLocalInput(event.eventEndAt)}
      />
    </div>
    <label class="flex items-center gap-2 text-sm">
      <input type="checkbox" name="isActive" checked={event.isActive} /> Aktif
    </label>
    <div class="sm:col-span-2"><Button type="submit">Simpan acara</Button></div>
  </form>
{/if}

{#if tab === 'emails'}
  <p class="mb-4 text-sm text-muted-foreground">
    Placeholder: {data.placeholders.map((token) => `{${token}}`).join(', ')}
  </p>

  <div class="grid gap-6">
    {#each templates as template (template.kind)}
      <form
        method="POST"
        action="?/saveTemplate"
        use:enhance
        class="grid gap-3 rounded-xl border border-border/60 p-4"
      >
        <input type="hidden" name="kind" value={template.kind} />
        <h3 class="font-medium">{TEMPLATE_LABELS[template.kind]}</h3>
        <div class="grid gap-2">
          <Label for={`subject-${template.kind}`}>Subjek</Label>
          <Input id={`subject-${template.kind}`} name="subject" value={template.subject} />
        </div>
        <div class="grid gap-2">
          <Label for={`body-${template.kind}`}>Isi</Label>
          <Textarea id={`body-${template.kind}`} name="body" rows={8} value={template.body} />
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" name="enabled" checked={template.enabled} /> Aktifkan
        </label>
        <div><Button type="submit" size="sm">Simpan template</Button></div>
      </form>
    {/each}
  </div>
{/if}
