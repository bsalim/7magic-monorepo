<script lang="ts">
  import { enhance } from '$app/forms';

  import type { AdminBranch } from '$lib/api';
  import DateField from '$lib/components/DateField.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Table from '$lib/components/ui/table';
  import { Textarea } from '$lib/components/ui/textarea';
  import { formatDate } from '$lib/format-date';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const branch = $derived(data.branch as AdminBranch);

  const DAYS = [
    { iso: 1, label: 'Monday' },
    { iso: 2, label: 'Tuesday' },
    { iso: 3, label: 'Wednesday' },
    { iso: 4, label: 'Thursday' },
    { iso: 5, label: 'Friday' },
    { iso: 6, label: 'Saturday' },
    { iso: 7, label: 'Sunday' }
  ];

  // "10:00:00" -> "10:00" for <input type="time">
  const toTimeInput = (value: string | undefined) => (value ? value.slice(0, 5) : '');
  const hourFor = (iso: number) => branch.opening_hours.find((row) => row.day_of_week === iso);

  let tab = $state<'details' | 'settings' | 'hours' | 'closures'>('details');
  const tabs = [
    { key: 'details', label: 'Details' },
    { key: 'settings', label: 'Settings' },
    { key: 'hours', label: 'Opening hours' },
    { key: 'closures', label: 'Closed dates' }
  ] as const;

  // Reset after a save so the next closure starts from an empty form.
  let closureStart = $state('');
  let closureEnd = $state('');
</script>

<PageHeader
  title={branch.name}
  description={`/tour/${branch.slug}`}
  backHref="/branches"
  backLabel="Branches"
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
      <Label for="name">Name</Label>
      <Input id="name" name="name" value={branch.name} required />
    </div>
    <div class="grid gap-2">
      <Label for="slug">Slug</Label>
      <Input id="slug" name="slug" value={branch.slug} required />
    </div>
    <div class="grid gap-2">
      <Label for="address_line1">Address</Label>
      <Input id="address_line1" name="address_line1" value={branch.address_line1} />
    </div>
    <div class="grid gap-2">
      <Label for="address_line2">Address (line 2)</Label>
      <Input id="address_line2" name="address_line2" value={branch.address_line2 ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="city">City</Label>
      <Input id="city" name="city" value={branch.city} />
    </div>
    <div class="grid gap-2">
      <Label for="postal_code">Postal code</Label>
      <Input id="postal_code" name="postal_code" value={branch.postal_code ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="timezone">Time zone</Label>
      <Input id="timezone" name="timezone" value={branch.timezone} />
    </div>
    <div class="grid gap-2">
      <Label for="public_phone">Phone</Label>
      <Input id="public_phone" name="public_phone" value={branch.public_phone ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="public_email">Email</Label>
      <Input id="public_email" name="public_email" value={branch.public_email ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="whatsapp_number">WhatsApp</Label>
      <Input id="whatsapp_number" name="whatsapp_number" value={branch.whatsapp_number ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="website_url">Branch website</Label>
      <Input id="website_url" name="website_url" value={branch.website_url ?? ''} />
    </div>
    <div class="flex flex-col gap-2 pt-6 text-sm">
      <label><input type="checkbox" name="active" checked={branch.active} /> Active</label>
      <label>
        <input type="checkbox" name="bookable" checked={branch.bookable} /> Takes visits
      </label>
      <label>
        <input type="checkbox" name="is_default" checked={branch.is_default} /> Default branch
      </label>
    </div>
    <div class="sm:col-span-2">
      <Button type="submit">Save details</Button>
    </div>
  </form>
{/if}

{#if tab === 'settings'}
  <form method="POST" action="?/settings" use:enhance class="grid max-w-2xl gap-4">
    <div class="grid gap-2">
      <Label for="sender_display_name">Email sender name</Label>
      <Input
        id="sender_display_name"
        name="sender_display_name"
        value={branch.settings?.sender_display_name ?? ''}
      />
    </div>
    <div class="grid gap-2">
      <Label for="reply_to_email">Reply to</Label>
      <Input id="reply_to_email" name="reply_to_email" value={branch.settings?.reply_to_email ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="tour_notification_recipients">
        Registration alerts (one email address per line)
      </Label>
      <Textarea
        id="tour_notification_recipients"
        name="tour_notification_recipients"
        rows={4}
        value={(branch.settings?.tour_notification_recipients ?? []).join('\n')}
      />
    </div>
    <div class="grid gap-2">
      <Label for="tour_intro_html">Visit page introduction</Label>
      <Textarea
        id="tour_intro_html"
        name="tour_intro_html"
        rows={4}
        value={branch.settings?.tour_intro_html ?? ''}
      />
      <p class="text-xs text-muted-foreground">
        Shown to guests on the branch's visit page. Anything outside p, br, strong, em, ul, ol, li,
        h2, h3, h4 and a is removed when saved.
      </p>
    </div>
    <div class="grid gap-2">
      <Label for="arrival_instructions">Arrival instructions</Label>
      <Textarea
        id="arrival_instructions"
        name="arrival_instructions"
        rows={3}
        value={branch.settings?.arrival_instructions ?? ''}
      />
    </div>
    <div class="grid gap-2">
      <Label for="parking_notes">Parking notes</Label>
      <Textarea
        id="parking_notes"
        name="parking_notes"
        rows={3}
        value={branch.settings?.parking_notes ?? ''}
      />
    </div>
    <div><Button type="submit">Save settings</Button></div>
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
          value={toTimeInput(hour?.opens_at_local) || '10:00'}
          class="w-32"
        />
        <span class="text-sm text-muted-foreground">until</span>
        <Input
          type="time"
          name={`day-${day.iso}-closes`}
          value={toTimeInput(hour?.closes_at_local) || '18:00'}
          class="w-32"
        />
      </div>
    {/each}
    <div><Button type="submit">Save opening hours</Button></div>
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
      <Label for="startDate">From</Label>
      <DateField name="startDate" bind:value={closureStart} placeholder="Pick a start date" />
    </div>
    <div class="grid gap-2">
      <Label for="endDate">Until</Label>
      <!-- Cannot end before it starts; blank means a single day. -->
      <DateField
        name="endDate"
        bind:value={closureEnd}
        min={closureStart}
        placeholder="Same day"
      />
    </div>
    <div class="grid gap-2">
      <Label for="public_label">Public label</Label>
      <Input id="public_label" name="public_label" placeholder="Eid holiday" />
    </div>
    <div class="grid gap-2">
      <Label for="reason">Internal note</Label>
      <Input id="reason" name="reason" />
    </div>
    <div class="sm:col-span-2"><Button type="submit">Add closed date</Button></div>
  </form>

  <Table.Root>
    <Table.Header>
      <Table.Row>
        <Table.Head>From</Table.Head>
        <Table.Head>Until</Table.Head>
        <Table.Head>Public label</Table.Head>
        <Table.Head class="text-right">Actions</Table.Head>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {#each branch.closures as closure (closure.id)}
        <Table.Row>
          <Table.Cell>{formatDate(closure.starts_at_local)}</Table.Cell>
          <Table.Cell>{formatDate(closure.ends_at_local)}</Table.Cell>
          <Table.Cell>{closure.public_label ?? '—'}</Table.Cell>
          <Table.Cell class="text-right">
            <form method="POST" action="?/deleteClosure" use:enhance class="inline">
              <input type="hidden" name="closureId" value={closure.id} />
              <Button type="submit" variant="ghost" size="sm">Delete</Button>
            </form>
          </Table.Cell>
        </Table.Row>
      {:else}
        <Table.Row>
          <Table.Cell colspan={4} class="text-center text-sm text-muted-foreground">
            No closed dates yet.
          </Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>
{/if}
