<script lang="ts">
  import { onMount } from 'svelte';
  import LockOpenIcon from '@lucide/svelte/icons/lock-open';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button } from '$lib/components/ui/button';
  import Turnstile from '$lib/components/Turnstile.svelte';
  import { captchaPending, TURNSTILE_HEADER } from '$lib/turnstile';
  import { trackEvent } from '$lib/analytics';
  import { m } from '$lib/paraglide/messages.js';
  import { localizeHref } from '$lib/paraglide/runtime';
  import { markUnlocked, normalizeWhatsapp, rememberEmail, storedEmail, type WeddingTool } from '$lib/tools/lead';

  /**
   * The soft gate in front of a tool's extras: email, WhatsApp and consent, once.
   *
   * Shared by every tool, so it knows nothing about mahar: the tool passes its
   * id, the couple's names and whatever inputs it wants the team to see in the
   * lead. What it does own is the flag that spares the couple a second gate on
   * the next tool (`markUnlocked`), the email it remembers in this browser
   * (`rememberEmail`, offered back the next time a gate opens), and the
   * conversion event.
   *
   * A centred dialog from `sm`, a bottom sheet below it: on a phone the keyboard
   * pushes a centred dialog's fields off screen, while a sheet anchored to the
   * bottom keeps the field being typed in visible.
   *
   * `inline` drops the dialog and renders the same form as a card in the page,
   * for a tool that shows the gate in the place its result will appear.
   */

  type Scalar = string | number | boolean | null;

  interface Props {
    open?: boolean;
    tool: WeddingTool;
    title: string;
    description: string;
    names?: string;
    inputs: Record<string, Scalar>;
    /** Fields the tool's own lead endpoint takes beside the shared ones. */
    extra?: Record<string, unknown>;
    /** A card in the page flow instead of a dialog; `open` is then ignored. */
    inline?: boolean;
    /** The button's label, when "unlock for free" is not what it does. */
    submitLabel?: string;
    /** The line under the button, when "only once" is not the whole story. */
    note?: string;
    /** WhatsApp may be left blank; a number that is typed must still be a real one. */
    phoneOptional?: boolean;
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
    extra = {},
    inline = false,
    submitLabel = '',
    note = '',
    phoneOptional = false,
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
  let captcha = $state<ReturnType<typeof Turnstile> | null>(null);
  let captchaToken = $state('');

  onMount(() => {
    email = storedEmail() ?? '';
  });

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (sending) return;

    const typed = phone.trim();
    const normalized = typed ? normalizeWhatsapp(typed) : null;
    if (typed ? !normalized : !phoneOptional) {
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
        headers: { 'Content-Type': 'application/json', [TURNSTILE_HEADER]: captchaToken },
        body: JSON.stringify({
          tool,
          email: email.trim(),
          phone: normalized,
          names: names.trim().slice(0, 120),
          inputs,
          consent,
          source_path: sourcePath,
          website,
          ...extra
        })
      });

      if (!response.ok) {
        // Keep what they typed so a retry is one click, not a second form.
        errorMessage = m.tools_gate_error();
        return;
      }

      markUnlocked();
      rememberEmail(email);
      trackEvent('generate_lead', { tool, source_path: sourcePath });
      open = false;
      onUnlocked();
    } catch {
      errorMessage = m.tools_gate_error();
    } finally {
      sending = false;
      // Tokens are single-use, so every attempt needs a fresh one.
      captcha?.reset();
    }
  }

  const FIELD =
    'h-11 w-full rounded-md border border-input bg-background px-3 text-base placeholder:text-muted-foreground/60 focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none aria-invalid:border-destructive aria-invalid:ring-destructive/20 md:text-[15px]';
</script>

{#snippet badge()}
  <span
    aria-hidden="true"
    class="mb-1 flex size-11 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover"
  >
    <LockOpenIcon size={20} />
  </span>
{/snippet}

{#snippet fields()}
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
      <label for="{uid}-phone" class="text-[13px] font-medium">
        {m.tools_gate_whatsapp()}
        {#if phoneOptional}
          <span class="font-normal text-muted-foreground">{m.tools_gate_optional()}</span>
        {/if}
      </label>
      <input
        id="{uid}-phone"
        type="tel"
        required={!phoneOptional}
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

    <Turnstile bind:this={captcha} bind:token={captchaToken} />
    <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending || captchaPending(captchaToken)}>
      {sending ? m.tools_gate_sending() : submitLabel || m.tools_gate_submit()}
    </Button>
    <p class="text-center text-xs leading-5 text-muted-foreground">{note || m.tools_gate_note()}</p>
  </form>
{/snippet}

{#if inline}
  <section
    aria-labelledby="{uid}-title"
    class="grid w-full max-w-md gap-4 rounded-2xl border border-brand-warm-deep bg-background p-5 text-foreground shadow-[0_30px_70px_-30px_rgba(138,101,36,0.55)] sm:p-8"
  >
    <div class="grid gap-2">
      {@render badge()}
      <h3 id="{uid}-title" class="font-display text-xl leading-snug font-bold">{title}</h3>
      <p class="text-sm leading-6 text-muted-foreground">{description}</p>
    </div>
    {@render fields()}
  </section>
{:else}
  <Dialog.Root bind:open>
    <Dialog.Content
      class="max-h-[92dvh] overflow-y-auto max-sm:top-auto max-sm:bottom-0 max-sm:max-w-full max-sm:translate-y-0 max-sm:rounded-b-none max-sm:pb-[max(1.5rem,env(safe-area-inset-bottom))] max-sm:data-open:slide-in-from-bottom-8 sm:max-w-md"
    >
      <Dialog.Header>
        {@render badge()}
        <Dialog.Title class="font-display text-xl font-bold">{title}</Dialog.Title>
        <Dialog.Description class="leading-6">{description}</Dialog.Description>
      </Dialog.Header>
      {@render fields()}
    </Dialog.Content>
  </Dialog.Root>
{/if}
