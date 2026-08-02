import { fail, redirect } from '@sveltejs/kit';

import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

type ChangePasswordResponse = {
  status: string;
  revoked_sessions: number;
};

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  return {};
};

export const actions: Actions = {
  default: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const currentPassword = String(form.get('current_password') ?? '');
    const newPassword = String(form.get('new_password') ?? '');
    const confirmPassword = String(form.get('confirm_password') ?? '');

    if (!currentPassword || !newPassword) {
      return fail(400, { message: 'Fill in your current password and the new one.' });
    }

    // The confirmation field never reaches the API, so this is the only guard
    // against a typo locking the account behind a password nobody knows.
    if (newPassword !== confirmPassword) {
      return fail(400, { message: 'The new password and its confirmation do not match.' });
    }

    try {
      const result = await apiFetch<ChangePasswordResponse>('/api/v1/auth/change-password', {
        method: 'POST',
        token: locals.token,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      const revoked = result.revoked_sessions;
      return {
        success: true,
        message:
          revoked > 0
            ? `Password updated. ${revoked} other session${revoked === 1 ? '' : 's'} signed out.`
            : 'Password updated.'
      };
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        message:
          error instanceof ApiRequestError
            ? error.message
            : 'Unable to reach the API. Check the API server and try again.'
      });
    }
  }
};
