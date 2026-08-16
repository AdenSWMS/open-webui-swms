import { WEBUI_API_BASE_URL } from '$lib/constants';

export interface UserInfoResponse {
	user_id: string;
	user_email: string;
	user_alias: string;
	user_role: string;
	spend: number;
	max_budget: number;
	models: string[];
	budget_duration?: string;
	budget_reset_at: string;
	created_at: string;
	updated_at: string;
	sso_user_id: string;
	teams: string[];
}

export const generateLiteLLMApiKey = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm/generate-litellm-api-key`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail ?? err;
			return error;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const deleteLiteLLMApiKey = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm/delete-litellm-api-key`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail ?? err;
			return error;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserInfo = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm/get-user-info`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail ?? err;
			return error;
		});

	if (error) {
		throw error;
	}

	return res;
};