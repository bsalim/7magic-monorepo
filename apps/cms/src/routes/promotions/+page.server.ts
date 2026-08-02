import { fail, redirect } from '@sveltejs/kit';

import { ApiRequestError, apiFetch, getApiBaseUrl } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export type PromotionPopup = {
  id: number;
  active: boolean;
  title_id: string;
  title_en: string | null;
  body_id: string;
  body_en: string | null;
  banner_url: string | null;
  banner_key: string | null;
  cta_label_id: string | null;
  cta_label_en: string | null;
  cta_url: string | null;
  frequency: 'daily' | 'weekly' | 'once';
  updated_at: string | null;
};

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const popup = await apiFetch<PromotionPopup>('/api/v1/admin/promotion-popup', {
      token: locals.token
    });
    return { error: '', popup };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError
          ? error.message
          : 'Unable to load the promotion popup. Check the API server and try again.',
      popup: null
    };
  }
};

export const actions: Actions = {
  save: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const text = (key: string) => String(form.get(key) ?? '').trim();
    const optional = (key: string) => text(key) || null;

    const frequency = text('frequency');
    if (!['daily', 'weekly', 'once'].includes(frequency)) {
      return fail(400, { message: 'Choose how often the popup should appear.' });
    }

    const active = form.get('active') === 'on';
    const titleId = text('title_id');

    // An active popup with no title and no banner would render an empty box.
    if (active && !titleId && !text('banner_url')) {
      return fail(400, {
        message: 'Add an Indonesian title or a banner before switching the popup on.'
      });
    }

    try {
      await apiFetch('/api/v1/admin/promotion-popup', {
        method: 'PUT',
        token: locals.token,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          active,
          title_id: titleId,
          title_en: optional('title_en'),
          body_id: text('body_id'),
          body_en: optional('body_en'),
          banner_url: optional('banner_url'),
          banner_key: optional('banner_key'),
          cta_label_id: optional('cta_label_id'),
          cta_label_en: optional('cta_label_en'),
          cta_url: optional('cta_url'),
          frequency
        })
      });

      return { message: 'Promotion popup saved.' };
    } catch (error) {
      return fail(400, {
        message:
          error instanceof ApiRequestError ? error.message : 'Unable to save the promotion popup.'
      });
    }
  },

  upload: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const file = form.get('banner');
    if (!(file instanceof File) || file.size === 0) {
      return fail(400, { message: 'Choose a banner image to upload.' });
    }

    // Forwarded as multipart rather than through apiFetch's JSON path so the
    // API receives a real UploadFile.
    const upload = new FormData();
    upload.append('file', file);

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/admin/uploads/promotion-banner`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${locals.token}` },
        body: upload
      });

      if (!response.ok) {
        return fail(response.status, { message: 'Banner upload failed. Try a different image.' });
      }

      const result = (await response.json()) as { url: string; storage_key: string };
      return { message: 'Banner uploaded. Remember to save.', banner: result };
    } catch {
      return fail(500, { message: 'Banner upload failed. Check the API server and try again.' });
    }
  }
};
