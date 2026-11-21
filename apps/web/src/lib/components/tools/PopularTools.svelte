<script lang="ts">
  import ArrowRight from '@lucide/svelte/icons/arrow-right';
  import ToolIcon, { type ToolIconName } from './ToolIcon.svelte';

  /**
   * A row of wedding tools for a page that is not about them: the home page
   * shows four under its venue sections, as a way into the hub.
   *
   * The cards are the hub's own (same title, same copy, same icon), passed in
   * already localized, so a tool reads the same wherever it is linked from.
   * On a phone each card lies flat, icon beside text, so four of them do not
   * push the rest of the page a screen and a half down.
   */

  type Tool = { key: ToolIconName; title: string; copy: string; href: string };

  interface Props {
    eyebrow: string;
    title: string;
    body: string;
    tools: Tool[];
    /** The link to the whole hub. */
    allHref: string;
    allLabel: string;
    openLabel: string;
  }

  let { eyebrow, title, body, tools, allHref, allLabel, openLabel }: Props = $props();
</script>

<section class="bg-brand-warm px-5 py-14 lg:px-8">
  <div class="mx-auto max-w-7xl">
    <div class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p class="text-sm font-semibold tracking-widest text-accent-foreground uppercase">{eyebrow}</p>
        <h2 class="mt-3 text-3xl font-semibold md:text-4xl">{title}</h2>
        <p class="mt-3 max-w-2xl text-slate-600">{body}</p>
      </div>
      <a href={allHref} class="inline-flex shrink-0 items-center gap-2 font-semibold text-accent-foreground">
        {allLabel}
        <ArrowRight size={18} aria-hidden="true" />
      </a>
    </div>

    <ul class="mt-8 grid gap-4 sm:grid-cols-2 sm:gap-5 lg:grid-cols-4">
      {#each tools as tool (tool.key)}
        <li class="h-full">
          <a
            href={tool.href}
            class="group flex h-full gap-4 rounded-2xl border border-brand-gold/40 bg-background p-5 text-brand-ink transition hover:-translate-y-0.5 hover:border-brand-gold hover:shadow-[0_24px_60px_-28px_rgba(138,101,36,0.55)] focus-visible:ring-3 focus-visible:ring-ring/40 focus-visible:outline-none sm:flex-col sm:gap-0 sm:p-6"
          >
            <ToolIcon tool={tool.key} size={64} class="size-14 shrink-0 sm:size-16" />
            <div class="flex min-w-0 flex-1 flex-col">
              <h3 class="font-display text-lg leading-snug font-bold sm:mt-5">{tool.title}</h3>
              <p class="mt-1.5 line-clamp-3 text-sm leading-6 text-slate-600 sm:mt-2">{tool.copy}</p>
              <span class="mt-auto flex items-center gap-1.5 pt-3 text-sm font-semibold text-accent-foreground sm:pt-5">
                {openLabel}
                <ArrowRight size={16} aria-hidden="true" class="transition group-hover:translate-x-0.5" />
              </span>
            </div>
          </a>
        </li>
      {/each}
    </ul>
  </div>
</section>
