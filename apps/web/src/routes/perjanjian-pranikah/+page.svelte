<script lang="ts">
  import PrenupLanding from '$lib/components/prenup/PrenupLanding.svelte';
  import { getLocale } from '$lib/paraglide/runtime';
  import { m } from '$lib/paraglide/messages.js';
  import { NOTARY, OFFER_PRICE, SEGMENT_IMAGES, prenupCopy } from './content';

  /**
   * Acquisition landing page for the prenuptial agreement service (Jakarta).
   *
   * Bilingual, and one of the pages whose route name differs per locale:
   * /perjanjian-pranikah and /en/prenuptial-agreement, mapped in the paraglide
   * urlPatterns. The service is the same in both -- same notary, same price, same
   * legal references -- so `content.ts` holds a translation, not a second offer.
   * The Bali service is a second offer, at /perjanjian-pranikah-bali, on the
   * same template.
   *
   * Indonesian keywords targeted (Jakarta market research): "perjanjian
   * pranikah", "perjanjian pra nikah", "biaya perjanjian pranikah", "perjanjian
   * pisah harta", "perjanjian perkawinan", "prenup Indonesia", "perjanjian
   * pranikah WNA" / "kawin campur". English: "prenuptial agreement Indonesia",
   * "prenup Jakarta", "separation of property agreement", and the
   * foreign-national variants, which is what the /en page exists to catch.
   */

  const copy = $derived(prenupCopy(getLocale()));
</script>

<PrenupLanding
  {copy}
  path="/perjanjian-pranikah"
  serviceName={m.service_prenup()}
  areaServed={['Jakarta']}
  offerPrice={OFFER_PRICE}
  notary={NOTARY}
  segmentImages={SEGMENT_IMAGES}
/>
