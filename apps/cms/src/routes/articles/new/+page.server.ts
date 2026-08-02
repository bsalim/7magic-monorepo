import { fail, redirect } from '@sveltejs/kit';

import type { AdminArticleDetail } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import {
  articlePayloadFromForm,
  emptyArticle,
  validateArticlePayload,
  type ArticleFormErrors
} from '$lib/server/articleForm';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  return {
    values: emptyArticle(),
    errors: {} as ArticleFormErrors,
    message: ''
  };
};

export const actions: Actions = {
  default: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const formData = await request.formData();
    const values = articlePayloadFromForm(formData);
    const errors = validateArticlePayload(values);

    if (Object.keys(errors).length) {
      return fail(400, { errors, message: 'Fix the highlighted fields.', values });
    }

    let created: AdminArticleDetail;
    try {
      created = await apiFetch<AdminArticleDetail>('/api/v1/admin/articles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
        token: locals.token
      });
    } catch (error) {
      const apiErrors: ArticleFormErrors = {};
      if (error instanceof ApiRequestError && error.code === 'slug_conflict') {
        apiErrors.slug = error.message;
      }
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        errors: apiErrors,
        message:
          error instanceof ApiRequestError ? error.message : 'Unable to create the article.',
        values
      });
    }

    throw redirect(303, `/articles/${created.id}`);
  }
};
