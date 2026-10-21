<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import BaliEnquiry from '$lib/components/bali/BaliEnquiry.svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import { buttonVariants } from '$lib/components/ui/button';
  import { englishPath, siteHref } from '$lib/seo/english-only';
  import {
    breadcrumbList,
    canonicalUrl,
    faqPage,
    graph,
    jsonLdScript,
    organization,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { formatDateRange } from '$lib/tools/bali-format';
  import { cn } from '$lib/utils';
  import { ALL_SOURCES, FACTS, LAST_CHECKED, PATH, type Fact } from './content';

  /**
   * "Is a Bali wedding legal in Australia?" for Australian couples. English only.
   *
   * Every factual sentence comes from `FACTS` in ./content, each with the
   * primary source it was checked against, and renders with that source
   * linked. The guides this page competes with date from 2019 and quote a CNI
   * fee years out of date; being current and sourced is the whole argument.
   *
   * 7Magic's Bali team handles the paperwork (confirmed by the user), so the
   * page closes on that, with no price.
   */

  const path = englishPath(PATH);
  const title = 'Is a Bali Wedding Legal in Australia? (2027 Guide) | 7Magic';
  const description =
    'How to get legally married in Bali as Australians: the religion rule, the Certificate of No Impediment (A$181 in 2026), civil registration, recognition at home, and when to marry at home and celebrate in Bali. Every fact sourced.';

  const answer =
    'Yes, usually. A marriage legally made in Bali is generally recognised in Australia if it was valid in Indonesia and would be valid here. To be legal in Indonesia you must share a recognised religion, hold a religious ceremony, and register it with the civil registry using a Certificate of No Impediment. Many couples marry legally at home and hold a symbolic ceremony in Bali instead.';

  const routes = [
    {
      label: 'Who it suits',
      legal: 'Couples who share a religion recognised in Indonesia and want the wedding day itself to be the legal one.',
      symbolic: 'Couples of different or no religion, same-sex couples, and anyone who wants the simplest paperwork.'
    },
    {
      label: 'Where the legal part happens',
      legal: 'In Bali: religious ceremony, then civil registration.',
      symbolic: 'In Australia, with an Australian celebrant, before or after the trip.'
    },
    {
      label: 'Paperwork in Bali',
      legal: 'CNI from the Australian consulate, notice to the registry 10 working days ahead, documents for both of you.',
      symbolic: 'None for the marriage itself.'
    },
    {
      label: 'Recognised in Australia',
      legal: 'Usually, if valid in Indonesia and valid under Australian law. It cannot be registered here.',
      symbolic: 'Yes: the marriage is Australian.'
    }
  ];

  const timeline = [
    {
      when: '9–12 months before',
      what: 'Decide between a legal wedding in Bali and legal at home with a symbolic ceremony in Bali. If legal in Bali, check that you can marry under one shared religion, and if you are Catholic, ask the parish what it requires.'
    },
    {
      when: '3–4 months before',
      what: 'Gather passports, birth certificates, and divorce or death certificates if either of you was married before. Book a CNI appointment at the Bali Consulate-General for a date inside the three months before the wedding.'
    },
    {
      when: 'At least 10 working days before',
      what: 'Give notice to the civil registry where you will marry, with the CNI and your documents.'
    },
    {
      when: 'The week of the wedding',
      what: 'The religious ceremony, then registration with the civil registry (or the KUA for Muslim couples).'
    },
    {
      when: 'After you are home',
      what: 'Keep the Indonesian marriage certificate safe; it cannot be registered in Australia. Check with your state registry before using it to change your name.'
    }
  ];

  const faqs = [
    { q: 'Is a Bali wedding legally recognised in Australia?', a: answer },
    {
      q: 'Can an Australian celebrant marry us in Bali?',
      a: `No. ${FACTS.celebrant.text}`
    },
    {
      q: 'What is a Certificate of No Impediment and how much does it cost?',
      a: `It is the Australian Government's statement that you are free to marry, and Indonesian registries require it. ${FACTS.cniFee.text} ${FACTS.cniTiming.text}`
    },
    {
      q: 'Do we both need to be the same religion to marry in Bali?',
      a: `Yes, in practice. ${FACTS.religionLaw.text} ${FACTS.sameReligion.text}`
    },
    {
      q: 'Can same-sex couples marry in Bali?',
      a: `No. ${FACTS.sameSexLaw.text} ${FACTS.sameSexAustralia.text} Same-sex couples can marry legally in Australia.`
    },
    {
      q: 'How far ahead do we need to start the paperwork?',
      a: `${FACTS.notice.text} The CNI must be recent: registries do not normally accept one issued more than three months before the wedding.`
    }
  ];

  const crumbs = [
    { name: 'Home', path: '/' },
    { name: 'Bali wedding planning', path: '/bali-wedding-planning' },
    { name: 'Legally married in Bali' }
  ];

  const jsonLd = jsonLdScript(
    graph(
      organization(),
      website(),
      webPageNode({ url: path, name: title, description, locale: 'en', dateModified: LAST_CHECKED }),
      breadcrumbList(crumbs),
      faqPage(faqs)
    )
  );

  const checked = formatDateRange(LAST_CHECKED, LAST_CHECKED).replace(/^\w+ /, '');
  const H2 = 'font-display text-2xl font-bold md:text-3xl';
  const LIST = 'mt-4 grid gap-3 text-[15px] leading-7 text-foreground/80';
</script>

{#snippet fact(item: Fact)}
  {item.text}
  <a
    href={item.source.url}
    target="_blank"
    rel="noopener noreferrer"
    title={item.source.title}
    class="text-xs whitespace-nowrap text-brand-gold-hover underline underline-offset-2">[source]</a
  >
{/snippet}

<svelte:head>
  <title>{title}</title>
  <meta name="description" content={description} />
  <meta
    name="keywords"
    content="is a bali wedding legal in australia, legally married in bali, certificate of no impediment bali, symbolic ceremony bali, getting married in bali legal requirements, australians marrying in bali"
  />
  <link rel="canonical" href={canonicalUrl(path)} />
  {@html jsonLd}
</svelte:head>

<SocialMeta {title} {description} url={path} />

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <article>
    <header class="bg-secondary px-5 pt-10 pb-12 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <p class="text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase">
          Bali weddings · for Australian couples
        </p>
        <h1 class="mt-3 font-display text-3xl leading-tight font-bold md:text-5xl">
          Is a Bali wedding legal in Australia? (2027 guide)
        </h1>
        <p class="mt-3 text-sm text-muted-foreground">
          Last checked <time datetime={LAST_CHECKED}>{checked}</time> against Australian Government and
          Indonesian primary sources. General information, not legal advice.
        </p>
        <p class="mt-6 rounded-xl border-l-4 border-brand-gold bg-background p-5 text-[17px] leading-8">
          {answer}
        </p>
      </div>
    </header>

    <div class="mx-auto grid max-w-3xl grid-cols-1 gap-14 px-5 py-14 lg:px-0">
      <section>
        <h2 class={H2}>Two ways to marry in Bali</h2>
        <p class="mt-3 text-[15px] leading-7 text-foreground/80">{@render fact(FACTS.celebrant)}</p>
        <div class="mt-4 overflow-x-auto">
          <table class="w-full min-w-[560px] text-sm">
            <thead>
              <tr class="text-left text-muted-foreground">
                <th class="py-2 pr-4 font-medium"></th>
                <th class="py-2 pr-4 font-medium">Legal wedding in Bali</th>
                <th class="py-2 font-medium">Legal at home, symbolic in Bali</th>
              </tr>
            </thead>
            <tbody>
              {#each routes as row (row.label)}
                <tr class="border-t border-border align-top">
                  <th scope="row" class="py-2 pr-4 text-left font-medium">{row.label}</th>
                  <td class="py-2 pr-4">{row.legal}</td>
                  <td class="py-2">{row.symbolic}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 class={H2}>What Indonesian law requires</h2>
        <ul class={LIST}>
          <li>{@render fact(FACTS.religionLaw)}</li>
          <li>{@render fact(FACTS.sameReligion)}</li>
          <li>{@render fact(FACTS.muslim)}</li>
          <li>{@render fact(FACTS.notice)}</li>
          <li>{@render fact(FACTS.documentsLaw)}</li>
          <li>{@render fact(FACTS.documentsBadung)}</li>
          <li>{@render fact(FACTS.documentsEmbassy)}</li>
        </ul>
      </section>

      <section>
        <h2 class={H2}>The Certificate of No Impediment</h2>
        <ul class={LIST}>
          <li>{@render fact(FACTS.cniWho)}</li>
          <li>{@render fact(FACTS.cniBooking)}</li>
          <li>{@render fact(FACTS.cniTiming)}</li>
          <li>{@render fact(FACTS.cniFee)}</li>
        </ul>
      </section>

      <section>
        <h2 class={H2}>Will Australia recognise it?</h2>
        <ul class={LIST}>
          <li>{@render fact(FACTS.recognised)}</li>
          <li>{@render fact(FACTS.nameChange)}</li>
          <li>
            {@render fact(FACTS.apostilleIndonesia)}
            {@render fact(FACTS.apostilleAuthority)} If an Australian office asks for an apostilled copy
            of your certificate, that is where it comes from.
          </li>
        </ul>
      </section>

      <section>
        <h2 class={H2}>Same-sex couples</h2>
        <ul class={LIST}>
          <li>{@render fact(FACTS.sameSexLaw)}</li>
          <li>{@render fact(FACTS.sameSexIndonesia)}</li>
          <li>{@render fact(FACTS.sameSexAustralia)}</li>
        </ul>
        <p class="mt-3 text-[15px] leading-7 text-foreground/80">
          A legal marriage is possible in Australia. Talk to us before planning anything public in Bali.
        </p>
      </section>

      <section>
        <h2 class={H2}>Temples and photo shoots</h2>
        <p class="mt-3 text-[15px] leading-7 text-foreground/80">{@render fact(FACTS.temples)}</p>
        <p class="mt-3 text-[15px] leading-7 text-foreground/80">
          A temple as a backdrop is different from a ceremony inside one. Ask your venue or planner
          before booking a shoot at a sacred site.
        </p>
      </section>

      <section>
        <h2 class={H2}>A paperwork timeline</h2>
        <ol class="mt-4 grid gap-4">
          {#each timeline as step, index (step.when)}
            <li class="flex gap-4">
              <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-brand-gold-soft font-semibold text-brand-gold-hover">{index + 1}</span>
              <div>
                <p class="font-semibold">{step.when}</p>
                <p class="mt-1 text-[15px] leading-7 text-foreground/80">{step.what}</p>
              </div>
            </li>
          {/each}
        </ol>
        <a
          href={siteHref('/wedding-tools/bali-wedding-date-planner')}
          class={cn(buttonVariants({ variant: 'outline' }), 'mt-6')}
        >
          Check your date against Nyepi and holy days <ArrowRightIcon size={16} />
        </a>
      </section>

      <section>
        <h2 class={H2}>Questions couples ask</h2>
        <div class="mt-6 grid gap-3">
          {#each faqs as faq (faq.q)}
            <details class="rounded-xl border border-border p-5">
              <summary class="cursor-pointer font-display font-semibold">{faq.q}</summary>
              <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{faq.a}</p>
            </details>
          {/each}
        </div>
      </section>

      <section>
        <h2 class="font-display text-lg font-semibold">Sources</h2>
        <ol class="mt-3 grid list-decimal gap-2 pl-5 text-sm leading-6 text-muted-foreground">
          {#each ALL_SOURCES as source (source.url)}
            <li>
              <a href={source.url} target="_blank" rel="noopener noreferrer" class="underline underline-offset-2 hover:text-foreground">{source.title}</a>
            </li>
          {/each}
        </ol>
      </section>
    </div>
  </article>

  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-5xl">
      <BaliEnquiry
        sourcePath={PATH}
        heading="We handle the paperwork for you"
        lead="Our Bali team books the CNI appointment, prepares the documents and handles the civil registration, so you can get on with the wedding."
        context={['Page: legal guide (legally married in Bali)']}
        whatsappText="Hi 7Magic, we'd like to get legally married in Bali. Can you help with the paperwork?"
        event="Bali Legal Help Requested"
      />
    </div>
  </section>

  <PublicFooter />
</main>
