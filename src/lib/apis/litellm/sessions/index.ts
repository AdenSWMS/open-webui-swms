import { WEBUI_API_BASE_URL } from '$lib/constants';

export interface UserSession {
	user_email: string;
	max_budget: number;
	spend: number;
	is_active: boolean;
}

export interface SessionResponse {
	status: string;
	session: UserSession | null;
	message?: string;
}

export interface CreateSessionPayload {
	max_budget: number;
	user_email?: string;
	ttl_seconds?: number;
}

/**
 * Holt die eigene Session des aktuell eingewählten Nutzers aus Redis
 */
export const getMySession = async (token: string): Promise<SessionResponse> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm/get-session`, {
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

/**
 * Erstellt oder aktualisiert eine Budget-Session in Redis
 */
export const createSession = async (
	token: string,
	payload: CreateSessionPayload
): Promise<SessionResponse> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm/create-session`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
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

/**
 * Löscht die eigene Session aus Redis
 */
export const deleteMySession = async (token: string): Promise<SessionResponse> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm/delete-session`, {
		method: 'DELETE',
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

/**
 * ADMIN: Löscht die Session eines spezifischen Nutzers aus Redis
 */
export const deleteUserSession = async (
	token: string,
	targetEmail: string
): Promise<SessionResponse> => {
	let error = null;

	const res = await fetch(
		`${WEBUI_API_BASE_URL}/litellm/user/${encodeURIComponent(targetEmail)}`,
		{
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${token}`
			}
		}
	)
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