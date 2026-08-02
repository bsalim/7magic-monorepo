<script lang="ts">
  import AdminShell from '$lib/components/AdminShell.svelte';
  import { Toaster } from '$lib/components/ui/sonner';

  import '../app.css';

  import type { LayoutData } from './$types';

  let { data, children }: { data: LayoutData; children: import('svelte').Snippet } = $props();
</script>

<Toaster richColors closeButton position="top-right" />

{#if data.user}
  <AdminShell user={data.user}>
    {@render children()}
  </AdminShell>
{:else}
  {@render children()}
{/if}
