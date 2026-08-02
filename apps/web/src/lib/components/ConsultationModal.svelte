<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { cn } from '$lib/utils';
  import { whatsappHref } from '$lib/whatsapp';
  import { page } from '$app/state';

  let { open = $bindable(false) }: { open?: boolean } = $props();

  let sending = $state(false);
  let submitted = $state(false);
  let errorMessage = $state('');

  let waHref = $derived(whatsappHref(m.consult_wa_message()));

  // Reset back to the form whenever the modal is reopened, so a previous
  // success screen does not greet the next visitor.
  $effect(() => {
    if (open) {
      submitted = false;
      errorMessage = '';
    }
  });

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (sending) return;

    const form = event.currentTarget as HTMLFormElement;
    const data = new FormData(form);

    sending = true;
    errorMessage = '';

    try {
      const response = await fetch('/api/contact-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: String(data.get('name') ?? ''),
          phone: String(data.get('phone') ?? ''),
          email: String(data.get('email') ?? '') || undefined,
          message: String(data.get('message') ?? ''),
          source_path: page.url?.pathname ?? '/'
        })
      });

      if (!response.ok) {
        // Keep their input on screen so they can retry, rather than showing a
        // success state for a request that never landed.
        errorMessage = m.consult_error();
        return;
      }

      submitted = true;
      form.reset();
    } catch {
      errorMessage = m.consult_error();
    } finally {
      sending = false;
    }
  }
</script>

<Dialog.Root bind:open>
  <Dialog.Content class="max-w-lg">
    <Dialog.Header>
      <Dialog.Title class="font-display text-xl font-bold">
        {submitted ? m.consult_success_title() : m.consult_title()}
      </Dialog.Title>
      {#if !submitted}
        <Dialog.Description>{m.consult_subtitle()}</Dialog.Description>
      {/if}
    </Dialog.Header>

    {#if submitted}
      <div class="flex flex-col items-center gap-4 py-4 text-center">
        <span
          class="flex size-14 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover"
        >
          <CheckIcon size={28} />
        </span>
        <p class="text-sm leading-6 text-muted-foreground">{m.consult_success_body()}</p>
        <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'w-full')}>
          <MessageCircleIcon size={17} />
          {m.consult_whatsapp_cta()}
        </a>
        <Button variant="ghost" class="w-full" onclick={() => (open = false)}>
          {m.consult_close()}
        </Button>
      </div>
    {:else}
      <form onsubmit={submit} class="grid gap-4">
        <div class="grid gap-1.5">
          <label for="consult-name" class="text-[13px] font-medium">
            {m.consult_name()} <span class="text-destructive" aria-hidden="true">*</span>
          </label>
          <input
            id="consult-name"
            name="name"
            required
            autocomplete="name"
            placeholder={m.consult_name_placeholder()}
            class="rounded-input border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30"
          />
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="grid gap-1.5">
            <label for="consult-phone" class="text-[13px] font-medium">
              {m.consult_whatsapp()} <span class="text-destructive" aria-hidden="true">*</span>
            </label>
            <input
              id="consult-phone"
              name="phone"
              required
              autocomplete="tel"
              placeholder={m.consult_whatsapp_placeholder()}
              class="rounded-input border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30"
            />
          </div>
          <div class="grid gap-1.5">
            <label for="consult-email" class="text-[13px] font-medium">
              {m.consult_email()}
              <span class="text-muted-foreground">({m.consult_optional()})</span>
            </label>
            <input
              id="consult-email"
              name="email"
              type="email"
              autocomplete="email"
              placeholder={m.consult_email_placeholder()}
              class="rounded-input border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30"
            />
          </div>
        </div>

        <div class="grid gap-1.5">
          <label for="consult-message" class="text-[13px] font-medium">
            {m.consult_message()} <span class="text-destructive" aria-hidden="true">*</span>
          </label>
          <textarea
            id="consult-message"
            name="message"
            required
            rows="3"
            placeholder={m.consult_message_placeholder()}
            class="rounded-input border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30"
          ></textarea>
        </div>

        {#if errorMessage}
          <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
        {/if}

        <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending}>
          {sending ? m.consult_sending() : m.consult_submit()}
        </Button>

        <div class="flex items-center gap-3 text-xs uppercase tracking-widest text-muted-foreground">
          <span class="h-px flex-1 bg-border"></span>
          {m.consult_or()}
          <span class="h-px flex-1 bg-border"></span>
        </div>

        <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp', size: 'lg' }), 'w-full')}>
          <MessageCircleIcon size={17} />
          {m.consult_whatsapp_cta()}
        </a>
      </form>
    {/if}
  </Dialog.Content>
</Dialog.Root>
