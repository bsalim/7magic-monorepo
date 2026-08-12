<script lang="ts">
  import MailIcon from '@lucide/svelte/icons/mail';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';

  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as m from '$lib/paraglide/messages';
  import { CONTACT_EMAIL } from '$lib/contact';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';

  let { form } = $props();

  // The same deep link the venue pages use, so this page reaches the team through
  // the channel they actually answer on rather than printing a number to copy.
  const waHref = whatsappHref(m.contact_whatsapp_prefill());
</script>

<svelte:head>
  <title>{m.contact_meta_title()}</title>
  <meta name="description" content={m.contact_meta_description()} />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />
  <section class="mx-auto grid max-w-7xl gap-8 px-5 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
    <div>
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {m.contact_eyebrow()}
      </p>
      <h1 class="mt-3 text-4xl font-semibold md:text-5xl">{m.contact_title()}</h1>
      <p class="mt-5 max-w-xl leading-7 text-muted-foreground">{m.contact_intro()}</p>

      <!-- No separate landline: the number printed here was the placeholder
           +62 812-3456-7890, and WhatsApp is the line the team answers. -->
      <div class="mt-8 grid gap-3 text-sm text-muted-foreground">
        <a href={waHref} class="flex items-center gap-2 transition hover:text-foreground">
          <MessageCircleIcon size={17} /> {whatsappDisplay}
        </a>
        <a
          href={`mailto:${CONTACT_EMAIL}`}
          class="flex items-center gap-2 transition hover:text-foreground"
        >
          <MailIcon size={17} /> {CONTACT_EMAIL}
        </a>
        <p class="text-xs">{m.contact_whatsapp_note()}</p>
      </div>

      <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-6')}>
        <MessageCircleIcon size={18} />
        {m.contact_whatsapp_cta()}
      </a>
    </div>

    <Card.Root class="gap-0 py-0 shadow-sm">
      <Card.Content class="p-6">
        <form method="POST">
          {#if form?.lead}
            <div
              class="mb-5 rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm font-semibold text-green-800"
            >
              {form.lead.message}
            </div>
          {:else if form?.error}
            <div
              class="mb-5 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-800"
            >
              {form.error}
            </div>
          {/if}

          <div class="grid gap-4 md:grid-cols-2">
            <div class="grid gap-2">
              <Label for="contact-name">{m.contact_field_name()}</Label>
              <Input id="contact-name" name="name" required />
            </div>
            <div class="grid gap-2">
              <Label for="contact-phone">{m.contact_field_phone()}</Label>
              <Input id="contact-phone" name="phone" />
            </div>
          </div>

          <div class="mt-4 grid gap-2">
            <Label for="contact-email">{m.contact_field_email()}</Label>
            <Input id="contact-email" name="email" type="email" />
          </div>

          <div class="mt-4 grid gap-2">
            <Label for="contact-message">{m.contact_field_message()}</Label>
            <Textarea
              id="contact-message"
              name="message"
              rows={6}
              required
              placeholder={m.contact_message_placeholder()}
            />
          </div>

          <Button type="submit" class="mt-5 font-semibold hover:bg-brand-gold-hover">
            {m.contact_submit()}
          </Button>
        </form>
      </Card.Content>
    </Card.Root>
  </section>
  <PublicFooter />
</main>
