<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import type { Snippet } from 'svelte';
  import { trackEvent } from '$lib/analytics';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import Turnstile from '$lib/components/Turnstile.svelte';
  import { captchaPending, TURNSTILE_HEADER } from '$lib/turnstile';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';
  import { enquiryMessage } from './enquiry';

  /**
   * The close of every Bali-for-Australians page: WhatsApp first, because a
   * couple abroad already lives in it, and a short form for those who would
   * rather be emailed.
   *
   * The page passes what the couple chose (`context`) so the lead arrives
   * already qualified, and its own unlocalized path as `sourcePath`, which is
   * how the team tells which page an Australian lead came from.
   */

  interface Props {
    sourcePath: string;
    heading: string;
    lead?: string;
    /** One line per thing the couple chose on the page; goes first in the lead. */
    context: string[];
    whatsappText: string;
    /** Analytics event name, sent with `{ channel }`. */
    event: string;
    /**
     * `card` is the bordered panel every Bali page has used. `dark` drops the
     * panel for a page that sets the section on a dark band itself, and moves the
     * form into a white card of its own so the fields stay readable.
     */
    tone?: 'card' | 'dark';
    /** Small uppercase line above the heading. */
    eyebrow?: string;
    /** Replaces the heading's text when the page needs markup in it, e.g. an italic word. */
    title?: Snippet;
    /** Replaces the heading's classes, for a page with its own display type. */
    headingClass?: string;
  }

  let {
    sourcePath,
    heading,
    lead,
    context,
    whatsappText,
    event,
    tone = 'card',
    eyebrow,
    title,
    headingClass = 'font-display text-2xl font-bold md:text-3xl'
  }: Props = $props();

  const dark = $derived(tone === 'dark');

  const uid = $props.id();
  const waHref = $derived(whatsappHref(whatsappText));

  let sending = $state(false);
  let captcha = $state<ReturnType<typeof Turnstile> | null>(null);
  let captchaToken = $state('');
  let submitted = $state(false);
  let errorMessage = $state('');

  async function submit(submitEvent: SubmitEvent) {
    submitEvent.preventDefault();
    if (sending) return;

    const form = submitEvent.currentTarget as HTMLFormElement;
    const data = new FormData(form);
    const field = (key: string) => String(data.get(key) ?? '').trim();

    sending = true;
    errorMessage = '';

    try {
      const response = await fetch('/api/contact-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', [TURNSTILE_HEADER]: captchaToken },
        body: JSON.stringify({
          name: field('name'),
          phone: field('phone'),
          email: field('email') || undefined,
          message: enquiryMessage(context, field('notes')),
          source_path: sourcePath
        })
      });

      if (!response.ok) {
        errorMessage = 'That did not send. Try again, or message us on WhatsApp instead.';
        return;
      }

      submitted = true;
      trackEvent(event, { channel: 'form' });
      form.reset();
    } catch {
      errorMessage = 'That did not send. Try again, or message us on WhatsApp instead.';
    } finally {
      sending = false;
      // Tokens are single-use, so every attempt needs a fresh one.
      captcha?.reset();
    }
  }

  const inputClass =
    'rounded-md border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30';
</script>

<div
  class={dark
    ? 'grid gap-10 text-white md:grid-cols-2 md:gap-16'
    : 'grid gap-6 rounded-2xl border border-border bg-background p-6 md:grid-cols-2 md:p-8'}
>
  <div>
    {#if eyebrow}
      <p
        class={cn(
          'mb-4 text-[13px] font-semibold tracking-[0.2em] uppercase',
          dark ? 'text-brand-dark-accent' : 'text-brand-gold-hover'
        )}
      >
        {eyebrow}
      </p>
    {/if}
    <h2 class={headingClass}>
      {#if title}{@render title()}{:else}{heading}{/if}
    </h2>
    {#if lead}
      <p class={cn('mt-3 leading-7', dark ? 'text-[17px] text-white/80' : 'text-[15px] text-muted-foreground')}>
        {lead}
      </p>
    {/if}
    <a
      href={waHref}
      onclick={() => trackEvent(event, { channel: 'whatsapp' })}
      class={cn(
        dark
          ? 'inline-flex h-12 items-center justify-center gap-2 rounded-full bg-brand-dark-accent px-7 font-semibold text-brand-ink hover:bg-brand-dark-accent/90'
          : buttonVariants({ variant: 'whatsapp', size: 'lg' }),
        'mt-6 w-full sm:w-auto'
      )}
    >
      <MessageCircleIcon size={18} />
      WhatsApp {whatsappDisplay}
    </a>
    <p class={cn('mt-3 text-sm', dark ? 'text-white/70' : 'text-muted-foreground')}>
      Our Bali team replies in English, usually within the day (Bali is 2–3 hours behind the east
      coast).
    </p>
  </div>

  <div class={dark ? 'rounded-3xl bg-background p-6 text-foreground md:p-9' : 'contents'}>
  {#if submitted}
    <div class="flex flex-col items-center gap-3 py-8 text-center">
      <span
        class="flex size-12 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover"
      >
        <CheckIcon size={24} />
      </span>
      <p class="font-display text-lg font-semibold">Thank you — that reached us</p>
      <p class="max-w-sm text-[15px] leading-7 text-muted-foreground">
        A planner will reply within one working day.
      </p>
    </div>
  {:else}
    <form onsubmit={submit} class="grid gap-3">
      <div class="grid gap-1.5">
        <label for="{uid}-name" class="text-[13px] font-medium">Your name</label>
        <input id="{uid}-name" name="name" required autocomplete="name" class={inputClass} />
      </div>
      <div class="grid gap-1.5">
        <label for="{uid}-phone" class="text-[13px] font-medium">WhatsApp number</label>
        <input
          id="{uid}-phone"
          name="phone"
          required
          autocomplete="tel"
          placeholder="Include your country code, e.g. +61"
          class={inputClass}
        />
      </div>
      <div class="grid gap-1.5">
        <label for="{uid}-email" class="text-[13px] font-medium">
          Email <span class="text-muted-foreground">(optional)</span>
        </label>
        <input id="{uid}-email" name="email" type="email" autocomplete="email" class={inputClass} />
      </div>
      <div class="grid gap-1.5">
        <label for="{uid}-notes" class="text-[13px] font-medium">Anything else</label>
        <textarea id="{uid}-notes" name="notes" rows="3" class={inputClass}></textarea>
      </div>
      {#if errorMessage}
        <p role="alert" class="text-sm text-destructive">{errorMessage}</p>
      {/if}
      <Turnstile bind:this={captcha} bind:token={captchaToken} />
      <Button type="submit" variant="gold" disabled={sending || captchaPending(captchaToken)}>
        {sending ? 'Sending…' : 'Send enquiry'}
      </Button>
    </form>
  {/if}
  </div>
</div>
