<script lang="ts">
  import LockOpenIcon from '@lucide/svelte/icons/lock-open';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button } from '$lib/components/ui/button';
  import { trackEvent } from '$lib/analytics';
  import { m } from '$lib/paraglide/messages.js';
  import { localizeHref } from '$lib/paraglide/runtime';
  import { markUnlocked, normalizeWhatsapp } from '$lib/tools/lead';

  /**
   * The soft gate in front of a tool's extras: email, WhatsApp and consent, once.
   *
   * Shared by every tool, so it knows nothing about mahar: the tool passes its
   * id, the couple's names and whatever inputs it wants the team to see in the
   * lead. What it does own is the flag that spares the couple a second gate on
   * the next tool (`markUnlocked`), and the conversion event.
   *
   * A centred dialog from `sm`, a bottom sheet below it: on a phone the keyboard
   * pushes a centred dialog's fields off screen, while a sheet anchored to the
   * bottom keeps the field being typed in visible.
   */

  type Scalar = string | number | boolean | null;

  interface Props {
    open?: boolean;
    tool: 'mahar';
    title: string;
    description: string;
    names?: string;
    inputs: Record<string, Scalar>;
    /** The unlocalized path, so both language editions report as one tool. */
    sourcePath: string;
    onUnlocked: () => void;
  }

  let {
    open = $bindable(false),
    tool,
    title,
    description,
    names = '',
    inputs,
    sourcePath,
    onUnlocked
  }: Props = $props();

  const uid = $props.id();

  let email = $state('');
  let phone = $state('');
  let consent = $state(false);
  let website = $state('');
  let phoneError = $state('');
  let errorMessage = $state('');
  let sending = $state(false);

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (sending) return;

    const normalized = normalizeWhatsapp(phone);
    if (!normalized) {
      phoneError = m.tools_gate_whatsapp_invalid();
      document.getElementById(`${uid}-phone`)?.focus();
      return;
    }
    phoneError = '';
    errorMessage = '';
    sending = true;

    try {
      const response = await fetch('/api/tool-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool,
          email: email.trim(),
          phone: normalized,
          names: names.trim().slice(0, 120),
          inputs,
          consent,
          source_path: sourcePath,
          website
        })
      });

      if (!response.ok) {
        // Keep what they typed so a retry is one click, not a second form.
        errorMessage = m.tools_gate_error();
        return;
      }

      markUnlocked();
      trackEvent('generate_lead', { tool, source_path: sourcePath });
      open = false;
      onUnlocked();
    } catch {
      errorMessage = m.tools_gate_error();
    } finally {
      sending = false;
    }
  }

  const FIELD =
    'h-11 w-full rounded-md border border-input bg-background px-3 text-base placeholder:text-muted-foreground/60 focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none aria-invalid:border-destructive aria-invalid:ring-destructive/20 md:text-[15px]';
</script>

<Dialog.Root bind:open>
  <Dialog.Content
    class="max-h-[92dvh] overflow-y-auto max-sm:top-auto max-sm:bottom-0 max-sm:max-w-full max-sm:translate-y-0 max-sm:rounded-b-none max-sm:pb-[max(1.5rem,env(safe-area-inset-bottom))] max-sm:data-open:slide-in-from-bottom-8 sm:max-w-md"
  >
    <Dialog.Header>
      <span
        aria-hidden="true"
        class="mb-1 flex size-11 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover"
      >
        <LockOpenIcon size={20} />
      </span>
      <Dialog.Title class="font-display text-xl font-bold">{title}</Dialog.Title>
      <Dialog.Description class="leading-6">{description}</Dialog.Description>
    </Dialog.Header>

    <form onsubmit={submit} class="grid gap-4">
      <div class="grid gap-1.5">
        <label for="{uid}-email" class="text-[13px] font-medium">{m.tools_gate_email()}</label>
        <input
          id="{uid}-email"
          type="email"
          required
          autocomplete="email"
          inputmode="email"
          bind:value={email}
          placeholder={m.tools_gate_email_placeholder()}
          class={FIELD}
        />
      </div>

      <div class="grid gap-1.5">
        <label for="{uid}-phone" class="text-[13px] font-medium">{m.tools_gate_whatsapp()}</label>
        <input
          id="{uid}-phone"
          type="tel"
          required
          autocomplete="tel"
          inputmode="tel"
          bind:value={phone}
          oninput={() => (phoneError = '')}
          placeholder={m.tools_gate_whatsapp_placeholder()}
          aria-invalid={phoneError ? 'true' : undefined}
          aria-describedby={phoneError ? `${uid}-phone-error` : undefined}
          class={FIELD}
        />
        {#if phoneError}
          <p id="{uid}-phone-error" class="text-sm text-destructive">{phoneError}</p>
        {/if}
      </div>

      <!-- Honeypot. Off screen rather than display:none, which some bots skip;
           hidden from assistive tech and the tab order so no person fills it. -->
      <div aria-hidden="true" class="absolute -left-[9999px] h-px w-px overflow-hidden">
        <label for="{uid}-website">{m.tools_gate_honeypot()}</label>
        <input id="{uid}-website" type="text" tabindex="-1" autocomplete="off" bind:value={website} />
      </div>

      <label class="flex items-start gap-3 text-sm leading-6">
        <input
          type="checkbox"
          required
          bind:checked={consent}
          class="mt-1 size-4 shrink-0 accent-brand-gold"
        />
        <span>
          {m.tools_gate_consent()}
          <a
            href={localizeHref('/privacy')}
            target="_blank"
            rel="noopener"
            class="font-medium text-brand-gold-hover underline underline-offset-2"
          >
            {m.tools_gate_consent_link()}</a
          >.
        </span>
      </label>

      {#if errorMessage}
        <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
      {/if}

      <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending}>
        {sending ? m.tools_gate_sending() : m.tools_gate_submit()}
      </Button>
      <p class="text-center text-xs leading-5 text-muted-foreground">{m.tools_gate_note()}</p>
    </form>
  </Dialog.Content>
</Dialog.Root>
