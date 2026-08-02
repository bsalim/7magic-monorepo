import { ARTICLE_CATEGORIES } from '$lib/articleCategories';
import type { ArticleValues } from '$lib/components/ArticleForm.svelte';

export type ArticleFormErrors = Partial<Record<keyof ArticleValues, string>>;

export { ARTICLE_CATEGORIES };

export function emptyArticle(): ArticleValues {
  return {
    title_id: '',
    title_en: '',
    slug: '',
    summary_id: '',
    summary_en: '',
    body_id: '',
    body_en: '',
    category: 'wedding-venue',
    topic: [],
    status: 'draft',
    featured: false
  };
}

export function articlePayloadFromForm(formData: FormData): ArticleValues {
  const text = (key: string) => String(formData.get(key) ?? '').trim();

  return {
    title_id: text('title_id'),
    title_en: text('title_en'),
    slug: text('slug'),
    summary_id: text('summary_id'),
    summary_en: text('summary_en'),
    body_id: text('body_id'),
    body_en: text('body_en'),
    category: text('category') || 'wedding-venue',
    topic: text('topic')
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
    status: (['draft', 'published', 'archived'] as const).includes(
      text('status') as ArticleValues['status']
    )
      ? (text('status') as ArticleValues['status'])
      : 'draft',
    featured: formData.get('featured') === 'on'
  };
}

/** Quill leaves an empty paragraph behind when the editor is cleared. */
export function isEmptyHtml(html: string): boolean {
  return html.replace(/<[^>]*>/g, '').trim().length === 0;
}

export function validateArticlePayload(values: ArticleValues): ArticleFormErrors {
  const errors: ArticleFormErrors = {};

  if (values.title_id.length < 3) errors.title_id = 'Title needs at least 3 characters.';
  if (values.slug.length < 3) errors.slug = 'Slug needs at least 3 characters.';
  if (!/^[a-z0-9-]+$/.test(values.slug)) {
    errors.slug = 'Use lowercase letters, numbers and dashes only.';
  }
  if (values.summary_id.length < 3) errors.summary_id = 'Add a short summary.';
  if (isEmptyHtml(values.body_id)) errors.body_id = 'Write the Indonesian body.';
  if (!values.category) errors.category = 'Choose a category.';

  // English is optional, but a half-filled translation would publish a title
  // with no body behind it.
  const hasEnglishTitle = values.title_en.trim().length > 0;
  const hasEnglishBody = !isEmptyHtml(values.body_en);
  if (hasEnglishTitle !== hasEnglishBody) {
    const missing = hasEnglishTitle ? 'body_en' : 'title_en';
    errors[missing as keyof ArticleValues] =
      'Fill both the English title and body, or leave both empty.';
  }

  return errors;
}
