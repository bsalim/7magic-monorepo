<script lang="ts">
  import { enhance } from '$app/forms';
  import { goto } from '$app/navigation';
  import DownloadIcon from '@lucide/svelte/icons/download';

  import type { AdminBranch, AdminEmailTemplate, AdminEvent, AdminRegistration } from '$lib/api';
  import DateField from '$lib/components/DateField.svelte';
  import DateTimeField from '$lib/components/DateTimeField.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Table from '$lib/components/ui/table';
  import { Textarea } from '$lib/components/ui/textarea';
  import { formatDate } from '$lib/format-date';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const event = $derived(data.event as AdminEvent);
  const registrations = $derived(data.registrations as AdminRegistration[]);
  const templates = $derived(data.templates as AdminEmailTemplate[]);
  const branches = $derived(data.branches as AdminBranch[]);

  let tab = $state<'details' | 'registrations' | 'emails'>('registrations');
  const tabs = [
    { key: 'registrations', label: 'Registrations' },
    { key: 'details', label: 'Event details' },
    { key: 'emails', label: 'Email' }
  ] as const;

  const STATUS_LABELS: Record<AdminRegistration['status'], string> = {
    registered: 'Registered',
    attended: 'Attended',
    no_show: 'No show',
    cancelled: 'Cancelled'
  };

  const TEMPLATE_LABELS: Record<AdminEmailTemplate['kind'], string> = {
    thank_you: 'Thank you',
    no_show: 'No show',
    cancel: 'Cancellation'
  };

  // The pickers hold "YYYY-MM-DDTHH:mm"; the API returns full ISO strings.
  const toLocalInput = (value: string | null) => (value ? value.slice(0, 16) : '');

  let newVisitDate = $state('');
  let opensAt = $state('');
  let closesAt = $state('');
  let startsAt = $state('');
  let endsAt = $state('');

  // Seeded from the loaded event rather than at declaration, and re-seeded when a
  // different event arrives: SvelteKit reuses this component across
  // /events/1 -> /events/2, so initial-value-only state would show the previous
  // event's timestamps. Guarded on the id so a save does not clobber edits.
  let seededFor = $state<number | null>(null);
  $effect(() => {
    if (seededFor === event.id) return;
    seededFor = event.id;
    opensAt = toLocalInput(event.registration_opens_at);
    closesAt = toLocalInput(event.registration_closes_at);
    startsAt = toLocalInput(event.event_start_at);
    endsAt = toLocalInput(event.event_end_at);
  });

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
  description={event.branch_name ?? 'All branches'}
  backHref="/events"
  backLabel="Events"
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
        <option value="">All</option>
        <option value="registered">Registered</option>
        <option value="attended">Attended</option>
        <option value="no_show">No show</option>
        <option value="cancelled">Cancelled</option>
      </select>
    </div>

    <!-- Proxied through the CMS: the session token lives in a server-side cookie,
         so a link straight at the API origin would download a 401. -->
    <Button variant="outline" size="sm" href={`/events/${event.id}/export`} data-sveltekit-reload>
      <DownloadIcon class="size-4" />
      Export CSV
    </Button>
  </div>

  <form
    method="POST"
    action="?/addRegistration"
    use:enhance
    class="mb-6 grid gap-4 rounded-xl border border-border/60 p-4 sm:grid-cols-3"
  >
    <div class="grid gap-2">
      <Label for="name">Guest name</Label>
      <Input id="name" name="name" required />
    </div>
    <div class="grid gap-2">
      <Label for="email">Email</Label>
      <Input id="email" name="email" type="email" required />
    </div>
    <div class="grid gap-2">
      <Label for="mobile">Mobile</Label>
      <Input id="mobile" name="mobile" />
    </div>
    <div class="grid gap-2">
      <Label for="visit_date">Visit date</Label>
      <DateField name="visit_date" bind:value={newVisitDate} />
    </div>
    <div class="grid gap-2">
      <Label for="visit_slot">Time</Label>
      <Input id="visit_slot" name="visit_slot" placeholder="10:00" />
    </div>
    <div class="flex items-end"><Button type="submit">Add registration</Button></div>
  </form>

  <Table.Root>
    <Table.Header>
      <Table.Row>
        <Table.Head>Guest</Table.Head>
        <Table.Head>Branch</Table.Head>
        <Table.Head>Venue</Table.Head>
        <Table.Head>Visit</Table.Head>
        <Table.Head class="text-right">Party</Table.Head>
        <Table.Head>Status</Table.Head>
        <Table.Head>Source</Table.Head>
        <Table.Head class="text-right">Actions</Table.Head>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {#each registrations as registration (registration.id)}
        <Table.Row>
          <Table.Cell>
            <div class="font-medium">{registration.guest_name}</div>
            <div class="text-xs text-muted-foreground">{registration.email}</div>
          </Table.Cell>
          <Table.Cell>{registration.branch_name ?? '—'}</Table.Cell>
          <Table.Cell>
            <div>{registration.venue_name ?? '—'}</div>
            <!-- The city only when no catalogue row sits behind the name: it is how
                 a staffer spots a venue we do not list yet. -->
            {#if registration.city && !registration.venue_id}
              <div class="text-xs text-muted-foreground">{registration.city}</div>
            {/if}
          </Table.Cell>
          <Table.Cell class="text-sm">
            {formatDate(registration.visit_date)}{registration.visit_slot
              ? ` · ${registration.visit_slot}`
              : ''}
          </Table.Cell>
          <Table.Cell class="text-right">{registration.party_size}</Table.Cell>
          <Table.Cell>{STATUS_LABELS[registration.status]}</Table.Cell>
          <Table.Cell class="text-xs text-muted-foreground">{registration.source}</Table.Cell>
          <Table.Cell class="text-right">
            <form method="POST" action="?/updateRegistration" use:enhance class="inline">
              <input type="hidden" name="registration_id" value={registration.id} />
              <input type="hidden" name="status" value="attended" />
              <Button type="submit" variant="ghost" size="sm">Attended</Button>
            </form>
            <form method="POST" action="?/updateRegistration" use:enhance class="inline">
              <input type="hidden" name="registration_id" value={registration.id} />
              <input type="hidden" name="status" value="no_show" />
              <Button type="submit" variant="ghost" size="sm">No show</Button>
            </form>
            <form method="POST" action="?/updateRegistration" use:enhance class="inline">
              <input type="hidden" name="registration_id" value={registration.id} />
              <input type="hidden" name="follow_up" value={String(!registration.follow_up)} />
              <Button type="submit" variant="ghost" size="sm">
                {registration.follow_up ? 'Clear follow up' : 'Follow up'}
              </Button>
            </form>
          </Table.Cell>
        </Table.Row>
      {:else}
        <Table.Row>
          <Table.Cell colspan={7} class="text-center text-sm text-muted-foreground">
            No registrations yet.
          </Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>
{/if}

{#if tab === 'details'}
  <form method="POST" action="?/details" use:enhance class="grid max-w-3xl gap-4 sm:grid-cols-2">
    <div class="grid gap-2">
      <Label for="name">Event name</Label>
      <Input id="name" name="name" value={event.name} required />
    </div>
    <div class="grid gap-2">
      <Label for="branch_id">Branch</Label>
      <select
        id="branch_id"
        name="branch_id"
        class="h-9 rounded-lg border border-border/60 bg-background px-3 text-sm"
      >
        <option value="" selected={event.branch_id === null}>All branches</option>
        {#each branches as branch (branch.id)}
          <option value={branch.id} selected={branch.id === event.branch_id}>{branch.name}</option>
        {/each}
      </select>
    </div>
    <div class="grid gap-2 sm:col-span-2">
      <Label for="description_html">Description</Label>
      <Textarea
        id="description_html"
        name="description_html"
        rows={6}
        value={event.description_html}
      />
      <p class="text-xs text-muted-foreground">
        Allowed tags: p, br, strong, em, ul, ol, li, h2, h3, h4, a. Anything else is removed when
        saved.
      </p>
    </div>
    <div class="grid gap-2">
      <Label for="venue">Location</Label>
      <Input id="venue" name="venue" value={event.venue ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="capacity">Capacity</Label>
      <Input id="capacity" name="capacity" type="number" min="1" value={event.capacity ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="registration_opens_at">Registration opens</Label>
      <DateTimeField name="registration_opens_at" bind:value={opensAt} />
    </div>
    <div class="grid gap-2">
      <Label for="registration_closes_at">Registration closes</Label>
      <DateTimeField name="registration_closes_at" bind:value={closesAt} />
    </div>
    <div class="grid gap-2">
      <Label for="event_start_at">Event starts</Label>
      <DateTimeField name="event_start_at" bind:value={startsAt} />
    </div>
    <div class="grid gap-2">
      <Label for="event_end_at">Event ends</Label>
      <DateTimeField name="event_end_at" bind:value={endsAt} />
    </div>
    <label class="flex items-center gap-2 text-sm">
      <input type="checkbox" name="is_active" checked={event.is_active} /> Active
    </label>
    <div class="sm:col-span-2"><Button type="submit">Save event</Button></div>
  </form>
{/if}

{#if tab === 'emails'}
  <p class="mb-4 text-sm text-muted-foreground">
    Placeholders: {data.placeholders.map((token) => `{${token}}`).join(', ')}
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
          <Label for={`subject-${template.kind}`}>Subject</Label>
          <Input id={`subject-${template.kind}`} name="subject" value={template.subject} />
        </div>
        <div class="grid gap-2">
          <Label for={`body-${template.kind}`}>Body</Label>
          <Textarea id={`body-${template.kind}`} name="body" rows={8} value={template.body} />
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" name="enabled" checked={template.enabled} /> Enable
        </label>
        <div><Button type="submit" size="sm">Save template</Button></div>
      </form>
    {/each}
  </div>
{/if}
