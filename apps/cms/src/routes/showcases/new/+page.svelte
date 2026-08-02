<script lang="ts">
  import PageHeader from '$lib/components/PageHeader.svelte';
  import ShowcaseForm, { type ShowcaseValues } from '$lib/components/ShowcaseForm.svelte';

  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();

  const blank: ShowcaseValues = {
    title_id: '',
    title_en: '',
    slug: '',
    body_id: '',
    body_en: '',
    showcase_date: '',
    status: 'draft',
    image_url: '',
    image_storage_key: '',
    image_variants: ''
  };

  const values = $derived(form?.values ?? blank);
</script>

<svelte:head>
  <title>New showcase | 7Magic CMS</title>
</svelte:head>

<PageHeader title="New showcase" description="Add a wedding to the public showcase grid." />

<ShowcaseForm
  {values}
  errors={form?.errors ?? {}}
  message={form?.message ?? ''}
  submitLabel="Create showcase"
/>
