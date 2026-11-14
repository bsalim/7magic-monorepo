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
  import { whatsappHref } from '$lib/whatsapp';
  import { ALL_SOURCES, FACTS, LAST_CHECKED, PATH, type Fact } from './content';

  /**
   * "Is a Bali wedding legal in Australia?" for Australian couples. English only.
   *
   * Every factual sentence comes from `FACTS` in ./content, each with the
   * primary source it was checked against, and renders with that source
   * linked. The guides this page competes with date from 2019 and quote a CNI
   * fee years out of date; being current and sourced is the whole argument, so
   * the redesign keeps every source link even where the mock-up dropped them.
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

  // The hero's short answer, beside the large "Usually, yes." `answer` above is
  // the full version, kept for the FAQ and its structured data.
  const heroAnswer =
    'Australia generally recognises a Bali marriage that was valid under Indonesian law and would also have been valid at home. That takes a shared religion, a religious ceremony and civil registration, so many couples sign the papers in Australia and hold a symbolic ceremony in Bali.';

  const waText = "Hi 7Magic, we'd like to get legally married in Bali. Can you help with the paperwork?";

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

  // Each repeats a number from FACTS; none is new.
  const stats = [
    { n: 'A$181', unit: '', text: 'Certificate of No Impediment fee in 2026 (Rp2,232,000)' },
    { n: '10', unit: 'working days', text: 'Minimum notice to the civil registry before the wedding' },
    { n: '3', unit: 'months', text: 'Oldest a CNI can generally be on your wedding day' }
  ];

  const options: {
    n: string;
    kind: 'legal' | 'symbolic';
    heading: string;
    img: string;
    alt: string;
    position: string;
    dark: boolean;
  }[] = [
    {
      n: '01',
      kind: 'legal',
      heading: 'Legal wedding in Bali',
      img: '/img/legal-bali/temple-couple.jpg',
      alt: 'Couple in traditional Balinese wedding dress sharing a frangipani flower at a temple',
      position: 'object-[50%_28%]',
      dark: false
    },
    {
      n: '02',
      kind: 'symbolic',
      heading: 'Legal at home, symbolic in Bali',
      img: '/img/legal-bali/beach-ceremony.jpg',
      alt: 'Beach wedding ceremony with guests seated either side of a petal-strewn aisle, facing an arch by the sea',
      position: 'object-center',
      dark: true
    }
  ];

  // Short titles for scanning; the sentence beside each is the sourced fact.
  const requirements: { title: string; fact: Fact }[] = [
    { title: 'Religious validity', fact: FACTS.religionLaw },
    { title: 'Shared religion', fact: FACTS.sameReligion },
    { title: 'Registration', fact: FACTS.muslim },
    { title: 'Notice', fact: FACTS.notice },
    { title: "Foreign partner's documents", fact: FACTS.documentsLaw },
    { title: 'Badung registry', fact: FACTS.documentsBadung },
    { title: 'Birth certificates', fact: FACTS.documentsEmbassy }
  ];

  // `figure` repeats a number already in the fact beside it, never a new one.
  const cni: { label: string; figure?: string; fact: Fact }[] = [
    { label: 'Cost', figure: 'A$181', fact: FACTS.cniFee },
    { label: 'Timing', figure: '3 months', fact: FACTS.cniTiming },
    { label: 'Where', fact: FACTS.cniWho },
    { label: 'How', fact: FACTS.cniBooking }
  ];

  const timeline = [
    {
      when: '9–12 months before',
      title: 'Choose your option',
      what: 'Decide between a legal wedding in Bali and legal at home with a symbolic ceremony in Bali. If legal in Bali, check you can marry under one shared religion, and if you are Catholic, ask the parish what it requires.'
    },
    {
      when: '3–4 months before',
      title: 'Gather documents',
      what: 'Passports, birth certificates, and divorce or death certificates if either of you was married before. Book a CNI appointment at the Bali Consulate-General inside the three months before the wedding.'
    },
    {
      when: '10+ working days before',
      title: 'Give notice',
      what: 'Give notice to the civil registry where you will marry, with the CNI and your documents.'
    },
    {
      when: 'Wedding week',
      title: 'Marry and register',
      what: 'The religious ceremony, then registration with the civil registry, or the KUA for Muslim couples.'
    },
    {
      when: 'Back home',
      title: 'Keep the certificate safe',
      what: 'It cannot be registered in Australia. Check with your state registry before using it to change your name.'
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

  const toc = [
    { href: '#options', label: 'Two options' },
    { href: '#requirements', label: 'Indonesian requirements' },
    { href: '#cni', label: 'The CNI' },
    { href: '#recognition', label: 'Back in Australia' },
    { href: '#timeline', label: 'Timeline' },
    { href: '#faq', label: 'FAQ' },
    { href: '#enquire', label: 'Get help' }
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

  // The design's display serif: the `font-serif` theme token in app.css.
  const SERIF = 'font-serif';
  const EYEBROW = 'text-[13px] font-semibold tracking-[0.2em] uppercase';
  const H2 = cn(SERIF, 'text-[38px] leading-[1.02] font-semibold tracking-[-0.01em] text-balance md:text-[62px]');
  const SECTION = 'mx-auto max-w-[1200px] px-5 py-20 md:px-7 md:py-24';
</script>

{#snippet source(item: Fact, tone: 'light' | 'dark' = 'light')}
  <a
    href={item.source.url}
    target="_blank"
    rel="noopener noreferrer"
    title={item.source.title}
    class={cn(
      'text-xs whitespace-nowrap underline underline-offset-2',
      tone === 'dark' ? 'text-brand-dark-accent' : 'text-brand-gold-hover'
    )}>[source]</a
  >
{/snippet}

{#snippet fact(item: Fact, tone: 'light' | 'dark' = 'light')}
  {item.text}
  {@render source(item, tone)}
{/snippet}

{#snippet enquiryTitle()}
  We handle the <em class="font-medium text-brand-dark-accent italic">paperwork</em> for you
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

<main class="min-h-screen bg-background text-[17px] leading-relaxed text-foreground md:text-lg">
  <PublicHeader />

  <article>
    <!-- Hero -->
    <header class="relative overflow-hidden bg-secondary">
      <img
        src="/img/legal-bali/hero-backdrop.jpg"
        alt=""
        aria-hidden="true"
        class="absolute inset-0 h-full w-full object-cover opacity-20"
      />
      <div
        class="relative mx-auto flex max-w-[1200px] flex-wrap items-end gap-x-14 gap-y-10 px-5 pt-14 md:px-7 md:pt-[72px]"
      >
        <div class="flex min-w-0 flex-[999_1_480px] flex-col gap-7 pb-16 md:pb-20">
          <p class={cn(EYEBROW, 'text-brand-gold-hover')}>Bali weddings · For Australian couples</p>
          <h1
            class={cn(
              SERIF,
              'text-[50px] leading-[0.96] font-semibold tracking-[-0.015em] text-balance md:text-[clamp(50px,6.6vw,94px)]'
            )}
          >
            Is a Bali wedding <em class="font-medium text-brand-gold-hover italic">legal</em> in Australia?
            <span class="text-[0.42em] font-medium tracking-normal whitespace-nowrap text-muted-foreground italic"
              >(2027 guide)</span
            >
          </h1>
          <div class="flex flex-wrap items-baseline gap-x-7 gap-y-3 border-t border-brand-warm-deep pt-6">
            <span class={cn(SERIF, 'text-[46px] leading-none font-semibold text-brand-gold-hover italic')}>
              Usually, yes.
            </span>
            <p class="min-w-0 flex-[1_1_320px] text-[19px] leading-[1.55] text-foreground/75">{heroAnswer}</p>
          </div>
          <div class="flex flex-wrap items-center gap-3.5">
            <a
              href={whatsappHref(waText)}
              class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'h-[54px] px-8 text-lg font-semibold')}
            >
              Chat on WhatsApp <ArrowRightIcon class="size-[18px]" />
            </a>
            <a
              href="#options"
              class="inline-flex h-[54px] items-center rounded-full border border-foreground px-7 text-lg font-medium hover:bg-background/60"
            >
              Compare your two options
            </a>
          </div>
          <p class="text-[15px] text-foreground/75">
            Last checked <time datetime={LAST_CHECKED}>{checked}</time> against Australian Government and
            Indonesian primary sources · General information, not legal advice
          </p>
        </div>

        <!-- Arched photos, sitting on the section's bottom edge -->
        <div class="flex min-w-0 flex-[1_1_500px] items-end gap-4">
          <div class="h-[clamp(320px,34vw,500px)] min-w-0 flex-[1.25_1_0] overflow-hidden rounded-t-full bg-brand-warm-deep">
            <img
              src="/img/legal-bali/ocean-arch.jpg"
              alt="Circular floral wedding arch on a deck facing the ocean, with draped chairs either side of the aisle"
              class="h-full w-full object-cover"
              fetchpriority="high"
            />
          </div>
          <div class="h-[clamp(240px,25vw,360px)] min-w-0 flex-[1_1_0] overflow-hidden rounded-t-full bg-brand-warm-deep">
            <img
              src="/img/legal-bali/lake-temple.jpg"
              alt="Balinese lake temple with tiered thatched roofs and small boats moored in front"
              class="h-full w-full object-cover object-[12%_50%]"
            />
          </div>
        </div>
      </div>
    </header>

    <!-- Three numbers -->
    <section aria-label="Three numbers to know" class="bg-brand-ink text-white">
      <div
        class="mx-auto grid max-w-[1200px] gap-x-10 gap-y-9 px-5 pt-[52px] pb-14 md:px-7 [grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr))]"
      >
        {#each stats as stat (stat.text)}
          <div class="flex flex-col gap-3 border-l border-brand-dark-accent/40 pl-7">
            <p class={cn(SERIF, 'text-[60px] leading-[0.9] font-semibold text-brand-dark-accent md:text-[clamp(60px,6.4vw,92px)]')}>
              {stat.n}
              {#if stat.unit}<span class="text-[0.4em] font-medium whitespace-nowrap italic">{stat.unit}</span>{/if}
            </p>
            <p class="text-[17px] text-white/85">{stat.text}</p>
          </div>
        {/each}
      </div>
    </section>

    <!-- On this page -->
    <nav aria-label="On this page" class="border-b border-border bg-background">
      <div class="mx-auto flex max-w-[1200px] flex-wrap items-center gap-2.5 px-5 py-4 text-[15px] font-medium md:px-7">
        <span class="mr-2 font-normal text-muted-foreground">On this page</span>
        {#each toc as item (item.href)}
          <a
            href={item.href}
            class="rounded-full border border-brand-warm-deep px-[18px] py-2.5 hover:border-brand-gold hover:text-brand-gold-hover"
          >
            {item.label}
          </a>
        {/each}
      </div>
    </nav>

    <!-- Two options -->
    <section id="options" class={cn(SECTION, 'flex scroll-mt-24 flex-col gap-12')}>
      <div class="flex max-w-[760px] flex-col gap-4">
        <p class={cn(EYEBROW, 'text-brand-gold-hover')}>Start here</p>
        <h2 class={H2}>
          Two ways to be <em class="font-medium text-brand-gold-hover italic">married in Bali</em>
        </h2>
        <p class="text-muted-foreground">
          Both end with the same celebration. What changes is where the legal part happens and how much
          paperwork follows you to the island. {@render fact(FACTS.celebrant)}
        </p>
      </div>

      <div class="grid gap-7 [grid-template-columns:repeat(auto-fit,minmax(min(440px,100%),1fr))]">
        {#each options as option (option.n)}
          <article
            class={cn(
              'flex flex-col overflow-hidden rounded-3xl border',
              option.dark ? 'border-brand-ink bg-brand-ink text-white' : 'border-border bg-background'
            )}
          >
            <div class="h-[300px] overflow-hidden bg-brand-warm-deep">
              <img src={option.img} alt={option.alt} class={cn('h-full w-full object-cover', option.position)} loading="lazy" />
            </div>
            <div class="flex flex-col gap-6 p-7 md:p-9">
              <div class="flex items-end justify-between gap-4">
                <div class="flex min-w-0 flex-col items-start gap-2">
                  {#if option.dark}
                    <span class="rounded-full bg-brand-dark-accent px-3.5 py-1 text-[13px] font-semibold text-brand-ink">
                      What many couples choose
                    </span>
                  {/if}
                  <span class={cn(EYEBROW, option.dark ? 'text-brand-dark-accent' : 'text-brand-gold-hover')}>
                    Option {Number(option.n)}
                  </span>
                  <h3 class={cn(SERIF, 'text-[34px] leading-[1.05] font-semibold md:text-[38px]')}>{option.heading}</h3>
                </div>
                <span
                  aria-hidden="true"
                  class={cn(SERIF, 'text-[76px] leading-[0.8] font-medium text-brand-dark-accent italic')}
                >
                  {option.n}
                </span>
              </div>
              <dl class="flex flex-col">
                {#each routes as row, index (row.label)}
                  <div
                    class={cn(
                      'flex flex-col gap-1 border-t py-4',
                      index === routes.length - 1 && 'pb-0',
                      option.dark ? 'border-white/15' : 'border-border'
                    )}
                  >
                    <dt
                      class={cn(
                        'text-xs font-semibold tracking-[0.16em] uppercase',
                        option.dark ? 'text-brand-dark-accent' : 'text-brand-gold-hover'
                      )}
                    >
                      {row.label}
                    </dt>
                    <dd class={option.dark ? 'text-white/90' : ''}>{row[option.kind]}</dd>
                  </div>
                {/each}
              </dl>
            </div>
          </article>
        {/each}
      </div>
    </section>

    <!-- Indonesian requirements -->
    <section id="requirements" class="scroll-mt-24 bg-secondary">
      <div class={cn(SECTION, 'flex flex-wrap gap-x-[72px] gap-y-12')}>
        <div class="flex min-w-0 flex-[1_1_340px] flex-col gap-4">
          <p class={cn(EYEBROW, 'text-brand-gold-hover')}>If you marry legally in Bali</p>
          <h2 class={H2}>What Indonesian law asks for</h2>
          <p class="text-muted-foreground">
            Requirements vary by province, so treat this as the Bali baseline and confirm with your registry.
          </p>
          <div
            class="relative mt-4 aspect-[4/5] w-full max-w-[380px] overflow-hidden rounded-t-full rounded-b-3xl bg-brand-warm-deep"
          >
            <img
              src="/img/legal-bali/ring-marriage-book.jpg"
              alt="Gold wedding ring resting on an Indonesian marriage book, surrounded by greenery"
              class="absolute inset-0 h-full w-full object-cover object-bottom"
              loading="lazy"
            />
          </div>
        </div>
        <ol class="flex min-w-0 flex-[999_1_560px] flex-col border-b border-brand-warm-deep">
          {#each requirements as item, index (item.title)}
            <li class="flex gap-6 border-t border-brand-warm-deep py-[22px]">
              <span
                aria-hidden="true"
                class={cn(SERIF, 'w-[52px] shrink-0 text-[40px] leading-none font-medium text-brand-gold-hover italic')}
              >
                {String(index + 1).padStart(2, '0')}
              </span>
              <div class="flex min-w-0 flex-col gap-1">
                <span class="text-xl font-semibold">{item.title}</span>
                <span class="text-foreground/75">{@render fact(item.fact)}</span>
              </div>
            </li>
          {/each}
        </ol>
      </div>
    </section>

    <!-- The CNI -->
    <section id="cni" class="scroll-mt-24 bg-brand-ink text-white">
      <div class={cn(SECTION, 'flex flex-wrap items-center gap-x-[72px] gap-y-12')}>
        <div class="flex min-w-0 flex-[1_1_400px] flex-col gap-5">
          <svg aria-hidden="true" width="132" height="84" viewBox="0 0 150 96" fill="none" class="stroke-brand-dark-accent" stroke-width="1.5">
            <circle cx="52" cy="48" r="44"></circle>
            <circle cx="98" cy="48" r="44"></circle>
          </svg>
          <p class={cn(EYEBROW, 'text-brand-dark-accent')}>For the foreign partner</p>
          <h2 class={H2}>
            The Certificate of <em class="font-medium text-brand-dark-accent italic">No Impediment</em>
          </h2>
          <p class="text-white/80">
            The CNI is Australia's statement that you are free to marry. Indonesian registries ask the foreign
            partner for one before they will register the marriage.
          </p>
        </div>
        <dl class="grid min-w-0 flex-[1_1_480px] gap-4 [grid-template-columns:repeat(auto-fit,minmax(min(220px,100%),1fr))]">
          {#each cni as card (card.label)}
            <div class="flex flex-col gap-2 rounded-[18px] border border-white/20 p-[26px]">
              <dt class="text-xs font-semibold tracking-[0.16em] text-brand-dark-accent uppercase">{card.label}</dt>
              <dd class="text-[16px] leading-relaxed text-white/80">
                {#if card.figure}
                  <span class={cn(SERIF, 'mb-2 block text-[52px] leading-none font-semibold text-white')}>{card.figure}</span>
                {/if}
                {@render fact(card.fact, 'dark')}
              </dd>
            </div>
          {/each}
        </dl>
      </div>
    </section>

    <!-- Back in Australia -->
    <section id="recognition" class={cn(SECTION, 'flex scroll-mt-24 flex-col gap-12')}>
      <div class="flex max-w-[760px] flex-col gap-4">
        <p class={cn(EYEBROW, 'text-brand-gold-hover')}>After the wedding</p>
        <h2 class={H2}>Once you are back in Australia</h2>
      </div>
      <div class="grid gap-x-12 gap-y-9 [grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr))]">
        <div class="flex flex-col gap-2.5 border-t-2 border-brand-gold pt-6">
          <h3 class={cn(SERIF, 'text-[32px] leading-[1.1] font-semibold')}>Recognised, not registered</h3>
          <p class="text-muted-foreground">{@render fact(FACTS.recognised)}</p>
        </div>
        <div class="flex flex-col gap-2.5 border-t-2 border-brand-gold pt-6">
          <h3 class={cn(SERIF, 'text-[32px] leading-[1.1] font-semibold')}>Changing your name</h3>
          <p class="text-muted-foreground">{@render fact(FACTS.nameChange)}</p>
        </div>
        <div class="flex flex-col gap-2.5 border-t-2 border-brand-gold pt-6">
          <h3 class={cn(SERIF, 'text-[32px] leading-[1.1] font-semibold')}>Apostilles</h3>
          <p class="text-muted-foreground">
            {@render fact(FACTS.apostilleIndonesia)}
            {@render fact(FACTS.apostilleAuthority)} If an Australian office asks for an apostilled copy of your
            certificate, that is where it comes from.
          </p>
        </div>
      </div>
    </section>

    <!-- Temples and same-sex couples -->
    <section class="bg-secondary">
      <div class={cn(SECTION, 'flex flex-wrap items-stretch gap-x-[72px] gap-y-12')}>
        <div class="relative min-h-[440px] min-w-0 flex-[1_1_420px] overflow-hidden rounded-3xl bg-brand-warm-deep">
          <img
            src="/img/legal-bali/water-temple.jpg"
            alt="Balinese water temple with a tall tiered roof on a lake, red flowers in the foreground"
            class="absolute inset-0 h-full w-full object-cover"
            loading="lazy"
          />
        </div>
        <div class="flex min-w-0 flex-[1_1_460px] flex-col justify-center gap-9">
          <section class="flex flex-col gap-3">
            <h2 class={cn(SERIF, 'text-[32px] leading-[1.05] font-semibold md:text-[44px]')}>Temples and photo shoots</h2>
            <p class="text-foreground/75">
              {@render fact(FACTS.temples)} A temple as a backdrop is different from a ceremony inside one, so
              ask your venue or planner before booking a shoot at a sacred site.
            </p>
          </section>
          <section class="flex flex-col gap-3 border-t border-brand-warm-deep pt-9">
            <h2 class={cn(SERIF, 'text-[32px] leading-[1.05] font-semibold md:text-[44px]')}>Same-sex couples</h2>
            <p class="text-foreground/75">
              {@render fact(FACTS.sameSexLaw)}
              {@render fact(FACTS.sameSexIndonesia)}
              {@render fact(FACTS.sameSexAustralia)} A legal marriage is possible in Australia. Talk to us before
              planning anything public in Bali.
            </p>
          </section>
        </div>
      </div>
    </section>

    <!-- Timeline -->
    <section id="timeline" class={cn(SECTION, 'flex scroll-mt-24 flex-col gap-12')}>
      <div class="flex flex-wrap items-end justify-between gap-x-10 gap-y-4">
        <div class="flex flex-col gap-4">
          <p class={cn(EYEBROW, 'text-brand-gold-hover')}>Five steps</p>
          <h2 class={H2}>Your paperwork timeline</h2>
        </div>
        <a
          href={siteHref('/wedding-tools/bali-wedding-date-planner')}
          class="inline-flex items-center gap-2 py-3 font-semibold text-brand-gold-hover underline-offset-4 hover:underline"
        >
          Check your date against Nyepi and holy days <ArrowRightIcon class="size-[18px]" />
        </a>
      </div>
      <ol class="mt-7 grid gap-y-14 [grid-template-columns:repeat(auto-fit,minmax(min(200px,100%),1fr))]">
        {#each timeline as step, index (step.when)}
          <li class="flex flex-col gap-3 border-t-2 border-brand-dark-accent pr-6">
            <span
              class={cn(
                SERIF,
                '-mt-[27px] flex size-[52px] items-center justify-center rounded-full bg-brand-ink text-[28px] leading-none font-semibold text-brand-dark-accent'
              )}
            >
              {index + 1}
            </span>
            <span class="text-[13px] font-semibold tracking-[0.14em] text-brand-gold-hover uppercase">{step.when}</span>
            <span class={cn(SERIF, 'text-[28px] leading-[1.1] font-semibold')}>{step.title}</span>
            <span class="text-base text-muted-foreground">{step.what}</span>
          </li>
        {/each}
      </ol>
    </section>

    <!-- FAQ -->
    <section id="faq" class="scroll-mt-24 bg-secondary">
      <div class={cn(SECTION, 'flex flex-wrap gap-x-[72px] gap-y-10')}>
        <div class="flex min-w-0 flex-[1_1_320px] flex-col items-start gap-4">
          <p class={cn(EYEBROW, 'text-brand-gold-hover')}>FAQ</p>
          <h2 class={H2}>Questions couples ask us</h2>
          <p class="text-muted-foreground">
            Can't see yours?
            <a href={whatsappHref(waText)} class="font-semibold text-brand-gold-hover underline underline-offset-2">
              Ask our Bali team on WhatsApp</a
            >.
          </p>
        </div>
        <div class="flex min-w-0 flex-[999_1_560px] flex-col border-b border-brand-warm-deep">
          {#each faqs as faq, index (faq.q)}
            <details open={index === 0} class="border-t border-brand-warm-deep py-[22px]">
              <summary
                class={cn(
                  SERIF,
                  'min-h-11 cursor-pointer text-[24px] leading-[1.15] font-semibold marker:text-brand-gold md:text-[28px]'
                )}
              >
                {faq.q}
              </summary>
              <p class="mt-2.5 text-foreground/75">{faq.a}</p>
            </details>
          {/each}
        </div>
      </div>
    </section>

    <!-- Sources: the page's case, so it stays, quietly -->
    <section class="mx-auto max-w-[1200px] px-5 pt-14 pb-4 md:px-7">
      <h2 class={cn(EYEBROW, 'text-brand-gold-hover')}>Sources</h2>
      <ol class="mt-4 grid list-decimal gap-2 pl-5 text-sm leading-6 text-muted-foreground md:grid-cols-2 md:gap-x-10">
        {#each ALL_SOURCES as item (item.url)}
          <li>
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              class="underline underline-offset-2 hover:text-foreground">{item.title}</a
            >
          </li>
        {/each}
      </ol>
    </section>
  </article>

  <!-- Enquiry -->
  <section id="enquire" class="mt-14 scroll-mt-24 bg-brand-ink">
    <div class={SECTION}>
      <BaliEnquiry
        tone="dark"
        sourcePath={PATH}
        eyebrow="Talk to our Bali team"
        heading="We handle the paperwork for you"
        title={enquiryTitle}
        headingClass={cn(SERIF, 'text-[40px] leading-none font-semibold tracking-[-0.01em] text-balance md:text-[clamp(40px,5vw,68px)]')}
        lead="Tell us your date and which option you are leaning towards. Our Bali team books the CNI appointment, prepares the documents and handles the civil registration, so you can get on with the wedding."
        context={['Page: legal guide (legally married in Bali)']}
        whatsappText={waText}
        event="Bali Legal Help Requested"
      />
    </div>
  </section>

  <PublicFooter />
</main>
