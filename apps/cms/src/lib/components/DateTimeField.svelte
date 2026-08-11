<script lang="ts">
  // Stands in for <input type="datetime-local">: a DateField for the day plus a
  // time input, submitting one "YYYY-MM-DDTHH:mm" value through a hidden input.
  //
  // Split rather than a segmented picker because these are registration windows
  // and event start/end times, which the team edits far more often by day than
  // by minute -- and a calendar is a much better day picker than a text segment.
  import { Input } from '$lib/components/ui/input';

  import DateField from './DateField.svelte';

  let {
    name,
    value = $bindable(''),
    id = name,
    placeholder = 'Pick a date',
    disabled = false
  }: {
    name: string;
    /** "YYYY-MM-DDTHH:mm", or "" for unset. */
    value?: string;
    id?: string;
    placeholder?: string;
    disabled?: boolean;
  } = $props();

  const DEFAULT_TIME = '09:00';

  let datePart = $state(value.slice(0, 10));
  let timePart = $state(value.slice(11, 16) || DEFAULT_TIME);

  // A time on its own is not a moment, so the combined value stays empty until a
  // day is chosen -- which is what makes the server store NULL rather than a
  // half-specified timestamp.
  $effect(() => {
    value = datePart ? `${datePart}T${timePart || DEFAULT_TIME}` : '';
  });
</script>

<input type="hidden" {name} {value} />

<div class="flex gap-2">
  <!-- Neither control carries a `name`: the hidden input above submits the one
       combined value, so the form data stays exactly as the action expects. -->
  <DateField bind:value={datePart} {id} {placeholder} {disabled} />
  <Input type="time" aria-label="Time" bind:value={timePart} {disabled} class="w-28 shrink-0" />
</div>
