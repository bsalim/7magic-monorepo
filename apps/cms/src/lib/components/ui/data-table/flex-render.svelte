<script lang="ts" generics="TProps extends Record<string, any>">
  import type { Component } from 'svelte';
  import { RenderComponentConfig, RenderSnippetConfig } from './render-helpers.js';

  let {
    content,
    context
  }: {
    content:
      | string
      | number
      | null
      | undefined
      | RenderComponentConfig<Component<any>>
      | RenderSnippetConfig<TProps>
      | ((context: TProps) => unknown);
    context: TProps;
  } = $props();
</script>

{#if typeof content === 'string' || typeof content === 'number'}
  {content}
{:else if content instanceof Function}
  {@const result = content(context)}
  {#if result instanceof RenderComponentConfig}
    {@const { component: Comp, props } = result}
    <Comp {...props} />
  {:else if result instanceof RenderSnippetConfig}
    {@const { snippet, params } = result}
    {@render snippet(params)}
  {:else}
    {result}
  {/if}
{:else if content instanceof RenderComponentConfig}
  {@const { component: Comp, props } = content}
  <Comp {...props} />
{:else if content instanceof RenderSnippetConfig}
  {@const { snippet, params } = content}
  {@render snippet(params)}
{:else}
  {content}
{/if}
