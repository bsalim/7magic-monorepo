<script lang="ts">
  import { untrack } from 'svelte';
  import { enhance } from '$app/forms';
  import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';

  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Select from '$lib/components/ui/select';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as Tabs from '$lib/components/ui/tabs';
  import RichTextEditor from './RichTextEditor.svelte';

  export type ArticleValues = {
    title_id: string;
    title_en: string;
    slug: string;
    summary_id: string;
    summary_en: string;
    body_id: string;
    body_en: string;
    category: string;
    topic: string[];
    status: 'draft' | 'published' | 'archived';
    featured: boolean;
  };

  let {
    values,
    errors = {},
    message = '',
    submitLabel = 'Save article',
    cancelHref = '/articles',
    action = '',
    categories = [],
    articleId
  }: {
    values: ArticleValues;
    errors?: Partial<Record<keyof ArticleValues, string>>;
    message?: string;
    submitLabel?: string;
    cancelHref?: string;
    action?: string;
    categories?: { value: string; label: string }[];
    articleId?: number;
  } = $props();

  let status = $state<ArticleValues['status']>(untrack(() => values.status));
  let category = $state(untrack(() => values.category));
  let submitting = $state(false);

  const statusLabels: Record<ArticleValues['status'], string> = {
    draft: 'Draft',
    published: 'Published',
    archived: 'Archived'
  };

  const categoryLabel = $derived(
    categories.find((item) => item.value === category)?.label || category || 'Select a category'
  );

  // Slug is only auto-derived while creating; changing it later would break
  // published URLs, so an existing slug is left alone.
  const isNew = $derived(!values.slug);
  function slugify(text: string) {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }
  let slug = $state(untrack(() => values.slug));
  let titleEn = $state(untrack(() => values.title_en));
  const hasEnglish = $derived(titleEn.trim().length > 0);
  function onTitleInput(event: Event) {
    if (!isNew) return;
    slug = slugify((event.currentTarget as HTMLInputElement).value);
  }
</script>

{#snippet fieldError(text: string | undefined)}
  {#if text}
    <p class="text-xs font-medium text-destructive">{text}</p>
  {/if}
{/snippet}

<form
  method="POST"
  {action}
  class="space-y-6"
  use:enhance={() => {
    submitting = true;
    return async ({ update }) => {
      await update();
      submitting = false;
    };
  }}
>
  {#if message}
    <div
      class="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      <TriangleAlertIcon class="mt-0.5 size-4 shrink-0" />
      <span>{message}</span>
    </div>
  {/if}

  <input type="hidden" name="status" value={status} />
  <input type="hidden" name="category" value={category} />
  {#if articleId}
    <input type="hidden" name="article_id" value={articleId} />
  {/if}

  <Card.Root>
    <Card.Content class="space-y-5">
      <div class="grid gap-5 md:grid-cols-2">
        <div class="grid gap-2">
          <Label for="slug">Slug</Label>
          <Input id="slug" name="slug" bind:value={slug} required aria-invalid={!!errors.slug} />
          <p class="text-xs text-muted-foreground">Shared by both languages.</p>
          {@render fieldError(errors.slug)}
        </div>

        <div class="grid gap-2">
          <Label>Category</Label>
          <Select.Root type="single" bind:value={category}>
            <Select.Trigger class="w-full">{categoryLabel}</Select.Trigger>
            <Select.Content>
              {#each categories as option (option.value)}
                <Select.Item value={option.value} label={option.label}>{option.label}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
          {@render fieldError(errors.category)}
        </div>
      </div>

      <Tabs.Root value="id">
        <Tabs.List>
          <Tabs.Trigger value="id">Indonesian</Tabs.Trigger>
          <Tabs.Trigger value="en" class="gap-2">
            English
            {#if !hasEnglish}
              <span class="text-xs font-normal text-muted-foreground">(empty)</span>
            {/if}
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="id" class="mt-4 space-y-5">
          <div class="grid gap-2">
            <Label for="title_id">Title</Label>
            <Input
              id="title_id"
              name="title_id"
              value={values.title_id}
              required
              oninput={onTitleInput}
              aria-invalid={!!errors.title_id}
            />
            {@render fieldError(errors.title_id)}
          </div>

          <div class="grid gap-2">
            <Label for="summary_id">Summary</Label>
            <Textarea
              id="summary_id"
              name="summary_id"
              rows={3}
              value={values.summary_id}
              required
              aria-invalid={!!errors.summary_id}
            />
            {@render fieldError(errors.summary_id)}
          </div>

          <div class="grid gap-2">
            <Label for="body_id">Body</Label>
            <RichTextEditor
              value={values.body_id}
              name="body_id"
              id="body_id"
              uploadUrl={articleId ? `/articles/${articleId}/image-upload` : ''}
            />
            {@render fieldError(errors.body_id)}
          </div>
        </Tabs.Content>

        <Tabs.Content value="en" class="mt-4 space-y-5">
          <p class="rounded-md border bg-muted/40 px-3 py-2 text-sm text-muted-foreground">
            Optional. Leave empty and the English site shows the Indonesian version.
          </p>

          <div class="grid gap-2">
            <Label for="title_en">Title</Label>
            <Input
              id="title_en"
              name="title_en"
              bind:value={titleEn}
              aria-invalid={!!errors.title_en}
            />
            {@render fieldError(errors.title_en)}
          </div>

          <div class="grid gap-2">
            <Label for="summary_en">Summary</Label>
            <Textarea id="summary_en" name="summary_en" rows={3} value={values.summary_en} />
          </div>

          <div class="grid gap-2">
            <Label for="body_en">Body</Label>
            <RichTextEditor
              value={values.body_en}
              name="body_en"
              id="body_en"
              uploadUrl={articleId ? `/articles/${articleId}/image-upload` : ''}
            />
            {@render fieldError(errors.body_en)}
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </Card.Content>
  </Card.Root>

  <Card.Root>
    <Card.Header>
      <Card.Title>Publishing</Card.Title>
    </Card.Header>
    <Card.Content class="grid gap-5 md:grid-cols-3">
      <div class="grid gap-2">
        <Label>Status</Label>
        <Select.Root type="single" bind:value={status}>
          <Select.Trigger class="w-full">{statusLabels[status]}</Select.Trigger>
          <Select.Content>
            <Select.Item value="draft">Draft</Select.Item>
            <Select.Item value="published">Published</Select.Item>
            <Select.Item value="archived">Archived</Select.Item>
          </Select.Content>
        </Select.Root>
      </div>

      <div class="grid gap-2">
        <Label for="topic">Topics</Label>
        <Input
          id="topic"
          name="topic"
          value={values.topic.join(', ')}
          placeholder="venue, budget"
        />
        <p class="text-xs text-muted-foreground">Comma separated.</p>
      </div>

      <div class="flex items-end gap-2 pb-2">
        <Checkbox id="featured" name="featured" checked={values.featured} />
        <Label for="featured" class="font-normal">Featured</Label>
      </div>
    </Card.Content>
  </Card.Root>

  <div class="flex flex-wrap items-center justify-end gap-3">
    <Button href={cancelHref} variant="outline" type="button">Cancel</Button>
    <Button type="submit" disabled={submitting}>{submitting ? 'Saving…' : submitLabel}</Button>
  </div>
</form>
