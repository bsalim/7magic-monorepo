<script lang="ts">
  import ArticleForm from '$lib/components/ArticleForm.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { ARTICLE_CATEGORIES } from '$lib/articleCategories';

  import type { PageData } from './$types';

  let { data, form }: { data: PageData; form: any } = $props();

  const values = $derived(form?.values ?? data.values);
  const errors = $derived(form?.errors ?? {});
  const message = $derived(form?.message ?? '');
</script>

<svelte:head>
  <title>New article | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title="New article"
  description="Indonesian is required. English is optional and can be added from the language tab."
  backHref="/articles"
  backLabel="Articles"
/>

<ArticleForm
  {values}
  {errors}
  {message}
  categories={ARTICLE_CATEGORIES}
  submitLabel="Create article"
/>
