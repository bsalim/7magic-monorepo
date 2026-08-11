<script lang="ts">
  // A shadcn/bits-ui calendar in a popover, standing in for <input type="date">.
  //
  // The picker owns a DateValue but the form owns a "YYYY-MM-DD" string, so the
  // real value is submitted through a hidden input. That keeps every server
  // action reading form.get(name) exactly as it did with a native date input --
  // and keeps working without JS beyond the picker itself.
  import { CalendarDate, type DateValue } from '@internationalized/date';
  import CalendarIcon from '@lucide/svelte/icons/calendar';

  import { Button } from '$lib/components/ui/button';
  import { Calendar } from '$lib/components/ui/calendar';
  import * as Popover from '$lib/components/ui/popover';
  import { formatDate } from '$lib/format-date';

  let {
    name = '',
    value = $bindable(''),
    id = name,
    min = '',
    placeholder = 'Pick a date',
    disabled = false,
    class: className = 'w-full'
  }: {
    /** Omit when a parent submits the value itself, as DateTimeField does. */
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

  let open = $state(false);

  // Derived, not synced with an effect: the string is the single source of truth,
  // so a value set by the server render and one picked in the calendar cannot
  // drift apart.
  const selected = $derived(toDateValue(value));
  const minValue = $derived(toDateValue(min));
</script>

{#if name}
  <input type="hidden" {name} {value} />
{/if}

<Popover.Root bind:open>
  <Popover.Trigger {id} {disabled}>
    {#snippet child({ props })}
      <Button
        {...props}
        type="button"
        variant="outline"
        class={`${className} justify-start font-normal ${value ? '' : 'text-muted-foreground'}`}
      >
        <CalendarIcon class="size-4" />
        {value ? formatDate(value) : placeholder}
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
