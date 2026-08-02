import {
  createTable,
  type RowData,
  type TableOptions,
  type TableOptionsResolved,
  type TableState
} from '@tanstack/table-core';

/**
 * Reactive Svelte 5 wrapper around `@tanstack/table-core`.
 * State updaters funnel through `$state`-backed options so the table
 * re-renders when sorting / filtering / pagination change.
 *
 * Mirrors the official shadcn-svelte data-table helper.
 */
export function createSvelteTable<TData extends RowData>(options: TableOptions<TData>) {
  const resolvedOptions = mergeObjects(
    {
      state: {},
      onStateChange() {},
      renderFallbackValue: null,
      mergeOptions: (
        defaultOptions: TableOptions<TData>,
        newOptions: Partial<TableOptions<TData>>
      ) => {
        return mergeObjects(defaultOptions, newOptions);
      }
    },
    options
  ) as unknown as TableOptionsResolved<TData>;

  const table = createTable(resolvedOptions);
  let state = $state<Partial<TableState>>(table.initialState);

  function updateOptions() {
    table.setOptions((prev) => {
      return mergeObjects(prev, options, {
        state: mergeObjects(state, options.state || {}),
        onStateChange: (updater: unknown) => {
          if (updater instanceof Function) state = updater(state);
          else state = mergeObjects(state, updater as Partial<TableState>);

          options.onStateChange?.(updater as never);
        }
      });
    });
  }

  updateOptions();

  $effect.pre(() => {
    updateOptions();
  });

  return table;
}

type MaybeThunk<T extends object> = T | (() => T | null | undefined);

/**
 * Lazily merges objects/thunks, returning a proxy so reads stay reactive.
 * The return type is taken from the first source — later sources override
 * its properties at read time.
 */
function mergeObjects<T extends object>(
  source: MaybeThunk<T>,
  ...overrides: MaybeThunk<object>[]
): T {
  const sources: MaybeThunk<object>[] = [source, ...overrides];
  const target = {};

  return new Proxy(target, {
    get(_, prop) {
      for (let i = sources.length - 1; i >= 0; i--) {
        const s = unwrap(sources[i]);
        if (s && prop in s) {
          return s[prop as keyof typeof s];
        }
      }
      return undefined;
    },
    has(_, prop) {
      for (let i = sources.length - 1; i >= 0; i--) {
        const s = unwrap(sources[i]);
        if (s && prop in s) return true;
      }
      return false;
    },
    ownKeys() {
      const keys = new Set<string | symbol>();
      for (const source of sources) {
        const s = unwrap(source);
        if (s) for (const k of Reflect.ownKeys(s)) keys.add(k);
      }
      return Array.from(keys);
    },
    getOwnPropertyDescriptor(_, prop) {
      for (let i = sources.length - 1; i >= 0; i--) {
        const s = unwrap(sources[i]);
        if (s && prop in s) {
          return {
            configurable: true,
            enumerable: true,
            value: s[prop as keyof typeof s],
            writable: true
          };
        }
      }
      return undefined;
    }
  }) as T;
}

function unwrap<T extends object>(source: MaybeThunk<T>): T | null | undefined {
  return typeof source === 'function' ? (source as () => T)() : source;
}
