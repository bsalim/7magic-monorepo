<script lang="ts">
  import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import { ARTICLE_CATEGORIES } from '$lib/articleCategories';
  import ArticleForm from '$lib/components/ArticleForm.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Button } from '$lib/components/ui/button';

  import type { PageData } from './$types';

  type ArticleActionData = {
    values?: NonNullable<PageData['values']>;
    errors?: Record<string, string>;
    message?: string;
  };

  let { data, form }: { data: PageData; form: ArticleActionData | null } = $props();

  const values = $derived(form?.values ?? data.values);
  const errors = $derived(form?.errors ?? {});
  const message = $derived(form?.message ?? '');

  const publicPath = $derived(
    data.article ? `/artikel/${data.article.category_slug}/${data.article.slug}` : ''
  );
</script>

<svelte:head>
  <title>{data.article?.title_id ?? 'Article'} | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title={data.article?.title_id ?? 'Article'}
  description="Indonesian is required. English is optional and falls back when empty."
  backHref="/articles"
  backLabel="Articles"
>
  {#snippet actions()}
    {#if data.article}
      <StatusBadge status={data.article.status} />
      {#if data.article.status === 'published'}
        <Button variant="outline" href={publicPath} target="_blank" rel="noopener">
          <ExternalLinkIcon class="size-4" />
          View public page
        </Button>
      {/if}
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
{:else if data.article && values}
  <ArticleForm
    {values}
    {errors}
    {message}
    action="?/save"
    articleId={data.article.id}
    categories={ARTICLE_CATEGORIES}
  />
{/if}
