<script lang="ts">
  // The real vendor list, not a summary of it. This page used to show three stock
  // photos standing in for categories, with copy admitting it was "a simple public
  // gallery surface ... while detailed vendor CRM remains outside this migration
  // pass". The venue detail page already had the genuine thing -- 35 named partners
  // with their logos and a category filter -- so this renders that same component
  // rather than keeping a second, worse version in step with it.
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import VenueVendors from '$lib/components/venue-detail/VenueVendors.svelte';
  import * as m from '$lib/paraglide/messages';
</script>

<svelte:head>
  <title>{m.vendors_meta_title()}</title>
  <meta name="description" content={m.vendors_meta_description()} />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />
  <!-- h1: here the section is the page, where on a venue page it is one section
       among several. -->
  <VenueVendors heading="h1" />
  <PublicFooter />
</main>
