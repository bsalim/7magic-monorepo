<script lang="ts">
  import PrenupLanding from '$lib/components/prenup/PrenupLanding.svelte';
  import { getLocale } from '$lib/paraglide/runtime';
  import { m } from '$lib/paraglide/messages.js';
  import { NOTARY, OFFER_PRICE, SEGMENT_IMAGES, baliPrenupCopy } from './content';

  /**
   * Acquisition landing page for the prenuptial agreement service in Bali:
   * /perjanjian-pranikah-bali and /en/prenuptial-agreement-bali, mapped in the
   * paraglide urlPatterns.
   *
   * Indonesian keywords targeted: "perjanjian pranikah bali", "notaris
   * perjanjian pranikah bali", "perjanjian pisah harta bali", "perjanjian kawin
   * campur". English, which carries most of the Bali demand: "prenuptial
   * agreement Bali", "prenup Bali", "postnuptial agreement Indonesia", and the
   * property questions a foreign spouse asks before buying a villa.
   */

  const copy = $derived(baliPrenupCopy(getLocale()));
</script>

<PrenupLanding
  {copy}
  path="/perjanjian-pranikah-bali"
  serviceName={m.service_prenup_bali()}
  areaServed={['Bali']}
  offerPrice={OFFER_PRICE}
  notary={NOTARY}
  segmentImages={SEGMENT_IMAGES}
/>
