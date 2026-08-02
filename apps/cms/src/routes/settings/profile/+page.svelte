<script lang="ts">
  import { enhance } from '$app/forms';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';
  import { toast } from 'svelte-sonner';

  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import PageHeader from '$lib/components/PageHeader.svelte';

  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();

  $effect(() => {
    if (form?.success) {
      toast.success(form.message);
    }
  });
</script>

<svelte:head>
  <title>Profile settings | 7Magic CMS</title>
</svelte:head>

<PageHeader
  title="Profile settings"
  description="Change the password you use to sign in to the CMS."
/>

<div class="max-w-xl">
  {#if form && !form.success && form.message}
    <div
      class="mb-6 flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
      <span>{form.message}</span>
    </div>
  {/if}

  <form method="POST" use:enhance>
    <Card.Root>
      <Card.Header>
        <Card.Title>Change password</Card.Title>
        <Card.Description>
          At least 8 characters. Every other device signed in as you is signed out; this one stays
          signed in.
        </Card.Description>
      </Card.Header>
      <Card.Content class="grid gap-5">
        <div class="grid gap-2">
          <Label for="current_password">Current password</Label>
          <Input
            id="current_password"
            name="current_password"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>

        <div class="grid gap-2">
          <Label for="new_password">New password</Label>
          <Input
            id="new_password"
            name="new_password"
            type="password"
            autocomplete="new-password"
            minlength={8}
            required
          />
        </div>

        <div class="grid gap-2">
          <Label for="confirm_password">Confirm new password</Label>
          <Input
            id="confirm_password"
            name="confirm_password"
            type="password"
            autocomplete="new-password"
            minlength={8}
            required
          />
        </div>
      </Card.Content>
      <Card.Footer class="justify-end">
        <Button type="submit">Update password</Button>
      </Card.Footer>
    </Card.Root>
  </form>
</div>
