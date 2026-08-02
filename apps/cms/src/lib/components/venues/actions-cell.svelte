<script lang="ts">
  import { enhance } from '$app/forms';
  import { invalidateAll } from '$app/navigation';
  import PencilIcon from '@lucide/svelte/icons/pencil';
  import Trash2Icon from '@lucide/svelte/icons/trash-2';
  import { toast } from 'svelte-sonner';

  import * as AlertDialog from '$lib/components/ui/alert-dialog';
  import { Button, buttonVariants } from '$lib/components/ui/button';

  let { id, name }: { id: number; name: string } = $props();

  let open = $state(false);
  let deleting = $state(false);
</script>

<div class="flex items-center justify-end gap-1">
  <Button href={`/venues/${id}`} variant="ghost" size="icon-sm" aria-label={`Edit ${name}`}>
    <PencilIcon class="size-4" />
  </Button>

  <AlertDialog.Root bind:open>
    <AlertDialog.Trigger
      class={buttonVariants({ variant: 'ghost', size: 'icon-sm' }) +
        ' text-muted-foreground hover:text-destructive'}
      aria-label={`Delete ${name}`}
    >
      <Trash2Icon class="size-4" />
    </AlertDialog.Trigger>
    <AlertDialog.Content>
      <AlertDialog.Header>
        <AlertDialog.Title>Delete venue?</AlertDialog.Title>
        <AlertDialog.Description>
          This permanently removes <span class="font-semibold text-foreground">{name}</span> and its
          gallery. This action cannot be undone.
        </AlertDialog.Description>
      </AlertDialog.Header>
      <AlertDialog.Footer>
        <AlertDialog.Cancel disabled={deleting}>Cancel</AlertDialog.Cancel>
        <form
          method="POST"
          action="/venues?/delete"
          use:enhance={() => {
            deleting = true;
            return async ({ result }) => {
              deleting = false;
              if (result.type === 'success') {
                open = false;
                toast.success('Venue deleted', { description: name });
                await invalidateAll();
              } else if (result.type === 'failure') {
                toast.error('Delete failed', {
                  description: (result.data?.message as string) ?? 'Please try again.'
                });
              } else {
                toast.error('Delete failed', { description: 'Unexpected error.' });
              }
            };
          }}
        >
          <input type="hidden" name="id" value={id} />
          <Button type="submit" variant="destructive" disabled={deleting}>
            {deleting ? 'Deleting…' : 'Delete'}
          </Button>
        </form>
      </AlertDialog.Footer>
    </AlertDialog.Content>
  </AlertDialog.Root>
</div>
