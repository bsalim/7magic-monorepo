# Branches, Events and Book a Tour — UI Implementation Plan (Plan 2 of 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the CMS branch and event screens where branch is a **column and a filter** on every list, and give the public site a per-branch Book a Tour page that only offers dates the branch is actually open.

**Architecture:** CMS routes follow the existing `+page.server.ts` (load + form actions, server-side token) / `+page.svelte` (shadcn-svelte, TanStack table) split. The public pages use the same shadcn primitives the contact page uses, with copy in Paraglide messages — `/en/tour` resolves to the same route through the existing `deLocalizeUrl` reroute, so no duplicate route folder is needed.

**Tech Stack:** SvelteKit 2, Svelte 5 runes, Tailwind v4, shadcn-svelte, `@tanstack/table-core`, `@lucide/svelte`, Paraglide, Vitest.

**Spec:** `docs/superpowers/specs/2026-08-11-branches-events-tour-design.md`
**Depends on:** `docs/superpowers/plans/2026-08-11-branches-events-api.md` — every endpoint below ships in Plan 1. Do not start this plan until Plan 1's suite is green.

---

## Endpoints this plan consumes

| Method | Path | Used by |
|---|---|---|
| GET/POST | `/api/v1/admin/branches` | branches list |
| GET/PATCH/DELETE | `/api/v1/admin/branches/{id}` | branch detail |
| PUT | `/api/v1/admin/branches/{id}/settings` | branch detail, settings tab |
| PUT | `/api/v1/admin/branches/{id}/opening-hours` | branch detail, hours tab |
| POST/DELETE | `/api/v1/admin/branches/{id}/closures[/{closureId}]` | branch detail, closures tab |
| GET/POST | `/api/v1/admin/events?branchId=` | events list |
| GET/PATCH/DELETE | `/api/v1/admin/events/{id}` | event detail |
| GET/POST | `/api/v1/admin/event-registrations` | registrations table |
| PATCH | `/api/v1/admin/event-registrations/{id}` | attendance, follow-up, notes |
| GET | `/api/v1/admin/event-registrations/export` | CSV button |
| GET/PUT/POST | `/api/v1/admin/events/{id}/email-templates[/{kind}[/preview]]` | templates tab |
| GET | `/api/v1/public/tour/branches` | `/tour` |
| GET | `/api/v1/public/tour/branches/{slug}` | `/tour/[slug]` |
| POST | `/api/v1/public/tour/branches/{slug}/register` | tour form action |

Every response is `{ "data": ... }` or `{ "items": [...] }`, and every error is `{ "error": { code, message, details } }` — the shape `apiFetch` in `apps/cms/src/lib/server/api.ts` already unwraps into `ApiRequestError`.

---

### Task 1: CMS API types

**Files:**
- Modify: `apps/cms/src/lib/api.ts`

- [ ] **Step 1: Add the types**

Append to `apps/cms/src/lib/api.ts`. Field names are camelCase because the new endpoints serialise with a camel alias generator (the older venue/article types are snake_case; do not "fix" them to match).

```ts
export type AdminBranchSettings = {
  senderDisplayName: string | null;
  replyToEmail: string | null;
  tourNotificationRecipients: string[];
  tourIntroHtml: string | null;
  arrivalInstructions: string | null;
  parkingNotes: string | null;
};

export type AdminOpeningHour = {
  id?: number;
  dayOfWeek: number; // ISO: Monday = 1 ... Sunday = 7
  opensAtLocal: string; // "10:00:00"
  closesAtLocal: string;
  active: boolean;
  sortOrder: number;
};

export type AdminClosure = {
  id: number;
  startsAtLocal: string;
  endsAtLocal: string;
  fullDay: boolean;
  reason: string | null;
  publicLabel: string | null;
  active: boolean;
};

export type AdminBranch = {
  id: number;
  publicId: string;
  slug: string;
  name: string;
  addressLine1: string;
  addressLine2: string | null;
  city: string;
  countryCode: string;
  postalCode: string | null;
  timezone: string;
  publicPhone: string | null;
  publicEmail: string | null;
  whatsappNumber: string | null;
  instagramUrl: string | null;
  facebookUrl: string | null;
  websiteUrl: string | null;
  active: boolean;
  bookable: boolean;
  isDefault: boolean;
  settings: AdminBranchSettings | null;
  openingHours: AdminOpeningHour[];
  closures: AdminClosure[];
};

export type AdminEvent = {
  id: number;
  publicId: string;
  branchId: number | null;
  branchName: string | null;
  name: string;
  descriptionHtml: string;
  venue: string | null;
  eventStartAt: string | null;
  eventEndAt: string | null;
  registrationOpensAt: string | null;
  registrationClosesAt: string | null;
  capacity: number | null;
  coverImageUrl: string | null;
  color: string | null;
  isActive: boolean;
  registrationCount: number;
  headCount: number;
};

export type AdminRegistration = {
  id: number;
  publicId: string;
  eventId: number;
  eventName: string | null;
  branchId: number | null;
  branchName: string | null;
  guestName: string;
  email: string;
  mobile: string | null;
  partySize: number;
  visitDate: string | null;
  visitSlot: string | null;
  status: 'registered' | 'attended' | 'no_show' | 'cancelled';
  followUp: boolean;
  notes: string | null;
  source: string;
  attendedAt: string | null;
  guests: Array<{ name: string; email: string | null; mobile: string | null }>;
  createdAt: string | null;
};

export type AdminEmailTemplate = {
  kind: 'thank_you' | 'no_show' | 'cancel';
  subject: string;
  body: string;
  enabled: boolean;
};
```

- [ ] **Step 2: Verify**

Run: `cd apps/cms && pnpm run check`
Expected: `0 errors`.

- [ ] **Step 3: Commit**

```bash
git add apps/cms/src/lib/api.ts
git commit -m "feat(cms): type the branch, event and registration payloads"
```

---

### Task 2: Branches list

**Files:**
- Create: `apps/cms/src/routes/branches/+page.server.ts`
- Create: `apps/cms/src/routes/branches/+page.svelte`
- Modify: `apps/cms/src/lib/components/AdminShell.svelte:25-30`

- [ ] **Step 1: Write the loader and actions**

Create `apps/cms/src/routes/branches/+page.server.ts`:

```ts
import { fail, redirect } from '@sveltejs/kit';

import type { AdminBranch } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const data = await apiFetch<{ items: AdminBranch[] }>('/api/v1/admin/branches', {
      token: locals.token
    });
    return { error: '', branches: data.items };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError
          ? error.message
          : 'Tidak bisa memuat cabang. Periksa server API lalu coba lagi.',
      branches: [] as AdminBranch[]
    };
  }
};

export const actions: Actions = {
  create: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const payload = {
      slug: String(form.get('slug') ?? '').trim(),
      name: String(form.get('name') ?? '').trim(),
      city: String(form.get('city') ?? 'jakarta').trim(),
      addressLine1: String(form.get('addressLine1') ?? '').trim(),
      timezone: String(form.get('timezone') ?? 'Asia/Jakarta').trim(),
      countryCode: 'ID'
    };

    if (!payload.slug || !payload.name) {
      return fail(400, { ok: false, message: 'Slug dan nama cabang wajib diisi.' });
    }

    try {
      await apiFetch('/api/v1/admin/branches', {
        method: 'POST',
        token: locals.token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (error) {
      return fail(400, {
        ok: false,
        message:
          error instanceof ApiRequestError && error.code === 'branch_slug_conflict'
            ? 'Slug cabang sudah dipakai.'
            : 'Cabang gagal dibuat.'
      });
    }

    return { ok: true, message: 'Cabang dibuat.' };
  },

  delete: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const id = String(form.get('id') ?? '').trim();
    if (!id) {
      return fail(400, { ok: false, message: 'Id cabang tidak ada.' });
    }

    try {
      await apiFetch(`/api/v1/admin/branches/${id}`, { method: 'DELETE', token: locals.token });
    } catch (error) {
      return fail(400, {
        ok: false,
        message: error instanceof ApiRequestError ? error.message : 'Cabang gagal dihapus.'
      });
    }

    return { ok: true, message: 'Cabang dihapus.' };
  }
};
```

- [ ] **Step 2: Write the page**

Create `apps/cms/src/routes/branches/+page.svelte`:

```svelte
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
```

- [ ] **Step 3: Add the nav entries**

In `apps/cms/src/lib/components/AdminShell.svelte`, import two icons alongside the existing ones:

```ts
  import BuildingIcon from '@lucide/svelte/icons/building-2';
  import CalendarIcon from '@lucide/svelte/icons/calendar-days';
```

and extend the `nav` array (currently at line 25) so the two new items sit after Dashboard:

```ts
  const nav: NavItem[] = [
    { label: 'Dashboard', href: '/', icon: LayoutDashboardIcon },
    { label: 'Branches', href: '/branches', icon: BuildingIcon },
    { label: 'Events', href: '/events', icon: CalendarIcon },
    { label: 'Venues', href: '/venues', icon: MapPinIcon },
    { label: 'Articles', href: '/articles', icon: NewspaperIcon },
    { label: 'Wedding Showcases', href: '/showcases', icon: ImagesIcon },
    { label: 'Promotion Pop up', href: '/promotions', icon: MegaphoneIcon }
  ];
```

- [ ] **Step 4: Verify**

Run: `cd apps/cms && pnpm run check`
Expected: `0 errors, 0 warnings`.

- [ ] **Step 5: Commit**

```bash
git add apps/cms/src/routes/branches apps/cms/src/lib/components/AdminShell.svelte
git commit -m "feat(cms): list and create branches"
```

---

### Task 3: Branch detail — settings, opening hours, closures

**Files:**
- Create: `apps/cms/src/routes/branches/[id]/+page.server.ts`
- Create: `apps/cms/src/routes/branches/[id]/+page.svelte`

- [ ] **Step 1: Write the loader and actions**

Create `apps/cms/src/routes/branches/[id]/+page.server.ts`:

```ts
import { error, fail, redirect } from '@sveltejs/kit';

import type { AdminBranch } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const data = await apiFetch<{ data: AdminBranch }>(`/api/v1/admin/branches/${params.id}`, {
      token: locals.token
    });
    return { branch: data.data };
  } catch (cause) {
    if (cause instanceof ApiRequestError && cause.status === 404) {
      throw error(404, 'Cabang tidak ditemukan.');
    }
    throw cause;
  }
};

const requireToken = (locals: App.Locals) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }
  return locals.token;
};

export const actions: Actions = {
  details: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}`, {
        method: 'PATCH',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          name: String(form.get('name') ?? '').trim(),
          slug: String(form.get('slug') ?? '').trim(),
          addressLine1: String(form.get('addressLine1') ?? '').trim(),
          addressLine2: String(form.get('addressLine2') ?? '').trim() || null,
          city: String(form.get('city') ?? '').trim(),
          postalCode: String(form.get('postalCode') ?? '').trim() || null,
          timezone: String(form.get('timezone') ?? '').trim(),
          publicPhone: String(form.get('publicPhone') ?? '').trim() || null,
          publicEmail: String(form.get('publicEmail') ?? '').trim() || null,
          whatsappNumber: String(form.get('whatsappNumber') ?? '').trim() || null,
          websiteUrl: String(form.get('websiteUrl') ?? '').trim() || null,
          active: form.get('active') === 'on',
          bookable: form.get('bookable') === 'on',
          isDefault: form.get('isDefault') === 'on'
        })
      });
    } catch (cause) {
      return fail(400, {
        ok: false,
        message:
          cause instanceof ApiRequestError && cause.code === 'branch_slug_conflict'
            ? 'Slug cabang sudah dipakai.'
            : 'Perubahan gagal disimpan.'
      });
    }

    return { ok: true, message: 'Detail cabang tersimpan.' };
  },

  settings: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();

    // One address per line in the textarea; blank lines dropped.
    const recipients = String(form.get('tourNotificationRecipients') ?? '')
      .split(/[\n,]/)
      .map((value) => value.trim())
      .filter(Boolean);

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}/settings`, {
        method: 'PUT',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          senderDisplayName: String(form.get('senderDisplayName') ?? '').trim() || null,
          replyToEmail: String(form.get('replyToEmail') ?? '').trim() || null,
          tourNotificationRecipients: recipients,
          tourIntroHtml: String(form.get('tourIntroHtml') ?? '').trim() || null,
          arrivalInstructions: String(form.get('arrivalInstructions') ?? '').trim() || null,
          parkingNotes: String(form.get('parkingNotes') ?? '').trim() || null
        })
      });
    } catch {
      return fail(400, { ok: false, message: 'Pengaturan gagal disimpan.' });
    }

    return { ok: true, message: 'Pengaturan tersimpan.' };
  },

  hours: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();

    // The whole week is replaced in one call: a day left unchecked is simply absent.
    const items = [1, 2, 3, 4, 5, 6, 7]
      .filter((day) => form.get(`day-${day}-active`) === 'on')
      .map((day) => ({
        dayOfWeek: day,
        opensAtLocal: `${String(form.get(`day-${day}-opens`) ?? '10:00')}:00`,
        closesAtLocal: `${String(form.get(`day-${day}-closes`) ?? '18:00')}:00`,
        active: true,
        sortOrder: day
      }));

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}/opening-hours`, {
        method: 'PUT',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ items })
      });
    } catch {
      return fail(400, { ok: false, message: 'Jam buka gagal disimpan.' });
    }

    return { ok: true, message: 'Jam buka tersimpan.' };
  },

  addClosure: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const startDate = String(form.get('startDate') ?? '').trim();
    const endDate = String(form.get('endDate') ?? '').trim() || startDate;

    if (!startDate) {
      return fail(400, { ok: false, message: 'Tanggal mulai wajib diisi.' });
    }

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}/closures`, {
        method: 'POST',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          startsAtLocal: `${startDate}T00:00:00`,
          endsAtLocal: `${endDate}T23:59:00`,
          fullDay: true,
          reason: String(form.get('reason') ?? '').trim() || null,
          publicLabel: String(form.get('publicLabel') ?? '').trim() || null,
          active: true
        })
      });
    } catch {
      return fail(400, { ok: false, message: 'Tanggal tutup gagal ditambahkan.' });
    }

    return { ok: true, message: 'Tanggal tutup ditambahkan.' };
  },

  deleteClosure: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const closureId = String(form.get('closureId') ?? '').trim();

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}/closures/${closureId}`, {
        method: 'DELETE',
        token
      });
    } catch {
      return fail(400, { ok: false, message: 'Tanggal tutup gagal dihapus.' });
    }

    return { ok: true, message: 'Tanggal tutup dihapus.' };
  }
};
```

- [ ] **Step 2: Write the page**

Create `apps/cms/src/routes/branches/[id]/+page.svelte`:

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';

  import type { AdminBranch } from '$lib/api';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as Table from '$lib/components/ui/table';

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

<PageHeader title={branch.name} description={`/tour/${branch.slug}`} />

{#if form?.message}
  <p class="mb-4 text-sm" class:text-destructive={form.ok === false}>{form.message}</p>
{/if}

<div class="mb-6 flex gap-2 border-b border-border/60">
  {#each tabs as item}
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
      <label><input type="checkbox" name="bookable" checked={branch.bookable} /> Terima kunjungan</label>
      <label><input type="checkbox" name="isDefault" checked={branch.isDefault} /> Cabang default</label>
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
      <Textarea id="tourIntroHtml" name="tourIntroHtml" rows={4} value={branch.settings?.tourIntroHtml ?? ''} />
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
      <Textarea id="parkingNotes" name="parkingNotes" rows={3} value={branch.settings?.parkingNotes ?? ''} />
    </div>
    <div><Button type="submit">Simpan pengaturan</Button></div>
  </form>
{/if}

{#if tab === 'hours'}
  <form method="POST" action="?/hours" use:enhance class="grid max-w-xl gap-3">
    {#each DAYS as day}
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
  <form method="POST" action="?/addClosure" use:enhance class="mb-6 grid max-w-xl gap-3 sm:grid-cols-2">
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
```

- [ ] **Step 3: Verify**

Run: `cd apps/cms && pnpm run check`
Expected: `0 errors`.

- [ ] **Step 4: Commit**

```bash
git add "apps/cms/src/routes/branches/[id]"
git commit -m "feat(cms): edit branch details, settings, opening hours and closures"
```

---

### Task 4: Events list with a branch column and filter

**Files:**
- Create: `apps/cms/src/routes/events/+page.server.ts`
- Create: `apps/cms/src/routes/events/+page.svelte`

- [ ] **Step 1: Write the loader and action**

Create `apps/cms/src/routes/events/+page.server.ts`. The branch filter is a URL search param, so a filtered list is linkable and survives a reload:

```ts
import { fail, redirect } from '@sveltejs/kit';

import type { AdminBranch, AdminEvent } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  const branchId = url.searchParams.get('branchId') ?? '';
  const query = branchId ? `?branchId=${encodeURIComponent(branchId)}` : '';

  try {
    const [events, branches] = await Promise.all([
      apiFetch<{ items: AdminEvent[] }>(`/api/v1/admin/events${query}`, { token: locals.token }),
      apiFetch<{ items: AdminBranch[] }>('/api/v1/admin/branches', { token: locals.token })
    ]);

    return { error: '', events: events.items, branches: branches.items, branchId };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError ? error.message : 'Tidak bisa memuat acara.',
      events: [] as AdminEvent[],
      branches: [] as AdminBranch[],
      branchId
    };
  }
};

export const actions: Actions = {
  create: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const branchValue = String(form.get('branchId') ?? '').trim();

    // The redirect is thrown OUTSIDE the try: SvelteKit signals redirects by
    // throwing, so a `throw redirect(...)` inside a try lands in the catch and
    // gets swallowed as a failure.
    let createdId: number;
    try {
      const created = await apiFetch<{ data: AdminEvent }>('/api/v1/admin/events', {
        method: 'POST',
        token: locals.token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          // "" means every branch; only an org-wide user may do that and the API enforces it.
          branchId: branchValue ? Number(branchValue) : null,
          name: String(form.get('name') ?? '').trim(),
          venue: String(form.get('venue') ?? '').trim() || null,
          capacity: form.get('capacity') ? Number(form.get('capacity')) : null,
          registrationOpensAt: String(form.get('registrationOpensAt') ?? '') || null,
          registrationClosesAt: String(form.get('registrationClosesAt') ?? '') || null
        })
      });
      createdId = created.data.id;
    } catch (error) {
      return fail(400, {
        ok: false,
        message:
          error instanceof ApiRequestError && error.code === 'branch_forbidden'
            ? 'Anda tidak punya akses ke cabang tersebut.'
            : 'Acara gagal dibuat.'
      });
    }

    throw redirect(303, `/events/${createdId}`);
  }
};
```

- [ ] **Step 2: Write the page**

Create `apps/cms/src/routes/events/+page.svelte`:

```svelte
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
        <option value={branch.id}>{branch.name}</option>
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
```

- [ ] **Step 3: Verify**

Run: `cd apps/cms && pnpm run check`
Expected: `0 errors`.

- [ ] **Step 4: Commit**

```bash
git add apps/cms/src/routes/events/+page.server.ts apps/cms/src/routes/events/+page.svelte
git commit -m "feat(cms): list events with a branch column and filter"
```

---

### Task 5: Event detail — form, registrations, email templates

**Files:**
- Create: `apps/cms/src/routes/events/[id]/+page.server.ts`
- Create: `apps/cms/src/routes/events/[id]/+page.svelte`
- Create: `apps/cms/src/routes/events/[id]/export/+server.ts`

- [ ] **Step 1: Write the loader and actions**

Create `apps/cms/src/routes/events/[id]/+page.server.ts`:

```ts
import { error, fail, redirect } from '@sveltejs/kit';

import type { AdminBranch, AdminEmailTemplate, AdminEvent, AdminRegistration } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params, url }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  const statusFilter = url.searchParams.get('status') ?? '';
  const search = url.searchParams.get('q') ?? '';
  const registrationQuery = new URLSearchParams({ eventId: params.id });
  if (statusFilter) registrationQuery.set('status', statusFilter);
  if (search) registrationQuery.set('q', search);

  try {
    const [event, registrations, templates, branches] = await Promise.all([
      apiFetch<{ data: AdminEvent }>(`/api/v1/admin/events/${params.id}`, { token: locals.token }),
      apiFetch<{ items: AdminRegistration[] }>(
        `/api/v1/admin/event-registrations?${registrationQuery.toString()}`,
        { token: locals.token }
      ),
      apiFetch<{ data: { placeholders: string[]; templates: AdminEmailTemplate[] } }>(
        `/api/v1/admin/events/${params.id}/email-templates`,
        { token: locals.token }
      ),
      apiFetch<{ items: AdminBranch[] }>('/api/v1/admin/branches', { token: locals.token })
    ]);

    return {
      event: event.data,
      registrations: registrations.items,
      placeholders: templates.data.placeholders,
      templates: templates.data.templates,
      branches: branches.items,
      statusFilter,
      search
    };
  } catch (cause) {
    if (cause instanceof ApiRequestError && cause.status === 404) {
      throw error(404, 'Acara tidak ditemukan.');
    }
    throw cause;
  }
};

const requireToken = (locals: App.Locals) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }
  return locals.token;
};

export const actions: Actions = {
  details: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const branchValue = String(form.get('branchId') ?? '').trim();

    try {
      await apiFetch(`/api/v1/admin/events/${params.id}`, {
        method: 'PATCH',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          branchId: branchValue ? Number(branchValue) : null,
          name: String(form.get('name') ?? '').trim(),
          descriptionHtml: String(form.get('descriptionHtml') ?? ''),
          venue: String(form.get('venue') ?? '').trim() || null,
          capacity: form.get('capacity') ? Number(form.get('capacity')) : null,
          registrationOpensAt: String(form.get('registrationOpensAt') ?? '') || null,
          registrationClosesAt: String(form.get('registrationClosesAt') ?? '') || null,
          eventStartAt: String(form.get('eventStartAt') ?? '') || null,
          eventEndAt: String(form.get('eventEndAt') ?? '') || null,
          isActive: form.get('isActive') === 'on'
        })
      });
    } catch (cause) {
      return fail(400, {
        ok: false,
        message:
          cause instanceof ApiRequestError && cause.code === 'branch_forbidden'
            ? 'Anda tidak punya akses ke cabang tersebut.'
            : 'Acara gagal disimpan.'
      });
    }

    return { ok: true, message: 'Acara tersimpan.' };
  },

  addRegistration: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();

    try {
      await apiFetch('/api/v1/admin/event-registrations', {
        method: 'POST',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          eventId: Number(params.id),
          name: String(form.get('name') ?? '').trim(),
          email: String(form.get('email') ?? '').trim(),
          mobile: String(form.get('mobile') ?? '').trim() || null,
          visitDate: String(form.get('visitDate') ?? '') || null,
          visitSlot: String(form.get('visitSlot') ?? '').trim() || null,
          notes: String(form.get('notes') ?? '').trim() || null,
          guests: []
        })
      });
    } catch (cause) {
      const code = cause instanceof ApiRequestError ? cause.code : '';
      const messages: Record<string, string> = {
        already_registered: 'Email ini sudah terdaftar untuk acara tersebut.',
        event_full: 'Kuota acara sudah penuh.',
        branch_closed: 'Cabang tutup pada tanggal tersebut.',
        registration_closed: 'Pendaftaran sudah ditutup.'
      };
      return fail(400, { ok: false, message: messages[code] ?? 'Pendaftaran gagal disimpan.' });
    }

    return { ok: true, message: 'Pendaftaran ditambahkan.' };
  },

  updateRegistration: async ({ locals, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const id = String(form.get('registrationId') ?? '').trim();

    const body: Record<string, unknown> = {};
    if (form.has('status')) body.status = String(form.get('status'));
    if (form.has('followUp')) body.followUp = form.get('followUp') === 'true';
    if (form.has('notes')) body.notes = String(form.get('notes'));

    try {
      await apiFetch(`/api/v1/admin/event-registrations/${id}`, {
        method: 'PATCH',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(body)
      });
    } catch {
      return fail(400, { ok: false, message: 'Pendaftaran gagal diperbarui.' });
    }

    return { ok: true, message: 'Pendaftaran diperbarui.' };
  },

  saveTemplate: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const kind = String(form.get('kind') ?? '').trim();

    try {
      await apiFetch(`/api/v1/admin/events/${params.id}/email-templates/${kind}`, {
        method: 'PUT',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          subject: String(form.get('subject') ?? ''),
          body: String(form.get('body') ?? ''),
          enabled: form.get('enabled') === 'on'
        })
      });
    } catch {
      return fail(400, { ok: false, message: 'Template gagal disimpan.' });
    }

    return { ok: true, message: 'Template tersimpan.' };
  }
};
```

- [ ] **Step 2: Write the page**

Create `apps/cms/src/routes/events/[id]/+page.svelte`:

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';
  import { goto } from '$app/navigation';
  import DownloadIcon from '@lucide/svelte/icons/download';

  import type { AdminBranch, AdminEmailTemplate, AdminEvent, AdminRegistration } from '$lib/api';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as Table from '$lib/components/ui/table';

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

<PageHeader title={event.name} description={event.branchName ?? 'Semua cabang'} />

{#if form?.message}
  <p class="mb-4 text-sm" class:text-destructive={form.ok === false}>{form.message}</p>
{/if}

<div class="mb-6 flex gap-2 border-b border-border/60">
  {#each tabs as item}
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
            {registration.visitDate ?? '—'}{registration.visitSlot ? ` · ${registration.visitSlot}` : ''}
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
      <Textarea id="descriptionHtml" name="descriptionHtml" rows={6} value={event.descriptionHtml} />
      <p class="text-xs text-muted-foreground">
        Tag yang diizinkan: p, br, strong, em, ul, ol, li, h2, h3, h4, a. Sisanya dibuang saat disimpan.
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
```

- [ ] **Step 3: Write the CSV proxy**

Create `apps/cms/src/routes/events/[id]/export/+server.ts`:

```ts
import { redirect } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/server/api';

import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ locals, params }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  // apiFetch parses JSON, and this endpoint returns CSV -- so call through
  // directly and stream the body back with its filename intact.
  const response = await fetch(
    `${getApiBaseUrl()}/api/v1/admin/event-registrations/export?eventId=${params.id}`,
    { headers: { Authorization: `Bearer ${locals.token}` } }
  );

  if (!response.ok) {
    return new Response('Ekspor gagal.', { status: response.status });
  }

  return new Response(response.body, {
    headers: {
      'content-type': 'text/csv',
      'content-disposition': `attachment; filename="event-${params.id}-registrations.csv"`
    }
  });
};
```

- [ ] **Step 4: Verify**

Run: `cd apps/cms && pnpm run check`
Expected: `0 errors`.

- [ ] **Step 5: Commit**

```bash
git add "apps/cms/src/routes/events/[id]"
git commit -m "feat(cms): manage an event, its registrations and its email templates"
```

---

### Task 6: Tour date and slot derivation (pure logic, tested first)

The public form must only offer dates the branch is open. That rule is pure and belongs in a tested module rather than inline in a component.

**Files:**
- Create: `apps/web/src/lib/tour-availability.ts`
- Test: `apps/web/src/lib/tour-availability.test.ts`

- [ ] **Step 1: Write the failing test**

Create `apps/web/src/lib/tour-availability.test.ts`:

```ts
import { describe, expect, it } from 'vitest';

import { isDateBookable, slotsForDate } from './tour-availability';

const HOURS = [
  { dayOfWeek: 1, opensAtLocal: '10:00:00', closesAtLocal: '13:00:00' },
  { dayOfWeek: 6, opensAtLocal: '09:00:00', closesAtLocal: '10:30:00' }
];

describe('isDateBookable', () => {
  it('accepts a day the branch has hours for', () => {
    // 2026-09-07 is a Monday.
    expect(isDateBookable('2026-09-07', HOURS, [])).toBe(true);
  });

  it('rejects a day with no hours', () => {
    // 2026-09-08 is a Tuesday, which is not in HOURS.
    expect(isDateBookable('2026-09-08', HOURS, [])).toBe(false);
  });

  it('rejects a closed date even when the weekday is open', () => {
    expect(isDateBookable('2026-09-07', HOURS, ['2026-09-07'])).toBe(false);
  });
});

describe('slotsForDate', () => {
  it('lists hourly slots from opening to closing, excluding the closing hour', () => {
    expect(slotsForDate('2026-09-07', HOURS)).toEqual(['10:00', '11:00', '12:00']);
  });

  it('rounds a part-hour window down so no slot runs past closing', () => {
    // Saturday closes at 10:30, so 10:00 is the last slot that fits.
    expect(slotsForDate('2026-09-12', HOURS)).toEqual(['09:00', '10:00']);
  });

  it('returns nothing for a day the branch is shut', () => {
    expect(slotsForDate('2026-09-08', HOURS)).toEqual([]);
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/web && pnpm vitest run src/lib/tour-availability.test.ts`
Expected: FAIL — cannot resolve `./tour-availability`.

- [ ] **Step 3: Write the module**

Create `apps/web/src/lib/tour-availability.ts`:

```ts
export type OpeningHour = {
  dayOfWeek: number; // ISO: Monday = 1 ... Sunday = 7
  opensAtLocal: string; // "10:00:00"
  closesAtLocal: string;
};

/** ISO weekday for a "YYYY-MM-DD" string, without dragging the browser timezone
 * into it: `new Date('2026-09-07')` is parsed as UTC midnight, which lands on the
 * previous day west of Greenwich. */
export function isoWeekday(isoDate: string): number {
  const [year, month, day] = isoDate.split('-').map(Number);
  const weekday = new Date(Date.UTC(year, month - 1, day)).getUTCDay();
  return weekday === 0 ? 7 : weekday;
}

const toMinutes = (value: string) => {
  const [hours, minutes] = value.split(':').map(Number);
  return hours * 60 + minutes;
};

const pad = (value: number) => String(value).padStart(2, '0');

export function isDateBookable(
  isoDate: string,
  hours: OpeningHour[],
  closedDates: string[]
): boolean {
  if (closedDates.includes(isoDate)) {
    return false;
  }
  const weekday = isoWeekday(isoDate);
  return hours.some((hour) => hour.dayOfWeek === weekday);
}

/** Hourly slots that start and finish inside the opening window. A tour is
 * assumed to take an hour; a window closing at 10:30 therefore offers 10:00 as
 * its last slot and never 10:30. */
export function slotsForDate(isoDate: string, hours: OpeningHour[]): string[] {
  const weekday = isoWeekday(isoDate);
  const slots: string[] = [];

  for (const hour of hours.filter((row) => row.dayOfWeek === weekday)) {
    const opens = toMinutes(hour.opensAtLocal);
    const closes = toMinutes(hour.closesAtLocal);
    for (let start = opens; start + 30 <= closes; start += 60) {
      slots.push(`${pad(Math.floor(start / 60))}:${pad(start % 60)}`);
    }
  }

  return [...new Set(slots)].sort();
}
```

- [ ] **Step 4: Run the tests**

Run: `cd apps/web && pnpm vitest run src/lib/tour-availability.test.ts`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/tour-availability.ts apps/web/src/lib/tour-availability.test.ts
git commit -m "feat(web): derive bookable tour dates and slots from branch hours"
```

---

### Task 7: Public branch picker at /tour

**Files:**
- Create: `apps/web/src/routes/tour/+page.server.ts`
- Create: `apps/web/src/routes/tour/+page.svelte`
- Modify: `apps/web/messages/id.json`
- Modify: `apps/web/messages/en.json`

- [ ] **Step 1: Add the copy**

Add to `apps/web/messages/id.json` (keys stay alphabetically sorted, as the file already is):

```json
  "tour_branch_pick": "Pilih cabang",
  "tour_empty": "Belum ada cabang yang menerima kunjungan saat ini.",
  "tour_intro": "Datang, lihat langsung, dan ngobrol dengan tim kami. Kunjungan gratis dan tanpa komitmen.",
  "tour_meta_description": "Jadwalkan kunjungan ke cabang 7Magic terdekat. Lihat venue, tanya paket, dan temui tim kami.",
  "tour_meta_title": "Book a Tour | 7Magic Wedding",
  "tour_title": "Kunjungi 7Magic"
```

Add the English equivalents to `apps/web/messages/en.json`:

```json
  "tour_branch_pick": "Choose a branch",
  "tour_empty": "No branch is taking visits right now.",
  "tour_intro": "Come see the space and talk to our team. The visit is free and there is no commitment.",
  "tour_meta_description": "Book a visit to your nearest 7Magic branch. See the venue, ask about packages, meet the team.",
  "tour_meta_title": "Book a Tour | 7Magic Wedding",
  "tour_title": "Visit 7Magic"
```

- [ ] **Step 2: Write the loader**

Create `apps/web/src/routes/tour/+page.server.ts`:

```ts
import { fetchJson } from '$lib/api';

import type { PageServerLoad } from './$types';

export type TourBranch = {
  id: number;
  slug: string;
  name: string;
  city: string;
  addressLine1: string;
  addressLine2: string | null;
  publicPhone: string | null;
  publicEmail: string | null;
  whatsappNumber: string | null;
};

export const load: PageServerLoad = async ({ fetch }) => {
  try {
    const data = await fetchJson<{ items: TourBranch[] }>('/api/v1/public/tour/branches', fetch);
    return { branches: data.items };
  } catch {
    // A branch list that fails to load must not 500 the page; the empty state covers it.
    return { branches: [] as TourBranch[] };
  }
};
```

- [ ] **Step 3: Write the page**

Create `apps/web/src/routes/tour/+page.svelte`:

```svelte
<script lang="ts">
  import MapPinIcon from '@lucide/svelte/icons/map-pin';

  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import * as m from '$lib/paraglide/messages';

  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<svelte:head>
  <title>{m.tour_meta_title()}</title>
  <meta name="description" content={m.tour_meta_description()} />
</svelte:head>

<PublicHeader />

<main class="mx-auto w-full max-w-5xl px-4 py-12">
  <h1 class="text-3xl font-semibold">{m.tour_title()}</h1>
  <p class="mt-3 max-w-2xl text-muted-foreground">{m.tour_intro()}</p>

  <h2 class="mt-10 mb-4 text-lg font-medium">{m.tour_branch_pick()}</h2>

  {#if data.branches.length === 0}
    <p class="text-muted-foreground">{m.tour_empty()}</p>
  {:else}
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each data.branches as branch (branch.id)}
        <Card.Root>
          <Card.Header>
            <Card.Title>{branch.name}</Card.Title>
            <Card.Description class="flex items-center gap-1">
              <MapPinIcon class="size-4" />
              {branch.city}
            </Card.Description>
          </Card.Header>
          <Card.Content class="text-sm text-muted-foreground">
            <p>{branch.addressLine1}</p>
            {#if branch.addressLine2}<p>{branch.addressLine2}</p>{/if}
          </Card.Content>
          <Card.Footer>
            <Button href={`/tour/${branch.slug}`}>{m.tour_branch_pick()}</Button>
          </Card.Footer>
        </Card.Root>
      {/each}
    </div>
  {/if}
</main>

<PublicFooter />
```

If `PublicHeader`/`PublicFooter` take required props in this codebase, match how `src/routes/contact/+page.svelte` calls them.

- [ ] **Step 4: Verify**

Run: `cd apps/web && pnpm run check`
Expected: `0 errors`.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/routes/tour apps/web/messages/id.json apps/web/messages/en.json
git commit -m "feat(web): list bookable branches at /tour"
```

---

### Task 8: The Book a Tour form at /tour/[slug]

**Files:**
- Create: `apps/web/src/routes/tour/[slug]/+page.server.ts`
- Create: `apps/web/src/routes/tour/[slug]/+page.svelte`
- Modify: `apps/web/messages/id.json`
- Modify: `apps/web/messages/en.json`

- [ ] **Step 1: Add the copy**

Add to `apps/web/messages/id.json`:

```json
  "tour_closed": "Cabang ini sedang tidak menerima pendaftaran kunjungan.",
  "tour_error_already": "Email ini sudah terdaftar untuk kunjungan tersebut.",
  "tour_error_branch_closed": "Kami tutup pada tanggal itu. Silakan pilih tanggal lain.",
  "tour_error_full": "Kuota kunjungan sudah penuh.",
  "tour_error_generic": "Pendaftaran gagal dikirim. Silakan coba lagi.",
  "tour_field_date": "Tanggal kunjungan",
  "tour_field_email": "Email",
  "tour_field_guests": "Jumlah tamu tambahan",
  "tour_field_mobile": "Nomor WhatsApp",
  "tour_field_name": "Nama lengkap",
  "tour_field_slot": "Jam kunjungan",
  "tour_submit": "Jadwalkan kunjungan",
  "tour_success": "Terima kasih! Pendaftaran Anda sudah kami terima dan detailnya dikirim ke email Anda."
```

Add the English equivalents to `apps/web/messages/en.json`:

```json
  "tour_closed": "This branch is not taking visit bookings right now.",
  "tour_error_already": "This email is already registered for that visit.",
  "tour_error_branch_closed": "We are closed on that date. Please pick another one.",
  "tour_error_full": "This visit is fully booked.",
  "tour_error_generic": "We could not send your booking. Please try again.",
  "tour_field_date": "Visit date",
  "tour_field_email": "Email",
  "tour_field_guests": "Extra guests",
  "tour_field_mobile": "WhatsApp number",
  "tour_field_name": "Full name",
  "tour_field_slot": "Visit time",
  "tour_submit": "Book the visit",
  "tour_success": "Thank you! Your booking is confirmed and the details are on their way to your inbox."
```

- [ ] **Step 2: Write the loader and action**

Create `apps/web/src/routes/tour/[slug]/+page.server.ts`:

```ts
import { error, fail } from '@sveltejs/kit';

import { fetchJson, getApiBaseUrl } from '$lib/api';
import type { OpeningHour } from '$lib/tour-availability';

import type { Actions, PageServerLoad } from './$types';

type TourBranchDetail = {
  branch: {
    id: number;
    slug: string;
    name: string;
    city: string;
    addressLine1: string;
    addressLine2: string | null;
    publicPhone: string | null;
    publicEmail: string | null;
    whatsappNumber: string | null;
  };
  settings: {
    tourIntroHtml: string | null;
    arrivalInstructions: string | null;
    parkingNotes: string | null;
  };
  event: {
    id: number;
    name: string;
    descriptionHtml: string;
    venue: string | null;
    registrationOpen: boolean;
    registrationClosedReason: string | null;
  } | null;
  openingHours: OpeningHour[];
  closedDates: string[];
};

export const load: PageServerLoad = async ({ fetch, params }) => {
  try {
    const data = await fetchJson<{ data: TourBranchDetail }>(
      `/api/v1/public/tour/branches/${params.slug}`,
      fetch
    );
    return data.data;
  } catch {
    throw error(404, 'Branch not found');
  }
};

export const actions: Actions = {
  default: async ({ fetch, params, request }) => {
    const form = await request.formData();

    const guestCount = Number(form.get('guests') ?? 0);
    const guests = Array.from({ length: Math.max(0, Math.min(guestCount, 10)) }, (_, index) => ({
      name: String(form.get(`guest-${index}`) ?? `Tamu ${index + 1}`).trim() || `Tamu ${index + 1}`
    }));

    const response = await fetch(
      `${getApiBaseUrl()}/api/v1/public/tour/branches/${params.slug}/register`,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          name: String(form.get('name') ?? '').trim(),
          email: String(form.get('email') ?? '').trim(),
          mobile: String(form.get('mobile') ?? '').trim() || null,
          visitDate: String(form.get('visitDate') ?? '') || null,
          visitSlot: String(form.get('visitSlot') ?? '') || null,
          guests
        })
      }
    );

    if (response.ok) {
      return { ok: true, code: '' };
    }

    // The API's error code drives which translated message the page shows, so the
    // copy stays in the message catalogue rather than in the server response.
    const payload = (await response.json().catch(() => ({}))) as {
      error?: { code?: string };
    };
    return fail(response.status === 422 ? 422 : 409, {
      ok: false,
      code: payload.error?.code ?? 'generic'
    });
  }
};
```

If `getApiBaseUrl` is not exported from `apps/web/src/lib/api.ts`, check what `fetchJson` uses internally and export it, or inline the same base-URL expression here.

- [ ] **Step 3: Write the page**

Create `apps/web/src/routes/tour/[slug]/+page.svelte`:

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';

  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as m from '$lib/paraglide/messages';
  import { isDateBookable, slotsForDate } from '$lib/tour-availability';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  let visitDate = $state('');
  let extraGuests = $state(0);

  const slots = $derived(visitDate ? slotsForDate(visitDate, data.openingHours) : []);
  const dateIsClosed = $derived(
    visitDate.length === 10 && !isDateBookable(visitDate, data.openingHours, data.closedDates)
  );

  const today = new Date().toISOString().slice(0, 10);

  const ERROR_MESSAGES: Record<string, () => string> = {
    already_registered: m.tour_error_already,
    event_full: m.tour_error_full,
    branch_closed: m.tour_error_branch_closed
  };

  const errorMessage = $derived(
    form && form.ok === false
      ? (ERROR_MESSAGES[form.code] ?? m.tour_error_generic)()
      : ''
  );
</script>

<svelte:head>
  <title>{`${m.tour_title()} · ${data.branch.name}`}</title>
  <meta name="description" content={m.tour_meta_description()} />
</svelte:head>

<PublicHeader />

<main class="mx-auto w-full max-w-3xl px-4 py-12">
  <h1 class="text-3xl font-semibold">{data.branch.name}</h1>
  <p class="mt-2 text-muted-foreground">
    {data.branch.addressLine1}{data.branch.addressLine2 ? `, ${data.branch.addressLine2}` : ''}
  </p>

  {#if data.settings.tourIntroHtml}
    <!-- Sanitized on write by the API's allowlist; see domains/events/sanitize.py -->
    <div class="prose mt-6">{@html data.settings.tourIntroHtml}</div>
  {/if}

  {#if form?.ok}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_success()}</p>
  {:else if !data.event || !data.event.registrationOpen}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_closed()}</p>
  {:else}
    {#if errorMessage}
      <p class="mt-6 text-sm text-destructive">{errorMessage}</p>
    {/if}

    <form method="POST" use:enhance class="mt-8 grid gap-4 sm:grid-cols-2">
      <div class="grid gap-2">
        <Label for="name">{m.tour_field_name()}</Label>
        <Input id="name" name="name" required />
      </div>
      <div class="grid gap-2">
        <Label for="email">{m.tour_field_email()}</Label>
        <Input id="email" name="email" type="email" required />
      </div>
      <div class="grid gap-2">
        <Label for="mobile">{m.tour_field_mobile()}</Label>
        <Input id="mobile" name="mobile" />
      </div>
      <div class="grid gap-2">
        <Label for="visitDate">{m.tour_field_date()}</Label>
        <Input id="visitDate" name="visitDate" type="date" min={today} bind:value={visitDate} required />
        {#if dateIsClosed}
          <p class="text-sm text-destructive">{m.tour_error_branch_closed()}</p>
        {/if}
      </div>
      <div class="grid gap-2">
        <Label for="visitSlot">{m.tour_field_slot()}</Label>
        <select
          id="visitSlot"
          name="visitSlot"
          class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
          disabled={slots.length === 0 || dateIsClosed}
        >
          {#each slots as slot (slot)}
            <option value={slot}>{slot}</option>
          {/each}
        </select>
      </div>
      <div class="grid gap-2">
        <Label for="guests">{m.tour_field_guests()}</Label>
        <Input id="guests" name="guests" type="number" min="0" max="10" bind:value={extraGuests} />
      </div>

      {#each Array.from({ length: Math.max(0, Math.min(extraGuests, 10)) }, (_, index) => index) as index (index)}
        <div class="grid gap-2">
          <Label for={`guest-${index}`}>{`${m.tour_field_guests()} ${index + 1}`}</Label>
          <Input id={`guest-${index}`} name={`guest-${index}`} />
        </div>
      {/each}

      <div class="sm:col-span-2">
        <Button type="submit" disabled={dateIsClosed}>{m.tour_submit()}</Button>
      </div>
    </form>

    {#if data.settings.arrivalInstructions || data.settings.parkingNotes}
      <div class="mt-10 grid gap-2 text-sm text-muted-foreground">
        {#if data.settings.arrivalInstructions}<p>{data.settings.arrivalInstructions}</p>{/if}
        {#if data.settings.parkingNotes}<p>{data.settings.parkingNotes}</p>{/if}
      </div>
    {/if}
  {/if}
</main>

<PublicFooter />
```

- [ ] **Step 4: Verify**

Run: `cd apps/web && pnpm run check && pnpm vitest run`
Expected: `0 errors` and all vitest suites pass.

- [ ] **Step 5: Commit**

```bash
git add "apps/web/src/routes/tour/[slug]" apps/web/messages/id.json apps/web/messages/en.json
git commit -m "feat(web): book a tour of a specific branch"
```

---

### Task 9: End-to-end check against a running stack

**Files:** none — this task verifies.

- [ ] **Step 1: Start everything**

Run: `./rundev.sh`
Expected: api on 8003, web on 5182, cms on 5181.

- [ ] **Step 2: Seed a branch through the CMS**

Open `https://cms.7magic.localhost/branches`, sign in, and create a branch with slug `bali`. Then on its detail page:
- **Jam buka** tab: tick Monday–Saturday, 10:00 to 18:00, save.
- **Tanggal tutup** tab: add tomorrow's date with public label "Libur".
- **Pengaturan** tab: put your own address in the notification recipients box, save.

- [ ] **Step 3: Create the tour event**

At `https://cms.7magic.localhost/events`, create an event named `Book a Tour`, branch `bali`, registration opening yesterday and closing in 30 days.

- [ ] **Step 4: Book it as a visitor**

Open `https://7magic.localhost/tour`, pick the Bali branch, and submit the form.

Confirm, in order:
1. The date picker refuses the closure date you added (the closed-date warning shows and Submit is disabled).
2. A Sunday offers no slots.
3. Submitting shows the success message.
4. The registration appears at `https://cms.7magic.localhost/events/<id>` under **Pendaftar**, with source `public`.
5. Marking it **Hadir** flips the status and stamps the attendance.
6. **Ekspor CSV** downloads a file whose first row is the header from Plan 1's `CSV_HEADER`.

- [ ] **Step 5: Check the English route**

Open `https://7magic.localhost/en/tour`. Expected: the same page in English — the existing `deLocalizeUrl` reroute in `apps/web/src/hooks.ts` maps it to the same route, so no `/en/tour` folder should exist.

- [ ] **Step 6: Run everything**

Run: `pnpm check && pnpm test && cd apps/api && uv run pytest -q && uv run ruff check .`
Expected: all green.

- [ ] **Step 7: Commit any fixes**

```bash
git add -A
git commit -m "fix: address issues found end-to-end in the branch and tour flow"
```

---

## Done means

- A visitor can pick a branch at `/tour`, book a visit, and get a confirmation email; the branch's recipients get an alert.
- A closed date or a day with no opening hours cannot be booked, in the form and again in the API.
- The CMS lists branches and events, both showing branch as a column with a working filter, and no branch switcher exists anywhere.
- A branch-scoped user sees only their branch's events and registrations (verified by Plan 1's API tests; the UI simply renders what it is given).
- `pnpm check`, `pnpm test`, `uv run pytest`, `uv run ruff check .` are all green.
