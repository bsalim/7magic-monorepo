<script lang="ts">
  import ImagesIcon from '@lucide/svelte/icons/images';

  import PageHeader from '$lib/components/PageHeader.svelte';
  import VenueForm from '$lib/components/VenueForm.svelte';
  import VenuePhotoDropzone from '$lib/components/venues/VenuePhotoDropzone.svelte';
  import * as Card from '$lib/components/ui/card';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const values = $derived(form?.values ?? data.values);
  const errors = $derived(form?.errors ?? {});
  const message = $derived(form?.message ?? '');
</script>

<svelte:head>
  <title>New Venue | 7Magic CMS</title>
</svelte:head>

<div class="mx-auto max-w-6xl">
  <PageHeader
    title="New venue"
    description="Fill in the venue details and drop gallery photos — everything is saved together when you create the venue."
    backHref="/venues"
    backLabel="Venues"
  />

  <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
    <VenueForm
      {values}
      {errors}
      {message}
      submitLabel="Create venue"
      tempVenueId={data.tempVenueId}
    />

    <aside class="xl:sticky xl:top-24 xl:self-start">
      <Card.Root>
        <Card.Header>
          <Card.Title class="flex items-center gap-2">
            <ImagesIcon class="size-4 text-brand" />
            Gallery photos
          </Card.Title>
          <Card.Description>
            Drag &amp; drop multiple images. They upload immediately and attach to the venue once
            you create it.
          </Card.Description>
        </Card.Header>
        <Card.Content>
          <VenuePhotoDropzone tempVenueId={data.tempVenueId} />
        </Card.Content>
      </Card.Root>
    </aside>
  </div>
</div>
