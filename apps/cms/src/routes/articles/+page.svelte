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

  const articles = $derived(data.articles);
</script>

<svelte:head>
  <title>Articles | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title="Articles"
  description="Open an article to edit its Indonesian and English versions."
>
  {#snippet actions()}
    <Button href="/articles/new">
      <PlusIcon class="size-4" />
      New article
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
  <Card.Root>
    <Card.Content class="p-0">
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.Head>Title</Table.Head>
            <Table.Head>Category</Table.Head>
            <Table.Head>Status</Table.Head>
            <Table.Head>English</Table.Head>
            <Table.Head class="text-right">Actions</Table.Head>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {#each articles as article (article.id)}
            <Table.Row>
              <Table.Cell>
                <a href={`/articles/${article.id}`} class="font-medium hover:underline">
                  {article.title}
                </a>
                <p class="text-xs text-muted-foreground">{article.word_count} words</p>
              </Table.Cell>
              <Table.Cell class="text-sm text-muted-foreground">{article.category}</Table.Cell>
              <Table.Cell><StatusBadge status={article.status} /></Table.Cell>
              <Table.Cell>
                {#if article.has_english}
                  <span class="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
                    <LanguagesIcon class="size-3.5" />
                    Translated
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
                  use:enhance={() => {
                    return async ({ result, update }) => {
                      await update();
                      if (result.type === 'success') toast.success('Article moved to trash');
                      else if (result.type === 'failure') toast.error('Could not delete article');
                    };
                  }}
                >
                  <input type="hidden" name="id" value={article.id} />
                  <Button
                    type="submit"
                    variant="ghost"
                    size="sm"
                    class="text-muted-foreground hover:text-destructive"
                  >
                    Delete
                  </Button>
                </form>
              </Table.Cell>
            </Table.Row>
          {:else}
            <Table.Row>
              <Table.Cell colspan={5} class="py-10 text-center text-sm text-muted-foreground">
                No articles yet.
              </Table.Cell>
            </Table.Row>
          {/each}
        </Table.Body>
      </Table.Root>
    </Card.Content>
  </Card.Root>
{/if}
