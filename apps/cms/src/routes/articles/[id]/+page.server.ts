import { fail, redirect } from '@sveltejs/kit';

import type { AdminArticleDetail } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import {
  articlePayloadFromForm,
  validateArticlePayload,
  type ArticleFormErrors
} from '$lib/server/articleForm';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const article = await apiFetch<AdminArticleDetail>(
      `/api/v1/admin/articles/${params.id}`,
      { token: locals.token }
    );

    return {
      error: '',
      article,
      values: {
        title_id: article.title_id,
        title_en: article.title_en,
        slug: article.slug,
        summary_id: article.summary_id,
        summary_en: article.summary_en,
        body_id: article.body_id,
        body_en: article.body_en,
        category: article.category_slug,
        topic: article.topic,
        status: (['draft', 'published', 'archived'] as const).includes(
          article.status as 'draft' | 'published' | 'archived'
        )
          ? (article.status as 'draft' | 'published' | 'archived')
          : 'draft',
        featured: article.featured
      }
    };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError ? error.message : 'Unable to load the article.',
      article: null,
      values: null
    };
  }
};

export const actions: Actions = {
  save: async ({ locals, params, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const values = articlePayloadFromForm(await request.formData());
    const errors = validateArticlePayload(values);
    if (Object.keys(errors).length) {
      return fail(400, {
        errors,
        message: 'Fix the highlighted fields.',
        values
      });
    }

    try {
      await apiFetch<AdminArticleDetail>(`/api/v1/admin/articles/${params.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
        token: locals.token
      });
      return { errors: {}, message: 'Article saved.', values };
    } catch (error) {
      const apiErrors: ArticleFormErrors = {};
      if (error instanceof ApiRequestError && error.code === 'slug_conflict') {
        apiErrors.slug = error.message;
      }
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        errors: apiErrors,
        message: error instanceof ApiRequestError ? error.message : 'Unable to save the article.',
        values
      });
    }
  }
};
