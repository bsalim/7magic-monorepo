<script lang="ts">
  import StarIcon from '@lucide/svelte/icons/star';

  let { value, size = 14 }: { value: number; size?: number } = $props();

  const count = $derived(Math.max(0, Math.min(5, Math.round(value))));
</script>

<span class="inline-flex items-center gap-0.5" aria-label={`${count} star${count === 1 ? '' : 's'}`}>
  {#each Array.from({ length: 5 }) as _, index (index)}
    <StarIcon
      {size}
      class={index < count ? 'fill-amber-400 text-amber-400' : 'fill-muted text-muted-foreground/30'}
    />
  {/each}
</span>
