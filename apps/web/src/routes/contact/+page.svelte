<script lang="ts">
  import MailIcon from '@lucide/svelte/icons/mail';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import PhoneIcon from '@lucide/svelte/icons/phone';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';

  let { form } = $props();
</script>

<svelte:head>
  <title>Contact 7Magic Wedding</title>
  <meta name="description" content="Contact 7Magic to ask about wedding venue packages and vendor recommendations." />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />
  <section class="mx-auto grid max-w-7xl gap-8 px-5 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
    <div>
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Contact</p>
      <h1 class="mt-3 text-4xl font-semibold md:text-5xl">Ask about your wedding shortlist</h1>
      <p class="mt-5 max-w-xl leading-7 text-muted-foreground">
        Share your city, guest count, preferred month, and venue style. The team will help narrow
        packages before you visit.
      </p>
      <div class="mt-8 grid gap-3 text-sm text-muted-foreground">
        <p class="flex items-center gap-2"><PhoneIcon size={17} /> +62 812-3456-7890</p>
        <p class="flex items-center gap-2"><MailIcon size={17} /> hello@7magic.id</p>
        <p class="flex items-center gap-2">
          <MessageCircleIcon size={17} /> WhatsApp replies during business hours
        </p>
      </div>
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
              <Label for="contact-name">Name</Label>
              <Input id="contact-name" name="name" required />
            </div>
            <div class="grid gap-2">
              <Label for="contact-phone">Phone</Label>
              <Input id="contact-phone" name="phone" />
            </div>
          </div>

          <div class="mt-4 grid gap-2">
            <Label for="contact-email">Email</Label>
            <Input id="contact-email" name="email" type="email" />
          </div>

          <div class="mt-4 grid gap-2">
            <Label for="contact-message">Message</Label>
            <Textarea
              id="contact-message"
              name="message"
              rows={6}
              required
              placeholder="City, guest count, target month, and package questions"
            />
          </div>

          <Button type="submit" class="mt-5 font-semibold hover:bg-brand-gold-hover">
            Send inquiry
          </Button>
        </form>
      </Card.Content>
    </Card.Root>
  </section>
  <PublicFooter />
</main>
