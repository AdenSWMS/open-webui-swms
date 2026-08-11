import { WEBUI_API_BASE_URL } from '$lib/constants';

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

export const getSpendForMessage = async (token: string, model: string, usage: any) => {
	let error = null;

	const payload = {
		completion_response: {
			model: model,
			usage: {
				prompt_tokens: usage?.input_tokens,
				completion_tokens: usage?.output_tokens,
				total_tokens: usage?.total_tokens,
			}
		}
	};

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm/spend-for-message`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		// 2. Payload im Body mitsenden
		body: JSON.stringify(payload)
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