<script lang="ts">
  import LegalPage from '$lib/components/LegalPage.svelte';
  import { getLocale } from '$lib/paraglide/runtime';
  import { termsCopy } from './content';
</script>

<LegalPage copy={termsCopy[getLocale()]} />
