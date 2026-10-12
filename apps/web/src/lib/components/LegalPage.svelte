<script lang="ts" module>
  /** A paragraph, or a bullet list, inside a numbered section. */
  export type LegalBlock = { p: string } | { list: string[] };
  export type LegalSection = { id: string; heading: string; blocks: LegalBlock[] };

  export type LegalCopy = {
    meta: { title: string; description: string };
    eyebrow: string;
    title: string;
    updated: string;
    intro: string[];
    contents: string;
    operator: {
      heading: string;
      name: string;
      addressLabel: string;
      otherOfficesLabel: string;
      emailLabel: string;
      whatsappLabel: string;
    };
    sections: LegalSection[];
  };
</script>

<script lang="ts">
  import * as Card from '$lib/components/ui/card';
  import PublicFooter from './PublicFooter.svelte';
  import PublicHeader from './PublicHeader.svelte';
  import SocialMeta from './SocialMeta.svelte';
  import { CONTACT_EMAIL } from '$lib/contact';
  import { OFFICES } from '$lib/offices';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';

  let { copy }: { copy: LegalCopy } = $props();

  // The operator block is assembled from the shared constants rather than
  // written into each document, so the address and contact a reader is told to
  // write to are always the ones the footer and contact page show.
  const otherOffices = [OFFICES.bali.join(', '), OFFICES.singapore.join(', ')];
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
</svelte:head>

<SocialMeta title={copy.meta.title} description={copy.meta.description} />

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />
  <section class="mx-auto max-w-4xl px-5 py-12 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      {copy.eyebrow}
    </p>
    <h1 class="mt-3 text-4xl font-semibold md:text-5xl">{copy.title}</h1>
    <p class="mt-3 text-sm text-muted-foreground">{copy.updated}</p>

    <div class="mt-6 grid gap-4 leading-8 text-muted-foreground">
      {#each copy.intro as paragraph (paragraph)}
        <p>{paragraph}</p>
      {/each}
    </div>

    <Card.Root class="mt-8 gap-0 py-0 shadow-sm">
      <Card.Content class="grid gap-3 p-6 text-sm leading-6 text-muted-foreground">
        <p class="font-display text-base font-semibold text-foreground">{copy.operator.heading}</p>
        <p class="font-semibold text-foreground">{copy.operator.name}</p>
        <p>
          <span class="font-semibold text-foreground">{copy.operator.addressLabel}:</span>
          {OFFICES.jakarta.join(', ')}
        </p>
        <p>
          <span class="font-semibold text-foreground">{copy.operator.otherOfficesLabel}:</span>
          {otherOffices.join('; ')}
        </p>
        <p>
          <span class="font-semibold text-foreground">{copy.operator.emailLabel}:</span>
          <a href={`mailto:${CONTACT_EMAIL}`} class="text-accent-foreground underline">{CONTACT_EMAIL}</a>
        </p>
        <p>
          <span class="font-semibold text-foreground">{copy.operator.whatsappLabel}:</span>
          <a href={whatsappHref('')} class="text-accent-foreground underline">{whatsappDisplay}</a>
        </p>
      </Card.Content>
    </Card.Root>

    <nav class="mt-8" aria-label={copy.contents}>
      <p class="font-display text-sm font-semibold text-foreground">{copy.contents}</p>
      <ol class="mt-3 grid gap-1 text-sm text-accent-foreground sm:grid-cols-2">
        {#each copy.sections as section, index (section.id)}
          <li><a href={`#${section.id}`} class="hover:underline">{index + 1}. {section.heading}</a></li>
        {/each}
      </ol>
    </nav>

    <div class="mt-10 grid gap-10">
      {#each copy.sections as section, index (section.id)}
        <section id={section.id} class="scroll-mt-28">
          <h2 class="font-display text-2xl font-semibold">{index + 1}. {section.heading}</h2>
          <div class="mt-4 grid gap-4 leading-8 text-muted-foreground">
            {#each section.blocks as block, blockIndex (blockIndex)}
              {#if 'p' in block}
                <p>{block.p}</p>
              {:else}
                <ul class="grid gap-2 pl-5 [list-style:disc]">
                  {#each block.list as item (item)}
                    <li>{item}</li>
                  {/each}
                </ul>
              {/if}
            {/each}
          </div>
        </section>
      {/each}
    </div>
  </section>
  <PublicFooter />
</main>
