<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import { trackEvent } from '$lib/analytics';
  import { Button, buttonVariants } from '$lib/components/ui/button';
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
  }

  let { sourcePath, heading, lead, context, whatsappText, event }: Props = $props();

  const uid = $props.id();
  const waHref = $derived(whatsappHref(whatsappText));

  let sending = $state(false);
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
        headers: { 'Content-Type': 'application/json' },
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
    }
  }

  const inputClass =
    'rounded-md border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30';
</script>

<div class="grid gap-6 rounded-2xl border border-border bg-background p-6 md:grid-cols-2 md:p-8">
  <div>
    <h2 class="font-display text-2xl font-bold md:text-3xl">{heading}</h2>
    {#if lead}
      <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{lead}</p>
    {/if}
    <a
      href={waHref}
      onclick={() => trackEvent(event, { channel: 'whatsapp' })}
      class={cn(buttonVariants({ variant: 'whatsapp', size: 'lg' }), 'mt-5 w-full sm:w-auto')}
    >
      <MessageCircleIcon size={18} />
      WhatsApp {whatsappDisplay}
    </a>
    <p class="mt-3 text-sm text-muted-foreground">
      Our Bali team replies in English, usually within the day (Bali is 2–3 hours behind the east
      coast).
    </p>
  </div>

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
      <Button type="submit" variant="gold" disabled={sending}>
        {sending ? 'Sending…' : 'Send enquiry'}
      </Button>
    </form>
  {/if}
</div>
