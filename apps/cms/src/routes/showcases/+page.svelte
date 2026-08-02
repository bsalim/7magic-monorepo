<script lang="ts">
  import { enhance } from '$app/forms';
  import LanguagesIcon from '@lucide/svelte/icons/languages';
  import PlusIcon from '@lucide/svelte/icons/plus';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';
  import { toast } from 'svelte-sonner';

  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import * as Table from '$lib/components/ui/table';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';

  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const showcases = $derived(data.showcases);
  const draftCount = $derived(showcases.filter((item) => item.status === 'draft').length);

  // Paged in the browser rather than the API: the admin list is small enough to
  // send whole, but rendering 435 rows at once fires 435 image requests at the
  // r2.dev public domain, which Cloudflare rate-limits hard. A page of 50 keeps
  // the thumbnails loading promptly.
  const PER_PAGE = 50;
  let page = $state(1);
  const lastPage = $derived(Math.max(1, Math.ceil(showcases.length / PER_PAGE)));
  const visible = $derived(showcases.slice((page - 1) * PER_PAGE, page * PER_PAGE));

  // Deleting the final row of the last page would otherwise strand us there.
  $effect(() => {
    if (page > lastPage) page = lastPage;
  });

  function formatDate(value: string | null) {
    if (!value) return '—';
    return new Date(`${value}T00:00:00`).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  }
</script>

<svelte:head>
  <title>Wedding Showcases | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title="Wedding Showcases"
  description="Past weddings shown on the public site. Imported posts arrive as drafts — publish the good ones and delete the rest."
>
  {#snippet actions()}
    <Button href="/showcases/new">
      <PlusIcon class="size-4" />
      New showcase
    </Button>
  {/snippet}
</PageHeader>

{#if data.error}
  <div
    class="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
  >
    <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
    <span>{data.error}</span>
  </div>
{:else}
  <p class="mb-4 text-sm text-muted-foreground">
    {showcases.length} total · {draftCount} awaiting review
  </p>

  <Card.Root>
    <Card.Content class="p-0">
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <!-- Wide enough for the 96px thumbnail plus cell padding, so the
                 column does not squeeze the title beside it. -->
            <Table.Head class="w-28">Photo</Table.Head>
            <Table.Head>Title</Table.Head>
            <Table.Head>Date</Table.Head>
            <Table.Head>Status</Table.Head>
            <Table.Head>English</Table.Head>
            <Table.Head class="text-right">Actions</Table.Head>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {#each visible as showcase (showcase.id)}
            <Table.Row>
              <Table.Cell>
                {#if showcase.image_url}
                  <img
                    src={showcase.image_url}
                    alt=""
                    loading="lazy"
                    class="size-24 rounded-md border border-border object-cover"
                  />
                {:else}
                  <div class="size-24 rounded-md border border-dashed border-border"></div>
                {/if}
              </Table.Cell>
              <Table.Cell>
                <a href={`/showcases/${showcase.id}`} class="font-medium hover:underline">
                  {showcase.title}
                </a>
                <p class="text-xs text-muted-foreground">{showcase.slug}</p>
              </Table.Cell>
              <Table.Cell class="text-sm text-muted-foreground">
                {formatDate(showcase.showcase_date)}
              </Table.Cell>
              <Table.Cell><StatusBadge status={showcase.status} /></Table.Cell>
              <Table.Cell>
                {#if showcase.has_english}
                  <span class="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
                    <LanguagesIcon class="size-4" />
                    Yes
                  </span>
                {:else}
                  <span class="text-sm text-muted-foreground">—</span>
                {/if}
              </Table.Cell>
              <Table.Cell class="text-right">
                <form
                  method="POST"
                  action="?/delete"
                  class="inline"
                  use:enhance={() =>
                    async ({ result, update }) => {
                      if (result.type === 'success') {
                        toast.success('Showcase deleted.');
                      } else if (result.type === 'failure') {
                        toast.error(String(result.data?.deleteMessage ?? 'Delete failed.'));
                      }
                      await update();
                    }}
                >
                  <input type="hidden" name="id" value={showcase.id} />
                  <Button type="submit" variant="ghost" size="sm">Delete</Button>
                </form>
              </Table.Cell>
            </Table.Row>
          {/each}
        </Table.Body>
      </Table.Root>
    </Card.Content>
  </Card.Root>

  {#if lastPage > 1}
    <div class="mt-4 flex items-center justify-between">
      <Button variant="outline" size="sm" disabled={page === 1} onclick={() => (page -= 1)}>
        Previous
      </Button>
      <span class="text-sm text-muted-foreground">
        Page {page} of {lastPage} · showing {visible.length} of {showcases.length}
      </span>
      <Button
        variant="outline"
        size="sm"
        disabled={page === lastPage}
        onclick={() => (page += 1)}
      >
        Next
      </Button>
    </div>
  {/if}
{/if}
