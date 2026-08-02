<script lang="ts">
  import { enhance } from '$app/forms';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';
  import UploadIcon from '@lucide/svelte/icons/upload';
  import { toast } from 'svelte-sonner';

  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';
  import PageHeader from '$lib/components/PageHeader.svelte';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const popup = $derived(data.popup);

  // An upload or a removal sets this override so the preview updates before the
  // record is saved. Everything else derives from the loaded record, so a save
  // that reloads `data` does not leave a stale banner on screen.
  let bannerOverride = $state<{ url: string; key: string } | null>(null);
  const bannerUrl = $derived(bannerOverride?.url ?? popup?.banner_url ?? '');
  const bannerKey = $derived(bannerOverride?.key ?? popup?.banner_key ?? '');
  let uploading = $state(false);

  const FREQUENCIES = [
    { value: 'daily', label: 'Once a day' },
    { value: 'weekly', label: 'Once a week' },
    { value: 'once', label: 'One time only' }
  ];

  $effect(() => {
    if (form?.banner) {
      bannerOverride = { url: form.banner.url, key: form.banner.storage_key };
    }
    if (form?.message) {
      toast.success(form.message);
    }
  });
</script>

<svelte:head>
  <title>Promotion Pop up | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title="Promotion Pop up"
  description="One promotional popup for the public site. Indonesian is required; English falls back to it when left blank."
/>

{#if data.error || !popup}
  <div
    class="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
  >
    <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
    <span>{data.error || 'The promotion popup could not be loaded.'}</span>
  </div>
{:else}
  <div class="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
    <form method="POST" action="?/save" use:enhance class="grid gap-6">
      <input type="hidden" name="banner_url" value={bannerUrl} />
      <input type="hidden" name="banner_key" value={bannerKey} />

      <Card.Root>
        <Card.Header>
          <Card.Title>Content</Card.Title>
          <Card.Description>Shown inside the popup on the public website.</Card.Description>
        </Card.Header>
        <Card.Content class="grid gap-5">
          <div class="grid gap-2">
            <Label for="title_id">Title (Indonesian)</Label>
            <Input id="title_id" name="title_id" value={popup.title_id} placeholder="Promo spesial bulan ini" />
          </div>

          <div class="grid gap-2">
            <Label for="title_en">Title (English)</Label>
            <Input
              id="title_en"
              name="title_en"
              value={popup.title_en ?? ''}
              placeholder="Leave blank to reuse the Indonesian title"
            />
          </div>

          <div class="grid gap-2">
            <Label for="body_id">Body (Indonesian)</Label>
            <Textarea id="body_id" name="body_id" rows={4} value={popup.body_id} />
          </div>

          <div class="grid gap-2">
            <Label for="body_en">Body (English)</Label>
            <Textarea
              id="body_en"
              name="body_en"
              rows={4}
              value={popup.body_en ?? ''}
              placeholder="Leave blank to reuse the Indonesian body"
            />
          </div>
        </Card.Content>
      </Card.Root>

      <Card.Root>
        <Card.Header>
          <Card.Title>Call to action</Card.Title>
          <Card.Description>Optional. The button is hidden when the link is empty.</Card.Description>
        </Card.Header>
        <Card.Content class="grid gap-5 sm:grid-cols-2">
          <div class="grid gap-2">
            <Label for="cta_label_id">Button label (Indonesian)</Label>
            <Input id="cta_label_id" name="cta_label_id" value={popup.cta_label_id ?? ''} placeholder="Lihat paket" />
          </div>
          <div class="grid gap-2">
            <Label for="cta_label_en">Button label (English)</Label>
            <Input id="cta_label_en" name="cta_label_en" value={popup.cta_label_en ?? ''} placeholder="See packages" />
          </div>
          <div class="grid gap-2 sm:col-span-2">
            <Label for="cta_url">Button link</Label>
            <Input id="cta_url" name="cta_url" value={popup.cta_url ?? ''} placeholder="/wedding-venue/search" />
          </div>
        </Card.Content>
      </Card.Root>

      <Card.Root>
        <Card.Header>
          <Card.Title>Appearance</Card.Title>
          <Card.Description>
            How often a visitor sees the popup again after dismissing it. Tracked with a browser
            cookie, so it resets if they clear cookies or use another device.
          </Card.Description>
        </Card.Header>
        <Card.Content class="grid gap-5">
          <div class="grid gap-2">
            <Label for="frequency">Frequency</Label>
            <select
              id="frequency"
              name="frequency"
              value={popup.frequency}
              class="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              {#each FREQUENCIES as option (option.value)}
                <option value={option.value}>{option.label}</option>
              {/each}
            </select>
          </div>

          <label class="flex items-center gap-3 text-sm">
            <input
              type="checkbox"
              name="active"
              checked={popup.active}
              class="size-4 rounded border-input"
            />
            <span>
              <span class="font-medium">Show the popup on the website</span>
              <span class="block text-muted-foreground">
                Turn off to hide it without deleting the content.
              </span>
            </span>
          </label>
        </Card.Content>
        <Card.Footer class="justify-end">
          <Button type="submit">Save popup</Button>
        </Card.Footer>
      </Card.Root>
    </form>

    <div class="grid gap-6">
      <Card.Root>
        <Card.Header>
          <Card.Title>Banner</Card.Title>
          <Card.Description>Uploaded to R2 under <code>packages/</code>.</Card.Description>
        </Card.Header>
        <Card.Content class="grid gap-4">
          {#if bannerUrl}
            <img src={bannerUrl} alt="Promotion banner preview" class="w-full rounded-md border border-border object-cover" />
          {:else}
            <div
              class="flex h-40 items-center justify-center rounded-md border border-dashed border-input text-sm text-muted-foreground"
            >
              No banner uploaded
            </div>
          {/if}

          <form
            method="POST"
            action="?/upload"
            enctype="multipart/form-data"
            use:enhance={() => {
              uploading = true;
              return async ({ update }) => {
                await update({ reset: false });
                uploading = false;
              };
            }}
            class="grid gap-3"
          >
            <Input type="file" name="banner" accept="image/*" required />
            <Button type="submit" variant="outline" disabled={uploading}>
              <UploadIcon class="size-4" />
              {uploading ? 'Uploading…' : 'Upload banner'}
            </Button>
          </form>

          {#if bannerUrl}
            <Button
              type="button"
              variant="ghost"
              onclick={() => (bannerOverride = { url: '', key: '' })}
            >
              Remove banner
            </Button>
          {/if}
        </Card.Content>
      </Card.Root>
    </div>
  </div>
{/if}
