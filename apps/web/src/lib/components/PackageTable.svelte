<script lang="ts">
  import * as Table from '$lib/components/ui/table';
  import { m } from '$lib/paraglide/messages.js';
  import type { VenueDetail } from '$lib/api';
  import { formatPrice } from '$lib/utils';

  let { packages }: { packages: VenueDetail['packages'] } = $props();
</script>

<div class="overflow-hidden rounded-md border border-border bg-card">
  <Table.Root>
    <Table.Header class="bg-secondary">
      <Table.Row>
        <Table.Head class="font-semibold text-secondary-foreground">{m.packages_heading()}</Table.Head>
        <Table.Head class="font-semibold text-secondary-foreground">{m.packages_starting_price()}</Table.Head>
        <Table.Head class="font-semibold text-secondary-foreground">{m.packages_guests()}</Table.Head>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {#each packages as item (item.name)}
        <Table.Row>
          <Table.Cell class="py-4">
            <p class="font-semibold">{item.name}</p>
            <p class="mt-1 text-muted-foreground">{item.note}</p>
          </Table.Cell>
          <Table.Cell class="py-4 font-semibold">{formatPrice(item.price)}</Table.Cell>
          <Table.Cell class="py-4">{item.pax} pax</Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>
</div>
