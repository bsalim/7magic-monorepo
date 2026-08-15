<script lang="ts">
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import { page } from '$app/state';
  import { m } from '$lib/paraglide/messages.js';
  import { whatsappHref } from '$lib/whatsapp';

  /**
   * Persistent WhatsApp entry point, bottom-right on every public page.
   *
   * The number comes from `$lib/whatsapp` rather than being written here: it was
   * once copied into several components and they drifted onto a number nobody
   * owned. One source, one place to change it.
   */

  // The venue detail page owns the bottom edge with its own fixed CTA bar, and
  // already offers WhatsApp in the booking card, the closing band and that bar.
  // A fourth entry point there would overlap the bar rather than help anyone.
  const HIDDEN_ON = ['/wedding-venue/[city]/[slug]'];

  const hidden = $derived(HIDDEN_ON.includes(page.route.id ?? ''));

  // Translated, like the label beside it: a hardcoded Indonesian prefill meant a
  // visitor on /en tapped "Chat on WhatsApp" and WhatsApp opened in Indonesian.
  const href = $derived(whatsappHref(m.wa_float_message()));
</script>

{#if !hidden}
  <a
    {href}
    target="_blank"
    rel="noopener noreferrer"
    class="wa-float"
    aria-label={m.wa_float_aria()}
  >
    <MessageCircleIcon size={26} aria-hidden="true" />
    <span class="wa-float-text">{m.wa_float_label()}</span>
  </a>
{/if}

<style>
  .wa-float {
    /* Below the venue page's own sticky bar (z-70) and any modal, above the
       page content and the sticky header (z-30). */
    position: fixed;
    z-index: 40;
    right: 20px;
    /* Clears the iOS home indicator, which otherwise sits under the button. */
    bottom: calc(20px + env(safe-area-inset-bottom, 0px));
    display: inline-flex;
    align-items: center;
    gap: 0;
    height: 56px;
    width: 56px;
    padding: 0;
    border-radius: 999px;
    background: var(--brand-whatsapp, #128c7e);
    color: #fff;
    box-shadow: 0 8px 24px rgba(18, 140, 126, 0.35);
    transition:
      width 0.28s cubic-bezier(0.4, 0, 0.2, 1),
      gap 0.28s cubic-bezier(0.4, 0, 0.2, 1),
      padding 0.28s cubic-bezier(0.4, 0, 0.2, 1),
      box-shadow 0.2s ease;
    overflow: hidden;
    justify-content: center;
  }

  .wa-float:hover,
  .wa-float:focus-visible {
    box-shadow: 0 12px 32px rgba(18, 140, 126, 0.45);
  }

  .wa-float-text {
    max-width: 0;
    white-space: nowrap;
    font-size: 15px;
    font-weight: 600;
    opacity: 0;
    transition:
      max-width 0.28s cubic-bezier(0.4, 0, 0.2, 1),
      opacity 0.2s ease;
  }

  /* Expands to a labelled pill on hover. Icon-only at rest keeps it out of the
     way of page content; the label removes the guesswork on what it does.
     Pointer-only, because a touch device has no hover and the tap should open
     WhatsApp rather than spend a tap revealing a label. */
  @media (hover: hover) and (pointer: fine) {
    .wa-float:hover,
    .wa-float:focus-visible {
      width: auto;
      gap: 10px;
      padding: 0 22px 0 18px;
    }

    .wa-float:hover .wa-float-text,
    .wa-float:focus-visible .wa-float-text {
      max-width: 220px;
      opacity: 1;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .wa-float,
    .wa-float-text {
      transition: none;
    }
  }
</style>
