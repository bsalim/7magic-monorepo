<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import ShieldCheckIcon from '@lucide/svelte/icons/shield-check';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';

  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();
</script>

<svelte:head>
  <title>Login | 7Magic CMS</title>
</svelte:head>

<main class="grid min-h-screen lg:grid-cols-[0.9fr_1.1fr]">
  <!-- Brand panel -->
  <section
    class="relative hidden flex-col justify-between overflow-hidden bg-zinc-950 px-10 py-10 text-white lg:flex"
  >
    <div
      class="pointer-events-none absolute -right-24 -top-24 size-96 rounded-full bg-amber-500/20 blur-3xl"
    ></div>
    <div
      class="pointer-events-none absolute -bottom-32 -left-16 size-96 rounded-full bg-amber-400/10 blur-3xl"
    ></div>

    <div class="relative flex items-center gap-3">
      <img
        src="/img/7magic-logo.png"
        alt="7Magic"
        class="size-12 rounded-md bg-white object-contain p-1.5"
      />
      <div>
        <p class="text-sm font-medium text-white/55">7Magic Wedding</p>
        <h1 class="text-xl font-semibold">CMS Console</h1>
      </div>
    </div>

    <div class="relative max-w-md">
      <div
        class="mb-6 flex size-11 items-center justify-center rounded-lg bg-amber-400 text-zinc-950"
      >
        <ShieldCheckIcon class="size-6" />
      </div>
      <p class="text-sm font-semibold text-amber-300">Admin access</p>
      <h2 class="mt-3 text-4xl font-bold leading-tight">
        Venue, article, and media operations.
      </h2>
      <p class="mt-4 text-sm leading-relaxed text-white/60">
        Manage the wedding-venue catalog, publishing workflow, and gallery media from a single
        console.
      </p>
    </div>

    <p class="relative text-sm text-white/45">Private workspace &middot; Authorized staff only</p>
  </section>

  <!-- Form panel -->
  <section class="flex min-h-screen items-center justify-center bg-muted/40 px-5 py-10">
    <div class="w-full max-w-[420px]">
      <div class="mb-8 lg:hidden">
        <img
          src="/img/7magic-logo.png"
          alt="7Magic"
          class="size-12 rounded-md bg-zinc-950 object-contain p-1.5"
        />
      </div>

      <Card.Root class="shadow-lg">
        <Card.Header>
          <p class="text-sm font-semibold text-brand">7Magic CMS</p>
          <Card.Title class="text-2xl">Sign in</Card.Title>
          <Card.Description>Use your admin credentials to continue.</Card.Description>
        </Card.Header>

        <Card.Content>
          {#if form?.message}
            <div
              class="mb-5 flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2.5 text-sm text-destructive"
            >
              <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
              <span>{form.message}</span>
            </div>
          {/if}

          <form method="POST" class="space-y-4">
            <div class="space-y-2">
              <Label for="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                autocomplete="email"
                placeholder="admin@7magic.test"
                value={form?.email ?? ''}
                required
              />
            </div>

            <div class="space-y-2">
              <Label for="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                autocomplete="current-password"
                placeholder="••••••••"
                required
              />
            </div>

            <Button type="submit" size="lg" class="w-full">
              Sign in
              <ArrowRightIcon class="size-4" />
            </Button>
          </form>
        </Card.Content>
      </Card.Root>
    </div>
  </section>
</main>
