<script lang="ts">
  import { untrack } from 'svelte';

  /**
   * A birth time as two dropdowns: hour and minute.
   *
   * The native time input renders differently on every phone and has no way to
   * say "I don't know", which is the commonest answer. Two dropdowns that can
   * be left empty cover both: an empty hour means the time is unknown.
   *
   * The form still owns one "HH:MM" string, empty when no hour is picked. An
   * hour without a minute counts as on the hour, so a rough guess like "around
   * 7 in the morning" needs one pick, not two.
   */

  interface Props {
    value?: string;
    /** Goes on the hour field, the first of the two. */
    id: string;
    /** The id of the visible label the two fields share. */
    labelledby: string;
    labels: { hour: string; minute: string };
  }

  let { value = $bindable(''), id, labelledby, labels }: Props = $props();

  let hour = $state('');
  let minute = $state('');

  const pad = (n: number) => String(n).padStart(2, '0');
  const HOURS = Array.from({ length: 24 }, (_, n) => pad(n));
  const MINUTES = Array.from({ length: 60 }, (_, n) => pad(n));

  const compose = () => (hour ? `${hour}:${minute || '00'}` : '');

  // A time written from outside (the example button) has to show in the two
  // fields; a value that already matches them is our own write.
  $effect(() => {
    const incoming = value;
    untrack(() => {
      if (incoming === compose()) return;
      const parts = /^(\d{2}):(\d{2})/.exec(incoming);
      hour = parts ? parts[1] : '';
      minute = parts ? parts[2] : '';
    });
  });

  function update() {
    if (!hour) minute = '';
    value = compose();
  }

  const FIELD =
    'h-12 w-full min-w-0 rounded-lg border border-input bg-background px-3 text-base focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none disabled:opacity-50';
</script>

<div role="group" aria-labelledby={labelledby} class="grid grid-cols-2 gap-2">
  <select {id} bind:value={hour} onchange={update} aria-label={labels.hour} class="{FIELD} {hour ? '' : 'text-muted-foreground/70'}">
    <option value="">{labels.hour}</option>
    {#each HOURS as h (h)}
      <option value={h}>{h}</option>
    {/each}
  </select>
  <select
    bind:value={minute}
    onchange={update}
    disabled={!hour}
    aria-label={labels.minute}
    class="{FIELD} {minute ? '' : 'text-muted-foreground/70'}"
  >
    <option value="">{labels.minute}</option>
    {#each MINUTES as m (m)}
      <option value={m}>{m}</option>
    {/each}
  </select>
</div>
