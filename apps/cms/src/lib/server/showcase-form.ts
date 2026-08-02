import type { ShowcaseValues } from '$lib/components/ShowcaseForm.svelte';

/**
 * Turns the showcase form post into both the values to re-render on error and
 * the JSON payload the API expects.
 *
 * Shared by the create and edit actions so the two cannot drift on which
 * fields are optional or how blanks are normalised.
 */
export function readShowcaseForm(form: FormData): {
  values: ShowcaseValues;
  payload: Record<string, unknown>;
  errors: Partial<Record<keyof ShowcaseValues, string>>;
} {
  const read = (key: string) => String(form.get(key) ?? '').trim();

  const values: ShowcaseValues = {
    title_id: read('title_id'),
    title_en: read('title_en'),
    slug: read('slug'),
    body_id: read('body_id'),
    body_en: read('body_en'),
    showcase_date: read('showcase_date'),
    status: (read('status') || 'draft') as ShowcaseValues['status'],
    image_url: read('image_url'),
    image_storage_key: read('image_storage_key'),
    image_variants: read('image_variants')
  };

  const errors: Partial<Record<keyof ShowcaseValues, string>> = {};
  if (values.title_id.length < 2) {
    errors.title_id = 'An Indonesian title is required.';
  }

  let variants: unknown = null;
  if (values.image_variants) {
    try {
      variants = JSON.parse(values.image_variants);
    } catch {
      // A malformed hidden field should not block the save -- the image URL is
      // what the page actually renders; variants only add the srcset.
      variants = null;
    }
  }

  const payload: Record<string, unknown> = {
    title_id: values.title_id,
    title_en: values.title_en || null,
    body_id: values.body_id || null,
    body_en: values.body_en || null,
    showcase_date: values.showcase_date || null,
    status: values.status,
    image_url: values.image_url || null,
    image_storage_key: values.image_storage_key || null,
    image_variants: variants
  };

  // Only send a slug when one was typed; the API derives it from the title.
  if (values.slug) {
    payload.slug = values.slug;
  }

  return { values, payload, errors };
}
