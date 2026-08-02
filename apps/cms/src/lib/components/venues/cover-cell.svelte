<script lang="ts">
  import ImageIcon from '@lucide/svelte/icons/image';

  let { src, alt }: { src?: string | null; alt: string } = $props();
</script>

{#if src}
  <img
    {src}
    {alt}
    loading="lazy"
    class="size-11 rounded-md border object-cover"
  />
{:else}
  <div class="flex size-11 items-center justify-center rounded-md border bg-muted text-muted-foreground">
    <ImageIcon class="size-4" />
  </div>
{/if}
