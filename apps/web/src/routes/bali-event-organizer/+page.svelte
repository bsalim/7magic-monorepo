<script lang="ts">
  import CalendarIcon from '@lucide/svelte/icons/calendar-days';
  import CheckIcon from '@lucide/svelte/icons/check';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';

  /**
   * Landing page for the corporate / outing side of the business.
   *
   * Bilingual, unlike /paket-sangjit and /perjanjian-pranikah: Bali outings are
   * booked both by Indonesian companies and by the English-language search that
   * the page's own URL targets, so neither audience can be dropped.
   *
   * Every array below is $derived, not const: the message functions read the
   * active locale, and a plain const would freeze the copy of whichever locale
   * rendered first.
   */

  // The Day Programme rate and the 20-person floor are confirmed by 7Magic.
  // The Two Nights package shows "on quote" rather than a figure — the number
  // that used to sit here was a placeholder that reached production.
  const packages = $derived([
    {
      name: m.beo_pkg_day_name(),
      from: 'Rp 500.000',
      unit: m.beo_pkg_day_unit(),
      minimum: m.beo_pkg_day_minimum(),
      summary: m.beo_pkg_day_summary(),
      includes: [
        m.beo_pkg_day_i1(),
        m.beo_pkg_day_i2(),
        m.beo_pkg_day_i3(),
        m.beo_pkg_day_i4(),
        m.beo_pkg_day_i5()
      ]
    },
    {
      name: m.beo_pkg_two_name(),
      from: m.beo_pkg_on_quote(),
      unit: '',
      minimum: m.beo_pkg_two_minimum(),
      summary: m.beo_pkg_two_summary(),
      featured: true,
      includes: [
        m.beo_pkg_two_i1(),
        m.beo_pkg_two_i2(),
        m.beo_pkg_two_i3(),
        m.beo_pkg_two_i4(),
        m.beo_pkg_two_i5(),
        m.beo_pkg_two_i6()
      ]
    },
    {
      name: m.beo_pkg_conf_name(),
      from: m.beo_pkg_on_quote(),
      unit: '',
      minimum: m.beo_pkg_conf_minimum(),
      summary: m.beo_pkg_conf_summary(),
      includes: [
        m.beo_pkg_conf_i1(),
        m.beo_pkg_conf_i2(),
        m.beo_pkg_conf_i3(),
        m.beo_pkg_conf_i4(),
        m.beo_pkg_conf_i5(),
        m.beo_pkg_conf_i6()
      ]
    }
  ]);

  const services = $derived([
    {
      image: '/img/bali-event/outing.jpg',
      alt: m.beo_svc_outing_alt(),
      title: m.beo_svc_outing_title(),
      copy: m.beo_svc_outing_copy()
    },
    {
      image: '/img/bali-event/teambuilding.jpg',
      alt: m.beo_svc_teambuilding_alt(),
      title: m.beo_svc_teambuilding_title(),
      copy: m.beo_svc_teambuilding_copy()
    },
    {
      image: '/img/bali-event/gathering.jpg',
      alt: m.beo_svc_gathering_alt(),
      title: m.beo_svc_gathering_title(),
      copy: m.beo_svc_gathering_copy()
    },
    {
      image: '/img/bali-event/gala.jpg',
      alt: m.beo_svc_gala_alt(),
      title: m.beo_svc_gala_title(),
      copy: m.beo_svc_gala_copy()
    },
    {
      image: '/img/bali-event/conference.jpg',
      alt: m.beo_svc_conference_alt(),
      title: m.beo_svc_conference_title(),
      copy: m.beo_svc_conference_copy()
    },
    {
      image: '/img/bali-event/incentive.jpg',
      alt: m.beo_svc_incentive_alt(),
      title: m.beo_svc_incentive_title(),
      copy: m.beo_svc_incentive_copy()
    }
  ]);

  const itinerary = $derived([
    {
      day: m.beo_itin_d1_day(),
      title: m.beo_itin_d1_title(),
      items: [m.beo_itin_d1_i1(), m.beo_itin_d1_i2(), m.beo_itin_d1_i3()]
    },
    {
      day: m.beo_itin_d2_day(),
      title: m.beo_itin_d2_title(),
      items: [m.beo_itin_d2_i1(), m.beo_itin_d2_i2(), m.beo_itin_d2_i3()]
    },
    {
      day: m.beo_itin_d3_day(),
      title: m.beo_itin_d3_title(),
      items: [m.beo_itin_d3_i1(), m.beo_itin_d3_i2(), m.beo_itin_d3_i3()]
    }
  ]);

  const steps = $derived([
    { title: m.beo_step1_title(), copy: m.beo_step1_copy(), time: m.beo_step1_time() },
    { title: m.beo_step2_title(), copy: m.beo_step2_copy(), time: m.beo_step2_time() },
    { title: m.beo_step3_title(), copy: m.beo_step3_copy(), time: m.beo_step3_time() },
    { title: m.beo_step4_title(), copy: m.beo_step4_copy(), time: m.beo_step4_time() }
  ]);

  const faqs = $derived([
    { q: m.beo_faq_q1(), a: m.beo_faq_a1() },
    { q: m.beo_faq_q2(), a: m.beo_faq_a2() },
    { q: m.beo_faq_q3(), a: m.beo_faq_a3() },
    { q: m.beo_faq_q4(), a: m.beo_faq_a4() },
    { q: m.beo_faq_q5(), a: m.beo_faq_a5() },
    { q: m.beo_faq_q6(), a: m.beo_faq_a6() }
  ]);

  const stats = $derived([
    { value: '18+', label: m.beo_stat_years_label() },
    { value: '1000+', label: m.beo_stat_events_label() },
    { value: '100+', label: m.beo_stat_vendors_label() },
    { value: 'Bali', label: m.beo_stat_bali_label() }
  ]);

  const budgets = $derived([
    m.beo_form_budget_1(),
    m.beo_form_budget_2(),
    m.beo_form_budget_3(),
    m.beo_form_budget_4(),
    m.beo_form_budget_5()
  ]);

  const eventTypes = $derived([
    m.beo_form_type_outing(),
    m.beo_form_type_teambuilding(),
    m.beo_form_type_gathering(),
    m.beo_form_type_gala(),
    m.beo_form_type_conference(),
    m.beo_form_type_incentive(),
    m.beo_form_type_other()
  ]);

  // Real client logos and quotes go here once 7Magic supplies them. Left empty
  // on purpose — an invented testimonial on a live site is a fake review.
  const testimonials: { quote: string; name: string; role: string }[] = [];

  const waHref = $derived(whatsappHref(m.beo_wa_prefill()));

  let sending = $state(false);
  let submitted = $state(false);
  let errorMessage = $state('');

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (sending) return;

    const form = event.currentTarget as HTMLFormElement;
    const data = new FormData(form);
    const field = (key: string) => String(data.get(key) ?? '').trim();

    // The API's contact-lead schema has no event-specific columns, so the
    // qualifying answers are folded into the message body. Sales reads them
    // there; a dedicated schema is the follow-up, not a blocker for launch.
    //
    // These labels stay English whatever the visitor's locale: they are read by
    // the sales inbox, not by the customer, and one fixed shape is easier to
    // scan than two.
    const message = [
      `Event type: ${field('event_type') || '—'}`,
      `Target date: ${field('event_date') || '—'}`,
      `Headcount: ${field('pax') || '—'}`,
      `Budget: ${field('budget') || '—'}`,
      `Company: ${field('company') || '—'}`,
      '',
      field('notes') || 'No extra notes.'
    ].join('\n');

    sending = true;
    errorMessage = '';

    try {
      const response = await fetch('/api/contact-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: field('name'),
          phone: field('phone'),
          email: field('email') || undefined,
          message,
          source_path: '/bali-event-organizer'
        })
      });

      if (!response.ok) {
        errorMessage = m.beo_form_error();
        return;
      }

      submitted = true;
      form.reset();
    } catch {
      errorMessage = m.beo_form_error();
    } finally {
      sending = false;
    }
  }

  const inputClass =
    'rounded-md border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30';
</script>

<svelte:head>
  <title>{m.beo_meta_title()}</title>
  <meta name="description" content={m.beo_meta_description()} />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[640px]">
    <img
      src="/img/bali-event/hero-temple.jpg"
      alt={m.beo_hero_image_alt()}
      class="absolute inset-0 h-full w-full object-cover object-[50%_38%]"
      fetchpriority="high"
    />
    <!-- No flat dimming layer — the sunset stays at full brightness. Contrast
         for the headline comes from a soft left-side gradient plus a shadow on
         the text itself, rather than from darkening the whole photo. -->
    <div class="absolute inset-0 bg-gradient-to-r from-black/55 via-black/15 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          {m.beo_hero_eyebrow()}
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.4rem]">
          {m.beo_hero_title()}
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/85">
          {m.beo_hero_body()}
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a href="#proposal" class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
            {m.beo_hero_cta_proposal()}
          </a>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'border border-white/30 bg-white/10 px-7 text-white backdrop-blur hover:bg-white hover:text-brand-ink'
            )}
          >
            <MessageCircleIcon size={18} />
            {m.beo_hero_cta_wa()}
          </a>
        </div>

        <p class="mt-5 text-sm text-white/90">
          {m.beo_hero_note()}
        </p>
      </div>
    </div>
  </section>

  <!-- Trust strip. Figures match the ones published on 7magicwedding.com. -->
  <section class="border-b border-border bg-brand-ink px-5 py-6 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {#each stats as stat}
        <div>
          <p class="font-display text-2xl font-bold text-brand-dark-accent">{stat.value}</p>
          <p class="mt-1 text-sm text-white/72">{stat.label}</p>
        </div>
      {/each}
    </div>
  </section>

  <!-- Services -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      {m.beo_services_eyebrow()}
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      {m.beo_services_title()}
    </h2>

    <div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {#each services as service}
        <article class="group relative h-[340px] overflow-hidden rounded-md">
          <img
            src={service.image}
            alt={service.alt}
            loading="lazy"
            class="absolute inset-0 h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
          <div
            class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/45 to-black/10"
          ></div>
          <div class="absolute inset-x-0 bottom-0 p-6 text-white">
            <h3 class="font-display text-xl font-semibold">{service.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-white/85">{service.copy}</p>
          </div>
        </article>
      {/each}
    </div>
  </section>

  <!-- Sample itinerary -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
        <div>
          <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
            {m.beo_itin_eyebrow()}
          </p>
          <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
            {m.beo_itin_title()}
          </h2>
          <p class="mt-4 max-w-xl text-[15px] leading-7 text-muted-foreground">
            {m.beo_itin_body()}
          </p>

          <div class="mt-8 grid gap-4">
            {#each itinerary as block}
              <div class="rounded-md border border-border bg-background p-6">
                <div class="flex items-baseline gap-3">
                  <span class="rounded-full bg-brand-gold-soft px-3 py-1 text-xs font-semibold uppercase tracking-widest text-brand-gold-hover">
                    {block.day}
                  </span>
                  <h3 class="font-display text-lg font-semibold">{block.title}</h3>
                </div>
                <ul class="mt-4 grid gap-2.5">
                  {#each block.items as item}
                    <li class="flex gap-3 text-[15px] leading-7 text-muted-foreground">
                      <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                      <span>{item}</span>
                    </li>
                  {/each}
                </ul>
              </div>
            {/each}
          </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
          <img
            src="/img/bali-event/teambuilding.jpg"
            alt={m.beo_svc_teambuilding_alt()}
            loading="lazy"
            class="h-64 w-full rounded-md object-cover"
          />
          <img
            src="/img/bali-event/kecak.jpg"
            alt={m.beo_svc_gala_alt()}
            loading="lazy"
            class="h-64 w-full rounded-md object-cover"
          />
          <img
            src="/img/bali-event/gala.jpg"
            alt={m.beo_svc_gala_alt()}
            loading="lazy"
            class="h-64 w-full rounded-md object-cover sm:col-span-2 lg:col-span-1"
          />
        </div>
      </div>
    </div>
  </section>

  <!-- Packages -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      {m.beo_pkg_eyebrow()}
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      {m.beo_pkg_title()}
    </h2>
    <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
      {m.beo_pkg_body()}
    </p>

    <div class="mt-10 grid gap-5 lg:grid-cols-3">
      {#each packages as pkg}
        <div
          class={cn(
            'flex flex-col rounded-md border bg-background p-7',
            pkg.featured ? 'border-brand-gold shadow-lg ring-1 ring-brand-gold/20' : 'border-border'
          )}
        >
          {#if pkg.featured}
            <span class="mb-4 w-fit rounded-full bg-brand-gold px-3 py-1 text-xs font-semibold uppercase tracking-widest text-white">
              {m.beo_pkg_featured()}
            </span>
          {/if}
          <h3 class="font-display text-xl font-semibold">{pkg.name}</h3>
          <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{pkg.summary}</p>

          <div class="mt-5 flex items-baseline gap-1.5">
            {#if pkg.unit}
              <span class="text-sm text-muted-foreground">{m.beo_pkg_from()}</span>
            {/if}
            <span class="font-display text-2xl font-bold">{pkg.from}</span>
            <span class="text-sm text-muted-foreground">{pkg.unit}</span>
          </div>
          <p class="mt-1 text-sm text-muted-foreground">{pkg.minimum}</p>

          <ul class="mt-6 grid flex-1 content-start gap-2.5 border-t border-border pt-6">
            {#each pkg.includes as item}
              <li class="flex gap-3 text-[15px] leading-7">
                <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>

          <a
            href="#proposal"
            class={cn(
              buttonVariants({ variant: pkg.featured ? 'gold' : 'outline' }),
              'mt-7 w-full'
            )}
          >
            {m.beo_pkg_cta()}
          </a>
        </div>
      {/each}
    </div>

    <div class="mt-8 rounded-md border border-border bg-secondary p-6">
      <h3 class="font-display text-base font-semibold">{m.beo_pkg_excluded_title()}</h3>
      <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
        {m.beo_pkg_excluded_body()}
      </p>
    </div>
  </section>

  <!-- How it works -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {m.beo_steps_eyebrow()}
      </p>
      <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">{m.beo_steps_title()}</h2>

      <div class="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        {#each steps as step, index}
          <div class="rounded-md border border-border bg-background p-6">
            <span class="font-display text-3xl font-bold text-brand-warm-deep">
              {String(index + 1).padStart(2, '0')}
            </span>
            <h3 class="mt-3 font-display text-lg font-semibold">{step.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{step.copy}</p>
            <p class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand-gold-hover">
              <CalendarIcon size={15} />
              {step.time}
            </p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  {#if testimonials.length}
    <section class="bg-secondary px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <h2 class="font-display text-3xl font-bold md:text-4xl">{m.beo_testimonials_title()}</h2>
        <div class="mt-10 grid gap-5 md:grid-cols-3">
          {#each testimonials as item}
            <figure class="rounded-md border border-border bg-background p-6">
              <blockquote class="text-[15px] leading-7">{item.quote}</blockquote>
              <figcaption class="mt-4 text-sm font-semibold">
                {item.name}
                <span class="block font-normal text-muted-foreground">{item.role}</span>
              </figcaption>
            </figure>
          {/each}
        </div>
      </div>
    </section>
  {/if}

  <!-- FAQ -->
  <section class="mx-auto max-w-4xl px-5 py-16 lg:px-8">
    <h2 class="font-display text-3xl font-bold md:text-4xl">{m.beo_faq_title()}</h2>
    <div class="mt-8 grid gap-3">
      {#each faqs as faq}
        <details class="group rounded-md border border-border bg-background p-6">
          <summary class="cursor-pointer list-none font-display text-lg font-semibold marker:hidden">
            {faq.q}
          </summary>
          <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{faq.a}</p>
        </details>
      {/each}
    </div>
  </section>

  <!-- Lead form -->
  <section id="proposal" class="scroll-mt-20 bg-brand-ink px-5 py-16 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.85fr_1.15fr]">
      <div>
        <h2 class="font-display text-3xl font-bold md:text-4xl">{m.beo_form_title()}</h2>
        <p class="mt-4 text-[15px] leading-7 text-white/75">
          {m.beo_form_subtitle()}
        </p>

        <div class="mt-8 rounded-md border border-white/15 bg-white/5 p-6">
          <p class="text-sm text-white/70">{m.beo_form_talk()}</p>
          <a
            href={waHref}
            class={cn(buttonVariants({ size: 'lg' }), 'mt-3 w-full bg-brand-success text-white hover:bg-brand-success-hover')}
          >
            <MessageCircleIcon size={18} />
            {m.beo_form_wa_button({ number: whatsappDisplay })}
          </a>
        </div>
      </div>

      <div class="rounded-md bg-background p-7 text-foreground">
        {#if submitted}
          <div class="flex flex-col items-center gap-4 py-12 text-center">
            <span class="flex size-14 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover">
              <CheckIcon size={28} />
            </span>
            <h3 class="font-display text-xl font-semibold">{m.beo_form_success_title()}</h3>
            <p class="max-w-sm text-[15px] leading-7 text-muted-foreground">
              {m.beo_form_success_body()}
            </p>
            <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-2')}>
              <MessageCircleIcon size={17} />
              {m.beo_form_success_cta()}
            </a>
          </div>
        {:else}
          <form onsubmit={submit} class="grid gap-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="ev-type" class="text-[13px] font-medium">
                  {m.beo_form_event_type()} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <select id="ev-type" name="event_type" required class={inputClass}>
                  <option value="">{m.beo_form_choose_one()}</option>
                  {#each eventTypes as type}
                    <option value={type}>{type}</option>
                  {/each}
                </select>
              </div>
              <div class="grid gap-1.5">
                <label for="ev-date" class="text-[13px] font-medium">
                  {m.beo_form_target_date()}
                  <span class="text-muted-foreground">{m.beo_form_rough_ok()}</span>
                </label>
                <input id="ev-date" name="event_date" type="date" class={inputClass} />
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="ev-pax" class="text-[13px] font-medium">
                  {m.beo_form_pax()} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="ev-pax"
                  name="pax"
                  type="number"
                  min="1"
                  required
                  placeholder={m.beo_form_pax_ph()}
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="ev-budget" class="text-[13px] font-medium">{m.beo_form_budget()}</label>
                <select id="ev-budget" name="budget" class={inputClass}>
                  <option value="">{m.beo_form_budget_none()}</option>
                  {#each budgets as budget}
                    <option value={budget}>{budget}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="ev-name" class="text-[13px] font-medium">
                  {m.beo_form_name()} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="ev-name"
                  name="name"
                  required
                  autocomplete="name"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="ev-company" class="text-[13px] font-medium">{m.beo_form_company()}</label>
                <input id="ev-company" name="company" autocomplete="organization" class={inputClass} />
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="ev-phone" class="text-[13px] font-medium">
                  {m.beo_form_whatsapp()} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="ev-phone"
                  name="phone"
                  required
                  autocomplete="tel"
                  placeholder={m.beo_form_phone_ph()}
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="ev-email" class="text-[13px] font-medium">
                  {m.beo_form_email()}
                  <span class="text-muted-foreground">{m.beo_form_optional()}</span>
                </label>
                <input
                  id="ev-email"
                  name="email"
                  type="email"
                  autocomplete="email"
                  class={inputClass}
                />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="ev-notes" class="text-[13px] font-medium">
                {m.beo_form_notes()}
              </label>
              <textarea
                id="ev-notes"
                name="notes"
                rows="3"
                placeholder={m.beo_form_notes_ph()}
                class={inputClass}
              ></textarea>
            </div>

            {#if errorMessage}
              <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
            {/if}

            <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending}>
              {sending ? m.beo_form_sending() : m.beo_form_submit()}
            </Button>
            <p class="text-center text-xs text-muted-foreground">
              {m.beo_form_privacy()}
            </p>
          </form>
        {/if}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
