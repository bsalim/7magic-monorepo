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
  const hourFor = (iso: number) => branch.openingHours.find((row) => row.dayOfWeek === iso);

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
      <Label for="addressLine1">Address</Label>
      <Input id="addressLine1" name="addressLine1" value={branch.addressLine1} />
    </div>
    <div class="grid gap-2">
      <Label for="addressLine2">Address (line 2)</Label>
      <Input id="addressLine2" name="addressLine2" value={branch.addressLine2 ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="city">City</Label>
      <Input id="city" name="city" value={branch.city} />
    </div>
    <div class="grid gap-2">
      <Label for="postalCode">Postal code</Label>
      <Input id="postalCode" name="postalCode" value={branch.postalCode ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="timezone">Time zone</Label>
      <Input id="timezone" name="timezone" value={branch.timezone} />
    </div>
    <div class="grid gap-2">
      <Label for="publicPhone">Phone</Label>
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
      <Label for="websiteUrl">Branch website</Label>
      <Input id="websiteUrl" name="websiteUrl" value={branch.websiteUrl ?? ''} />
    </div>
    <div class="flex flex-col gap-2 pt-6 text-sm">
      <label><input type="checkbox" name="active" checked={branch.active} /> Active</label>
      <label>
        <input type="checkbox" name="bookable" checked={branch.bookable} /> Takes visits
      </label>
      <label>
        <input type="checkbox" name="isDefault" checked={branch.isDefault} /> Default branch
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
      <Label for="senderDisplayName">Email sender name</Label>
      <Input
        id="senderDisplayName"
        name="senderDisplayName"
        value={branch.settings?.senderDisplayName ?? ''}
      />
    </div>
    <div class="grid gap-2">
      <Label for="replyToEmail">Reply to</Label>
      <Input id="replyToEmail" name="replyToEmail" value={branch.settings?.replyToEmail ?? ''} />
    </div>
    <div class="grid gap-2">
      <Label for="tourNotificationRecipients">
        Registration alerts (one email address per line)
      </Label>
      <Textarea
        id="tourNotificationRecipients"
        name="tourNotificationRecipients"
        rows={4}
        value={(branch.settings?.tourNotificationRecipients ?? []).join('\n')}
      />
    </div>
    <div class="grid gap-2">
      <Label for="tourIntroHtml">Visit page introduction</Label>
      <Textarea
        id="tourIntroHtml"
        name="tourIntroHtml"
        rows={4}
        value={branch.settings?.tourIntroHtml ?? ''}
      />
      <p class="text-xs text-muted-foreground">
        Shown to guests on the branch's visit page. Anything outside p, br, strong, em, ul, ol, li,
        h2, h3, h4 and a is removed when saved.
      </p>
    </div>
    <div class="grid gap-2">
      <Label for="arrivalInstructions">Arrival instructions</Label>
      <Textarea
        id="arrivalInstructions"
        name="arrivalInstructions"
        rows={3}
        value={branch.settings?.arrivalInstructions ?? ''}
      />
    </div>
    <div class="grid gap-2">
      <Label for="parkingNotes">Parking notes</Label>
      <Textarea
        id="parkingNotes"
        name="parkingNotes"
        rows={3}
        value={branch.settings?.parkingNotes ?? ''}
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
          value={toTimeInput(hour?.opensAtLocal) || '10:00'}
          class="w-32"
        />
        <span class="text-sm text-muted-foreground">until</span>
        <Input
          type="time"
          name={`day-${day.iso}-closes`}
          value={toTimeInput(hour?.closesAtLocal) || '18:00'}
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
      <Label for="publicLabel">Public label</Label>
      <Input id="publicLabel" name="publicLabel" placeholder="Eid holiday" />
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
          <Table.Cell>{formatDate(closure.startsAtLocal)}</Table.Cell>
          <Table.Cell>{formatDate(closure.endsAtLocal)}</Table.Cell>
          <Table.Cell>{closure.publicLabel ?? '—'}</Table.Cell>
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
