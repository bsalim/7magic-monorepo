<script lang="ts">
  import LegalPage from '$lib/components/LegalPage.svelte';
  import { getLocale } from '$lib/paraglide/runtime';
  import { privacyCopy } from './content';
</script>

<LegalPage copy={privacyCopy[getLocale()]} />
