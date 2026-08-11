<script lang="ts">
  import { enhance } from '$app/forms';
  import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
  import UploadIcon from '@lucide/svelte/icons/upload';
  import Trash2Icon from '@lucide/svelte/icons/trash-2';
  import StarIcon from '@lucide/svelte/icons/star';
  import ImagePlusIcon from '@lucide/svelte/icons/image-plus';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';
  import InfoIcon from '@lucide/svelte/icons/info';
  import { toast } from 'svelte-sonner';

  import type { VenuePhoto } from '$lib/api';
  import * as AlertDialog from '$lib/components/ui/alert-dialog';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import VenueForm from '$lib/components/VenueForm.svelte';

  import type { PageData } from './$types';

  type VenueActionData = {
    values?: NonNullable<PageData['values']>;
    errors?: Record<string, string>;
    message?: string;
    uploadMessage?: string;
    storageNotConfigured?: boolean;
    deleteMessage?: string;
    descriptionEn?: string;
  };

  let { data, form }: { data: PageData; form: VenueActionData | null } = $props();

  const values = $derived(form?.values ?? data.values);
  const errors = $derived(form?.errors ?? {});
  const message = $derived(form?.message ?? '');
  const uploadMessage = $derived(form?.uploadMessage ?? '');
  const storageNotConfigured = $derived(form?.storageNotConfigured ?? false);
  const descriptionEn = $derived(form?.descriptionEn ?? data.descriptionEn ?? '');

  let deleteOpen = $state(false);
  let deletingVenue = $state(false);

  const photoSource = (photo: VenuePhoto) =>
    photo.thumbnail_url ??
    photo.thumb_fallback ??
    photo.url ??
    photo.fallback ??
    data.venue?.cover_photo.small_url ??
    '';
</script>

<svelte:head>
  <title>{data.venue?.name ?? 'Venue'} | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title={data.venue?.name ?? 'Venue detail'}
  description={data.venue ? `${data.venue.district}, ${data.venue.city}` : ''}
  backHref="/venues"
  backLabel="Venues"
>
  {#snippet actions()}
    {#if data.venue}
      <StatusBadge status={data.venue.status} />
      <Button
        variant="outline"
        href={`/wedding-venue/${data.venue.city}/${data.venue.slug}`}
        target="_blank"
        rel="noopener"
      >
        <ExternalLinkIcon class="size-4" />
        View public page
      </Button>

      <AlertDialog.Root bind:open={deleteOpen}>
        <AlertDialog.Trigger
          class={buttonVariants({ variant: 'destructive' })}
        >
          <Trash2Icon class="size-4" />
          Delete
        </AlertDialog.Trigger>
        <AlertDialog.Content>
          <AlertDialog.Header>
            <AlertDialog.Title>Delete this venue?</AlertDialog.Title>
            <AlertDialog.Description>
              This permanently removes
              <span class="font-semibold text-foreground">{data.venue.name}</span>
              and its gallery. This action cannot be undone.
            </AlertDialog.Description>
          </AlertDialog.Header>
          <AlertDialog.Footer>
            <AlertDialog.Cancel disabled={deletingVenue}>Cancel</AlertDialog.Cancel>
            <form
              method="POST"
              action="?/deleteVenue"
              use:enhance={() => {
                deletingVenue = true;
                return async ({ result, update }) => {
                  deletingVenue = false;
                  if (result.type === 'redirect') {
                    toast.success('Venue deleted');
                    await update();
                  } else if (result.type === 'failure') {
                    toast.error('Delete failed', {
                      description: (result.data?.deleteMessage as string) ?? 'Please try again.'
                    });
                  }
                };
              }}
            >
              <Button type="submit" variant="destructive" disabled={deletingVenue}>
                {deletingVenue ? 'Deleting…' : 'Delete venue'}
              </Button>
            </form>
          </AlertDialog.Footer>
        </AlertDialog.Content>
      </AlertDialog.Root>
    {/if}
  {/snippet}
</PageHeader>

{#if data.error}
  <div
    class="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
  >
    <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
    <span>{data.error}</span>
  </div>
{:else if data.venue && values}
  <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
    <VenueForm
      {values}
      {errors}
      {message}
      descriptionEnValue={descriptionEn}
      action="?/save"
      submitLabel="Save venue"
    />

    <aside class="space-y-6">
      <Card.Root>
        <Card.Header>
          <div class="flex items-start justify-between gap-3">
            <div>
              <Card.Title>Gallery upload</Card.Title>
              <Card.Description>Uploads are sent to R2 through the API.</Card.Description>
            </div>
            <span
              class="flex size-9 items-center justify-center rounded-md bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400"
            >
              <ImagePlusIcon class="size-5" />
            </span>
          </div>
        </Card.Header>
        <Card.Content class="space-y-4">
          {#if uploadMessage}
            <div
              class={`flex items-start gap-2 rounded-md border px-3 py-2.5 text-sm ${
                storageNotConfigured
                  ? 'border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-300'
                  : 'border-border bg-muted text-muted-foreground'
              }`}
            >
              {#if storageNotConfigured}
                <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
              {:else}
                <InfoIcon class="mt-0.5 size-4 shrink-0" />
              {/if}
              <span>{uploadMessage}</span>
            </div>
          {/if}

          <form
            method="POST"
            action="?/uploadPhoto"
            enctype="multipart/form-data"
            class="space-y-4"
            use:enhance={() => {
              return async ({ result, update }) => {
                await update();
                if (result.type === 'success') {
                  toast.success('Photo uploaded');
                } else if (result.type === 'failure') {
                  toast.error('Upload failed', {
                    description: (result.data?.uploadMessage as string) ?? 'Try again.'
                  });
                }
              };
            }}
          >
            <div class="grid gap-2">
              <Label for="file">Photo</Label>
              <Input id="file" name="file" type="file" accept="image/*" required />
            </div>

            <div class="grid gap-2">
              <Label for="alt_text">Alt text</Label>
              <Input id="alt_text" name="alt_text" value={`${data.venue.name} wedding venue`} />
            </div>

            <div class="grid gap-2">
              <Label for="sort_order">Sort order</Label>
              <Input
                id="sort_order"
                name="sort_order"
                type="number"
                min="0"
                value={data.venue.gallery.length}
              />
            </div>

            <div class="flex items-center gap-2">
              <Checkbox id="set_as_cover" name="set_as_cover" checked={data.venue.gallery.length === 0} />
              <Label for="set_as_cover" class="font-normal">Use as cover photo</Label>
            </div>

            <Button type="submit" class="w-full">
              <UploadIcon class="size-4" />
              Upload photo
            </Button>
          </form>
        </Card.Content>
      </Card.Root>

      <Card.Root>
        <Card.Header>
          <Card.Title>Current photos</Card.Title>
          <Card.Description>{data.venue.gallery.length} gallery records</Card.Description>
        </Card.Header>
        <Card.Content>
          {#if data.venue.gallery.length}
            <ul class="space-y-3">
              {#each data.venue.gallery as photo, index (photo.id ?? photo.storage_key ?? photoSource(photo))}
                <li class="flex gap-3 rounded-md border p-2">
                  <img
                    src={photoSource(photo)}
                    alt={photo.alt_text ?? data.venue.name}
                    class="size-20 shrink-0 rounded-md object-cover"
                    loading="lazy"
                  />
                  <div class="flex min-w-0 flex-1 flex-col">
                    <p class="flex items-center gap-1.5 truncate text-sm font-medium">
                      {#if index === 0}
                        <span
                          class="inline-flex shrink-0 items-center gap-1 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800 dark:bg-amber-950/50 dark:text-amber-400"
                          title="Shown on the public venue listing"
                        >
                          <StarIcon class="size-3" /> Cover
                        </span>
                      {/if}
                      <span class="truncate">{photo.alt_text ?? photo.filename ?? 'Venue photo'}</span>
                    </p>
                    <p class="mt-0.5 text-xs text-muted-foreground">Order {photo.sort_order ?? 0}</p>
                    {#if photo.file_size}
                      <p class="text-xs text-muted-foreground">
                        {Math.round(photo.file_size / 1024)} KB
                      </p>
                    {/if}
                    {#if photo.id !== undefined}
                      <div class="mt-auto flex items-center justify-end gap-1">
                        {#if index > 0}
                          <form
                            method="POST"
                            action="?/setCoverPhoto"
                            use:enhance={() => {
                              return async ({ result, update }) => {
                                await update();
                                if (result.type === 'success') {
                                  toast.success('Cover photo updated');
                                } else if (result.type === 'failure') {
                                  toast.error('Could not set cover', {
                                    description: (result.data?.uploadMessage as string) ?? 'Try again.'
                                  });
                                }
                              };
                            }}
                          >
                            <input type="hidden" name="photo_id" value={photo.id} />
                            <Button type="submit" variant="ghost" size="sm">
                              <StarIcon class="size-4" />
                              Set as cover
                            </Button>
                          </form>
                        {/if}
                      <form
                        method="POST"
                        action="?/deletePhoto"
                        use:enhance={() => {
                          return async ({ result, update }) => {
                            await update();
                            if (result.type === 'success') {
                              toast.success('Photo removed');
                            } else if (result.type === 'failure') {
                              toast.error('Remove failed', {
                                description: (result.data?.uploadMessage as string) ?? 'Try again.'
                              });
                            }
                          };
                        }}
                      >
                        <input type="hidden" name="photo_id" value={photo.id} />
                        <Button
                          type="submit"
                          variant="ghost"
                          size="sm"
                          class="text-muted-foreground hover:text-destructive"
                        >
                          <Trash2Icon class="size-4" />
                          Remove
                        </Button>
                      </form>
                      </div>
                    {/if}
                  </div>
                </li>
              {/each}
            </ul>
          {:else}
            <div
              class="rounded-md border border-dashed bg-muted/40 px-4 py-8 text-center text-sm text-muted-foreground"
            >
              No gallery photos yet.
            </div>
          {/if}
        </Card.Content>
      </Card.Root>
    </aside>
  </div>
{/if}
