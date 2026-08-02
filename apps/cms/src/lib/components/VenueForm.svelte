<script lang="ts">
  import { untrack } from 'svelte';
  import { enhance } from '$app/forms';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Select from '$lib/components/ui/select';
  import * as Tabs from '$lib/components/ui/tabs';
  import { Textarea } from '$lib/components/ui/textarea';

  type VenueValues = {
    name: string;
    slug: string;
    city: string;
    district: string;
    address: string;
    stars: number;
    description: string;
    price_start_from: number | null;
    price_for_total_pax: number;
    status: 'draft' | 'active' | 'archived';
  };

  type VenueErrors = Partial<Record<keyof VenueValues, string>>;

  let {
    values,
    errors = {},
    message = '',
    submitLabel = 'Save venue',
    cancelHref = '/venues',
    action = '',
    tempVenueId = '',
    descriptionEnValue = ''
  }: {
    values: VenueValues;
    errors?: VenueErrors;
    message?: string;
    submitLabel?: string;
    cancelHref?: string;
    action?: string;
    tempVenueId?: string;
    descriptionEnValue?: string;
  } = $props();

  let status = $state<VenueValues['status']>(untrack(() => values.status));
  let descriptionEn = $state(untrack(() => descriptionEnValue));
  let submitting = $state(false);

  const statusLabels: Record<VenueValues['status'], string> = {
    draft: 'Draft',
    active: 'Active',
    archived: 'Archived'
  };

  // Keep the local status in sync when the bound values change after a save.
  $effect(() => {
    status = values.status;
  });
</script>

{#snippet fieldError(text: string | undefined)}
  {#if text}
    <p class="text-xs font-medium text-destructive">{text}</p>
  {/if}
{/snippet}

<form method="POST" {action} class="space-y-6" use:enhance={() => {
  submitting = true;
  return async ({ update }) => {
    await update();
    submitting = false;
  };
}}>
  {#if message}
    <div
      class="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
      <span>{message}</span>
    </div>
  {/if}

  <input type="hidden" name="status" value={status} />
  {#if tempVenueId}
    <input type="hidden" name="temp_venue_id" value={tempVenueId} />
  {/if}

  <Card.Root>
    <Card.Header>
      <Card.Title>Identity</Card.Title>
      <Card.Description>Name, slug, and location details.</Card.Description>
    </Card.Header>
    <Card.Content class="grid gap-5 md:grid-cols-2">
      <div class="grid gap-2">
        <Label for="name">Venue name</Label>
        <Input id="name" name="name" value={values.name} required aria-invalid={!!errors.name} />
        {@render fieldError(errors.name)}
      </div>

      <div class="grid gap-2">
        <Label for="slug">Slug</Label>
        <Input id="slug" name="slug" value={values.slug} required aria-invalid={!!errors.slug} />
        {@render fieldError(errors.slug)}
      </div>

      <div class="grid gap-2">
        <Label for="city">City</Label>
        <Input id="city" name="city" value={values.city} required aria-invalid={!!errors.city} />
        {@render fieldError(errors.city)}
      </div>

      <div class="grid gap-2">
        <Label for="district">District</Label>
        <Input
          id="district"
          name="district"
          value={values.district}
          required
          aria-invalid={!!errors.district}
        />
        {@render fieldError(errors.district)}
      </div>

      <div class="grid gap-2 md:col-span-2">
        <Label for="address">Address</Label>
        <Input
          id="address"
          name="address"
          value={values.address}
          required
          aria-invalid={!!errors.address}
        />
        {@render fieldError(errors.address)}
      </div>
    </Card.Content>
  </Card.Root>

  <Card.Root>
    <Card.Header>
      <Card.Title>Package</Card.Title>
      <Card.Description>Commercial fields shown across the venue catalog.</Card.Description>
    </Card.Header>
    <Card.Content class="space-y-5">
      <div class="grid gap-5 md:grid-cols-4">
        <div class="grid gap-2">
          <Label for="stars">Stars</Label>
          <Input
            id="stars"
            name="stars"
            type="number"
            min="1"
            max="5"
            value={values.stars}
            required
            aria-invalid={!!errors.stars}
          />
          {@render fieldError(errors.stars)}
        </div>

        <div class="grid gap-2">
          <Label for="price_start_from">Starting price</Label>
          <Input
            id="price_start_from"
            name="price_start_from"
            type="number"
            min="0"
            value={values.price_start_from ?? ''}
            aria-invalid={!!errors.price_start_from}
          />
          {@render fieldError(errors.price_start_from)}
        </div>

        <div class="grid gap-2">
          <Label for="price_for_total_pax">Package pax</Label>
          <Input
            id="price_for_total_pax"
            name="price_for_total_pax"
            type="number"
            min="0"
            value={values.price_for_total_pax}
            aria-invalid={!!errors.price_for_total_pax}
          />
          {@render fieldError(errors.price_for_total_pax)}
        </div>

        <div class="grid gap-2">
          <Label>Status</Label>
          <Select.Root type="single" bind:value={status}>
            <Select.Trigger class="w-full">{statusLabels[status]}</Select.Trigger>
            <Select.Content>
              <Select.Item value="draft">Draft</Select.Item>
              <Select.Item value="active">Active</Select.Item>
              <Select.Item value="archived">Archived</Select.Item>
            </Select.Content>
          </Select.Root>
        </div>
      </div>

      <div class="grid gap-2">
        <Label for="description">Description</Label>
        <Tabs.Root value="id">
          <Tabs.List>
            <Tabs.Trigger value="id">Indonesian</Tabs.Trigger>
            <Tabs.Trigger value="en">English</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="id">
            <Textarea
              id="description"
              name="description"
              rows={7}
              value={values.description}
              required
              aria-invalid={!!errors.description}
            />
            {@render fieldError(errors.description)}
          </Tabs.Content>
          <Tabs.Content value="en">
            <Textarea
              id="description_en"
              name="description_en"
              rows={7}
              bind:value={descriptionEn}
              placeholder="Leave empty to show the Indonesian description."
            />
            {#if !descriptionEn.trim()}
              <p class="mt-2 text-sm text-muted-foreground">
                Empty — the public site falls back to the Indonesian description.
              </p>
            {/if}
          </Tabs.Content>
        </Tabs.Root>
      </div>
    </Card.Content>
  </Card.Root>

  <div class="flex flex-wrap items-center justify-end gap-3">
    <Button href={cancelHref} variant="outline" type="button">Cancel</Button>
    <Button type="submit" disabled={submitting}>{submitting ? 'Saving…' : submitLabel}</Button>
  </div>
</form>
