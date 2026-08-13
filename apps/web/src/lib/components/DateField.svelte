<script lang="ts">
  // A shadcn/bits-ui calendar in a popover, standing in for <input type="date">.
  //
  // The picker owns a DateValue but the form owns a "YYYY-MM-DD" string, so the
  // real value is submitted through a hidden input -- the tour form's server action
  // keeps reading form.get(name) exactly as it did with a native date input.
  import { CalendarDate, type DateValue } from '@internationalized/date';
  import CalendarIcon from '@lucide/svelte/icons/calendar';

  import { Button } from '$lib/components/ui/button';
  import { Calendar } from '$lib/components/ui/calendar';
  import * as Popover from '$lib/components/ui/popover';

  let {
    name = '',
    value = $bindable(''),
    id = name,
    min = '',
    placeholder = 'Pick a date',
    disabled = false,
    class: className = 'w-full'
  }: {
    name?: string;
    value?: string;
    id?: string;
    /** Earliest selectable day, as "YYYY-MM-DD". */
    min?: string;
    placeholder?: string;
    disabled?: boolean;
    class?: string;
  } = $props();

  const pad = (part: number) => String(part).padStart(2, '0');

  function toDateValue(iso: string): CalendarDate | undefined {
    const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
    return match
      ? new CalendarDate(Number(match[1]), Number(match[2]), Number(match[3]))
      : undefined;
  }

  const toIso = (date: DateValue | undefined) =>
    date ? `${date.year}-${pad(date.month)}-${pad(date.day)}` : '';

  /** "18 Aug 2026" -- read off the parts, since new Date(iso) is parsed as UTC
   * midnight and lands a day early west of Greenwich. */
  function label(iso: string): string {
    const parts = toDateValue(iso);
    if (!parts) return '';
    const months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec'
    ];
    return `${parts.day} ${months[parts.month - 1]} ${parts.year}`;
  }

  let open = $state(false);

  // Derived, not synced with an effect: the string stays the single source of
  // truth, so a server-rendered value and one picked in the calendar cannot drift.
  const selected = $derived(toDateValue(value));
  const minValue = $derived(toDateValue(min));
</script>

{#if name}
  <input type="hidden" {name} {value} />
{/if}

<Popover.Root bind:open>
  <Popover.Trigger {id} {disabled}>
    {#snippet child({ props })}
      <!-- rounded-md overrides the button base's rounded-full: this trigger stands
           in for a text input and sits in a column of them, so it takes the input's
           corner rather than the pill shape real buttons use. -->
      <Button
        {...props}
        type="button"
        variant="outline"
        class={`${className} justify-start rounded-md font-normal ${
          value ? '' : 'text-muted-foreground'
        }`}
      >
        <CalendarIcon class="size-4" />
        {value ? label(value) : placeholder}
      </Button>
    {/snippet}
  </Popover.Trigger>
  <Popover.Content class="w-auto p-0">
    <Calendar
      type="single"
      value={selected}
      {minValue}
      captionLayout="dropdown"
      onValueChange={(next) => {
        value = toIso(next);
        open = false;
      }}
    />
  </Popover.Content>
</Popover.Root>
