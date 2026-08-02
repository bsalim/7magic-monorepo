<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import * as Card from '$lib/components/ui/card';
  import { m } from '$lib/paraglide/messages.js';
  import type { ArticleCard } from '$lib/api';
  import { articlePath } from '$lib/utils';

  let { article }: { article: ArticleCard } = $props();
</script>

<!--
  The title link is stretched over the whole card with after:inset-0, so the
  image, summary and "read article" affordance are all clickable while the card
  still exposes exactly one link, named by the headline rather than by the
  concatenated card text.
-->
<Card.Root
  class="group relative gap-0 py-0 shadow-sm transition hover:-translate-y-1 hover:shadow-lg focus-within:ring-2 focus-within:ring-ring"
>
  <Card.Content class="p-4">
    <img
      src={article.image_url || '/img/wedding-venue-deal-768.jpg'}
      alt=""
      class="h-40 w-full rounded-card object-cover"
    />
    <p class="mt-4 text-xs font-semibold uppercase tracking-widest text-accent-foreground">
      {article.category}
    </p>
    <h3 class="mt-2 font-display text-xl font-semibold">
      <a
        href={articlePath(article.category, article.slug)}
        class="after:absolute after:inset-0 after:content-[''] focus-visible:outline-none"
      >
        {article.title}
      </a>
    </h3>
    <p class="mt-2 text-sm leading-6 text-muted-foreground">{article.summary}</p>
    <span
      class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-accent-foreground group-hover:gap-3"
    >
      {m.card_read_article()}
      <ArrowRightIcon size={16} />
    </span>
  </Card.Content>
</Card.Root>
