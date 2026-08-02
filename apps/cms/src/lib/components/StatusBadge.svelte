<script lang="ts">
  import { Badge } from '$lib/components/ui/badge';

  let { status }: { status: string | boolean } = $props();

  const normalized = $derived(String(status).toLowerCase());
  const label = $derived(typeof status === 'boolean' ? (status ? 'Yes' : 'No') : status);

  // Tailwind utility classes per state — soft, accessible tones.
  const className = $derived(
    normalized === 'active' || normalized === 'published' || normalized === 'true'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-400'
      : normalized === 'draft'
        ? 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-400'
        : normalized === 'archived'
          ? 'border-border bg-muted text-muted-foreground'
          : 'border-border bg-background text-foreground'
  );
</script>

<Badge variant="outline" class={`capitalize ${className}`}>{label}</Badge>
