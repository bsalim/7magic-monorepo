<script lang="ts">
  import { untrack } from 'svelte';
  import { enhance } from '$app/forms';
  import ImageIcon from '@lucide/svelte/icons/image';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Select from '$lib/components/ui/select';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as Tabs from '$lib/components/ui/tabs';

  export type ShowcaseValues = {
    title_id: string;
    title_en: string;
    slug: string;
    body_id: string;
    body_en: string;
    showcase_date: string;
    status: 'draft' | 'published' | 'archived';
    image_url: string;
    image_storage_key: string;
    image_variants: string;
  };

  let {
    values,
    errors = {},
    message = '',
    submitLabel = 'Save showcase',
    cancelHref = '/showcases',
    action = ''
  }: {
    values: ShowcaseValues;
    errors?: Partial<Record<keyof ShowcaseValues, string>>;
    message?: string;
    submitLabel?: string;
    cancelHref?: string;
    action?: string;
  } = $props();

  let status = $state<ShowcaseValues['status']>(untrack(() => values.status));
  let imageUrl = $state(untrack(() => values.image_url));
  let imageKey = $state(untrack(() => values.image_storage_key));
  let imageVariants = $state(untrack(() => values.image_variants));
  let uploading = $state(false);
  let uploadError = $state('');
  let submitting = $state(false);

  const statusLabels: Record<ShowcaseValues['status'], string> = {
    draft: 'Draft',
    published: 'Published',
    archived: 'Archived'
  };

  async function uploadImage(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    uploading = true;
    uploadError = '';
    try {
      const body = new FormData();
      body.set('file', file);
      const response = await fetch('/showcases/image-upload', { method: 'POST', body });
      if (!response.ok) {
        uploadError = 'Upload failed. Try again.';
        return;
      }
      const result = (await response.json()) as {
        url: string;
        storage_key: string;
        variants: unknown;
      };
      imageUrl = result.url;
      imageKey = result.storage_key;
      imageVariants = JSON.stringify(result.variants ?? {});
    } catch {
      uploadError = 'Upload failed. Try again.';
    } finally {
      uploading = false;
      input.value = '';
    }
  }
</script>

<form
  method="POST"
  {action}
  use:enhance={() => {
    submitting = true;
    return async ({ update }) => {
      await update({ reset: false });
      submitting = false;
    };
  }}
  class="grid gap-6"
>
  {#if message}
    <div
      class="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
      <span>{message}</span>
    </div>
  {/if}

  <Card.Root>
    <Card.Header>
      <Card.Title>Photo</Card.Title>
      <Card.Description>Stored on R2 with responsive sizes generated for you.</Card.Description>
    </Card.Header>
    <Card.Content class="grid gap-4">
      {#if imageUrl}
        <img
          src={imageUrl}
          alt="Showcase preview"
          class="h-56 w-full max-w-md rounded-md border border-border object-cover"
        />
      {:else}
        <div
          class="flex h-56 w-full max-w-md items-center justify-center rounded-md border border-dashed border-border text-muted-foreground"
        >
          <ImageIcon class="size-8" />
        </div>
      {/if}

      <div class="grid gap-1.5">
        <Label for="showcase-image">{imageUrl ? 'Replace photo' : 'Upload photo'}</Label>
        <input
          id="showcase-image"
          type="file"
          accept="image/*"
          onchange={uploadImage}
          disabled={uploading}
          class="text-sm file:mr-3 file:rounded-md file:border file:border-border file:bg-muted file:px-3 file:py-1.5 file:text-sm"
        />
        {#if uploading}
          <p class="text-xs text-muted-foreground">Uploading…</p>
        {/if}
        {#if uploadError}
          <p class="text-xs text-destructive">{uploadError}</p>
        {/if}
      </div>

      <input type="hidden" name="image_url" value={imageUrl} />
      <input type="hidden" name="image_storage_key" value={imageKey} />
      <input type="hidden" name="image_variants" value={imageVariants} />
    </Card.Content>
  </Card.Root>

  <Card.Root>
    <Card.Header>
      <Card.Title>Details</Card.Title>
    </Card.Header>
    <Card.Content class="grid gap-4 sm:grid-cols-2">
      <div class="grid gap-1.5">
        <Label for="showcase-date">Showcase date</Label>
        <Input id="showcase-date" name="showcase_date" type="date" value={values.showcase_date} />
        {#if errors.showcase_date}
          <p class="text-xs text-destructive">{errors.showcase_date}</p>
        {/if}
      </div>

      <div class="grid gap-1.5">
        <Label for="showcase-slug">Slug</Label>
        <Input id="showcase-slug" name="slug" value={values.slug} placeholder="wedding-showcase-…" />
        {#if errors.slug}
          <p class="text-xs text-destructive">{errors.slug}</p>
        {/if}
      </div>

      <div class="grid gap-1.5">
        <Label for="showcase-status">Status</Label>
        <Select.Root type="single" bind:value={status}>
          <Select.Trigger id="showcase-status">{statusLabels[status]}</Select.Trigger>
          <Select.Content>
            <Select.Item value="draft">Draft</Select.Item>
            <Select.Item value="published">Published</Select.Item>
            <Select.Item value="archived">Archived</Select.Item>
          </Select.Content>
        </Select.Root>
        <input type="hidden" name="status" value={status} />
      </div>
    </Card.Content>
  </Card.Root>

  <Card.Root>
    <Card.Header>
      <Card.Title>Content</Card.Title>
      <Card.Description>
        Indonesian is required. English is optional — leave it blank and the site falls back to
        Indonesian.
      </Card.Description>
    </Card.Header>
    <Card.Content>
      <Tabs.Root value="id">
        <Tabs.List>
          <Tabs.Trigger value="id">Indonesian</Tabs.Trigger>
          <Tabs.Trigger value="en">English</Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="id" class="grid gap-4 pt-4">
          <div class="grid gap-1.5">
            <Label for="title-id">Title <span class="text-destructive">*</span></Label>
            <Input id="title-id" name="title_id" value={values.title_id} required />
            {#if errors.title_id}
              <p class="text-xs text-destructive">{errors.title_id}</p>
            {/if}
          </div>
          <div class="grid gap-1.5">
            <Label for="body-id">Body</Label>
            <Textarea id="body-id" name="body_id" rows={8} value={values.body_id} />
          </div>
        </Tabs.Content>

        <Tabs.Content value="en" class="grid gap-4 pt-4">
          <div class="grid gap-1.5">
            <Label for="title-en">Title</Label>
            <Input id="title-en" name="title_en" value={values.title_en} />
          </div>
          <div class="grid gap-1.5">
            <Label for="body-en">Body</Label>
            <Textarea id="body-en" name="body_en" rows={8} value={values.body_en} />
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </Card.Content>
  </Card.Root>

  <div class="flex items-center gap-3">
    <Button type="submit" disabled={submitting || uploading}>
      {submitting ? 'Saving…' : submitLabel}
    </Button>
    <Button href={cancelHref} variant="ghost">Cancel</Button>
  </div>
</form>
