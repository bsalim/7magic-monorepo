<script lang="ts">
  import { untrack } from 'svelte';

  /**
   * A birth date as three plain fields: day, month, year.
   *
   * A calendar suits a wedding date, where the weekday matters and the date is
   * close. A birth date is decades back and known by heart, so typing "5",
   * picking "Mei" and typing "1995" beats paging a calendar to get there.
   *
   * The form still owns one "YYYY-MM-DD" string. It stays empty until all three
   * parts are in; whether that day exists (30 February) is the form's check,
   * so its message can sit with the rest of the form's errors.
   */

  interface Props {
    value?: string;
    /** Goes on the day field, the first of the three. */
    id: string;
    /** The id of the visible label the three fields share. */
    labelledby: string;
    locale: string;
    labels: { day: string; dayPlaceholder: string; month: string; year: string };
  }

  let { value = $bindable(''), id, labelledby, locale, labels }: Props = $props();

  let day = $state('');
  let month = $state('');
  let year = $state('');

  const months = $derived.by(() => {
    const format = new Intl.DateTimeFormat(locale === 'en' ? 'en-GB' : 'id-ID', { month: 'long', timeZone: 'UTC' });
    return Array.from({ length: 12 }, (_, index) => format.format(new Date(Date.UTC(2024, index, 1))));
  });

  const pad = (n: number) => String(n).padStart(2, '0');

  function compose(): string {
    const d = Number(day);
    const m = Number(month);
    if (!/^\d{4}$/.test(year) || !(m >= 1 && m <= 12) || !(d >= 1 && d <= 31)) return '';
    return `${year}-${pad(m)}-${pad(d)}`;
  }

  // A date written from outside (the example button) has to show in the three
  // fields. A value that already matches them is our own write, or a
  // half-typed date, and must not be parsed back over what is being typed.
  $effect(() => {
    const incoming = value;
    untrack(() => {
      if (incoming === compose()) return;
      const parts = /^(\d{4})-(\d{2})-(\d{2})$/.exec(incoming);
      year = parts ? parts[1] : '';
      month = parts ? String(Number(parts[2])) : '';
      day = parts ? String(Number(parts[3])) : '';
    });
  });

  function update() {
    day = day.replace(/\D/g, '');
    year = year.replace(/\D/g, '');
    value = compose();
  }

  const FIELD =
    'h-12 w-full min-w-0 rounded-lg border border-input bg-background px-3 text-base placeholder:text-muted-foreground/60 focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none';
</script>

<div role="group" aria-labelledby={labelledby} class="grid grid-cols-[4.25rem_minmax(0,1fr)_5.5rem] gap-2">
  <input
    {id}
    bind:value={day}
    oninput={update}
    inputmode="numeric"
    maxlength="2"
    autocomplete="off"
    aria-label={labels.day}
    placeholder={labels.dayPlaceholder}
    class="{FIELD} text-center"
  />
  <select
    bind:value={month}
    onchange={update}
    aria-label={labels.month}
    class="{FIELD} {month ? '' : 'text-muted-foreground/70'}"
  >
    <option value="">{labels.month}</option>
    {#each months as name, index (index)}
      <option value={String(index + 1)}>{name}</option>
    {/each}
  </select>
  <input
    bind:value={year}
    oninput={update}
    inputmode="numeric"
    maxlength="4"
    autocomplete="off"
    aria-label={labels.year}
    placeholder={labels.year}
    class="{FIELD} text-center"
  />
</div>
