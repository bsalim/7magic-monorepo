/* eslint-disable @typescript-eslint/no-explicit-any */
import type { Component, Snippet } from 'svelte';

/**
 * A helper class to make it easy to identify Svelte components in
 * `cell` and `header` definitions of column defs.
 */
export class RenderComponentConfig<TComponent extends Component<any>> {
  constructor(
    public component: TComponent,
    public props: Record<string, any> | undefined = undefined
  ) {}
}

/**
 * A helper class to make it easy to identify Svelte Snippets in
 * `cell` and `header` definitions of column defs.
 */
export class RenderSnippetConfig<TProps> {
  constructor(
    public snippet: Snippet<[TProps]>,
    public params: TProps
  ) {}
}

/**
 * Use to render a Svelte component within a column header or cell.
 */
export function renderComponent<
  TComponent extends Component<any>,
  TProps extends Record<string, any>
>(component: TComponent, props: TProps) {
  return new RenderComponentConfig(component, props);
}

/**
 * Use to render a Svelte Snippet within a column header or cell.
 */
export function renderSnippet<TProps>(snippet: Snippet<[TProps]>, params: TProps) {
  return new RenderSnippetConfig(snippet, params);
}
