<script lang="ts">
  import { toast } from 'svelte-sonner';

  import PageHeader from '$lib/components/PageHeader.svelte';
  import ShowcaseForm, { type ShowcaseValues } from '$lib/components/ShowcaseForm.svelte';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const showcase = $derived(data.showcase);

  const fromServer = $derived<ShowcaseValues>({
    title_id: showcase.title_id,
    title_en: showcase.title_en,
    slug: showcase.slug,
    body_id: showcase.body_id,
    body_en: showcase.body_en,
    showcase_date: showcase.showcase_date ?? '',
    status: showcase.status as ShowcaseValues['status'],
    image_url: showcase.image_url ?? '',
    image_storage_key: showcase.image_storage_key ?? '',
    image_variants: ''
  });

  const values = $derived(form?.values ?? fromServer);

  $effect(() => {
    if (form?.saved) {
      toast.success('Showcase saved.');
    }
  });
</script>

<svelte:head>
  <title>{showcase.title_id} | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title="Edit showcase"
  description={showcase.source_ref
    ? `Imported from ${showcase.source_ref}`
    : 'Update this showcase.'}
  backHref="/showcases"
  backLabel="Wedding Showcases"
/>

<ShowcaseForm {values} errors={form?.errors ?? {}} message={form?.message ?? ''} action="?/save" />
