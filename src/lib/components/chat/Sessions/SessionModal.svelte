<script lang="ts">
	import { getContext, createEventDispatcher, onDestroy } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import {
		getMySession,
		createSession,
		deleteMySession,
		deleteUserSession
	} from '$lib/apis/litellm/sessions';
	import type { UserSession } from '$lib/apis/litellm/sessions';
	import { toast } from 'svelte-sonner';

	export let show = false;
	export let currentUser: any = null;

	const dispatch = createEventDispatcher();

	let session: UserSession | null = null;
	let loading = false;
	let backgroundRefreshing = false;
	let submitting = false;

	let autoRefreshInterval: ReturnType<typeof setInterval> | null = null;
	let timerInterval: ReturnType<typeof setInterval> | null = null;
	let remainingSeconds: number | null = null;

	// Formular-Felder
	let maxBudgetInput: number = 5.0;
	let targetEmailToDelete: string = '';
	let ttlHoursInput: number | null = 24;

	$: isAdmin = currentUser?.role === 'admin';


	$: if (show) {
		loadSessionData();
		startAutoRefresh();
		startTimer();
	} else {
		stopAutoRefresh();
		stopTimer();
	}

	function startAutoRefresh() {
		stopAutoRefresh();
		// API Polling alle 60 Sekunden
		autoRefreshInterval = setInterval(() => {
			loadSessionData(true);
		}, 30000);
	}

	function stopAutoRefresh() {
		if (autoRefreshInterval) {
			clearInterval(autoRefreshInterval);
			autoRefreshInterval = null;
		}
	}

	function startTimer() {
		stopTimer();
		timerInterval = setInterval(() => {
			if (remainingSeconds !== null && remainingSeconds > 0) {
				remainingSeconds -= 1;
			} else if (remainingSeconds === 0) {
				session = null;
				remainingSeconds = null;
			}
		}, 1000);
	}

	function stopTimer() {
		if (timerInterval) {
			clearInterval(timerInterval);
			timerInterval = null;
		}
	}

	onDestroy(() => {
		stopAutoRefresh();
		stopTimer();
	});

	async function loadSessionData(isBackground = false) {
		if (isBackground) {
			backgroundRefreshing = true;
		} else {
			loading = true;
		}

		try {
			const token = localStorage.getItem('token') || '';
			const res = await getMySession(token);
			session = res?.session ?? null;

			if (session) {
				if (!submitting) {
					maxBudgetInput = session.max_budget;
				}

				const rawSession = session as any;
				if (rawSession.expires_at) {
					const expireTime = new Date(rawSession.expires_at).getTime();
					const now = Date.now();
					remainingSeconds = Math.max(0, Math.floor((expireTime - now) / 1000));
				} else if (rawSession.ttl_seconds !== undefined) {
					remainingSeconds = rawSession.ttl_seconds;
				} else if (rawSession.ttl !== undefined) {
					remainingSeconds = rawSession.ttl;
				} else {
					remainingSeconds = null;
				}
			} else {
				remainingSeconds = null;
			}
		} catch (err) {
			console.error('Fehler beim Laden der Redis-Session:', err);
		} finally {
			loading = false;
			backgroundRefreshing = false;
		}
	}

	function formatTTL(seconds: number | null): string {
		if (seconds === null || seconds <= 0) return 'Abgelaufen / Kein TTL';

		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		const s = seconds % 60;

		const parts = [];
		if (h > 0) parts.push(`${h}h`);
		parts.push(`${m.toString().padStart(2, '0')}m`);
		parts.push(`${s.toString().padStart(2, '0')}s`);

		return parts.join(' ');
	}

	async function handleSaveSession() {
		submitting = true;
		try {
			const token = localStorage.getItem('token') || '';
			// Erstellt/Aktualisiert IMMER nur die eigene Session
			const payload = {
				max_budget: Number(maxBudgetInput),
				ttl_seconds: ttlHoursInput ? ttlHoursInput * 3600 : undefined
			};

			const res = await createSession(token, payload);
			session = res?.session ?? null;
			toast.success(`Eigenes Session-Budget von $${Number(maxBudgetInput).toFixed(2)} aktiviert!`);
			loadSessionData(true);
			dispatch('update');
		} catch (err: any) {
			toast.error(err?.message || 'Fehler beim Erstellen der Session.');
		} finally {
			submitting = false;
		}
	}

	async function handleDeleteSession(targetEmail?: string) {
		submitting = true;
		try {
			const token = localStorage.getItem('token') || '';
			if (targetEmail && targetEmail.trim()) {
				await deleteUserSession(token, targetEmail.trim());
				toast.success(`Session für ${targetEmail.trim()} wurde gelöscht.`);
				targetEmailToDelete = '';
			} else {
				await deleteMySession(token);
				session = null;
				remainingSeconds = null;
				toast.success('Deine eigene Session wurde gelöscht.');
			}
			dispatch('update');
		} catch (err: any) {
			toast.error(err?.message || 'Fehler beim Löschen der Session.');
		} finally {
			submitting = false;
		}
	}
</script>

<Modal bind:show size="md">
	<div class="p-6 md:p-8 space-y-6">
		<!-- Header -->
		<div
			class="flex items-center justify-between pb-4 border-b border-gray-100 dark:border-gray-800"
		>
			<div class="flex items-center gap-3">
				<div
					class="p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800/50 text-xl"
				>
					⚡
				</div>
				<div>
					<h3 class="text-lg font-bold leading-tight text-gray-900 dark:text-gray-100">
						Session Budget Guard
					</h3>
					<p class="text-xs text-gray-500 dark:text-gray-400">
						Echtzeit-Kostenkontrolle für LiteLLM
					</p>
				</div>
			</div>

			<div class="flex items-center gap-3">
				{#if backgroundRefreshing}
					<span class="flex h-2.5 w-2.5 relative" title="Aktualisiere Daten...">
						<span
							class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
						></span>
						<span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
					</span>
				{/if}
				<button
					type="button"
					class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
					on:click={() => (show = false)}
				>
					✕
				</button>
			</div>
		</div>

		<!-- Body -->
		{#if loading && !session}
			<div class="flex flex-col justify-center items-center py-12 text-gray-500 text-sm gap-3">
				<div
					class="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"
				></div>
				<span>Lade Session-Informationen...</span>
			</div>
		{:else}
			<div class="space-y-6">
				<!-- Aktueller Status -->
				<div
					class="p-5 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-gray-200/80 dark:border-gray-700/60 shadow-sm space-y-4"
				>
					<div class="flex justify-between items-center">
						<span
							class="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400"
						>
							Eigene Session
						</span>
						{#if currentUser?.email}
							<span
								class="text-xs px-2.5 py-1 rounded-md bg-gray-200/60 dark:bg-gray-700/60 font-mono text-gray-700 dark:text-gray-300"
							>
								{currentUser.email}
							</span>
						{/if}
					</div>

					{#if session}
						<div class="flex items-baseline justify-between">
							<div>
								<span class="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
									${session.spend.toFixed(5)}
								</span>
								<span class="text-gray-500 dark:text-gray-400 text-sm font-medium">
									/ ${session.max_budget.toFixed(5)} USD
								</span>
							</div>
							<span
								class="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800"
							>
								Aktiv
							</span>
						</div>

						<!-- Fortschrittsbalken -->
						<div>
							<div
								class="w-full bg-gray-200 dark:bg-gray-700 h-2.5 rounded-full overflow-hidden p-0.5"
							>
								<div
									class="bg-emerald-500 h-full rounded-full transition-all duration-500 ease-out"
									style="width: {Math.min(100, (session.spend / session.max_budget) * 100)}%"
								></div>
							</div>
							<div class="flex justify-between text-[11px] text-gray-400 mt-1.5 font-medium">
								<span>Verbraucht: {((session.spend / session.max_budget) * 100).toFixed(1)}%</span>
								<span
									>Verbleibend: ${Math.max(0, session.max_budget - session.spend).toFixed(4)}</span
								>
							</div>
						</div>

						<!-- TTL Restzeit Anzeigebox -->
						{#if remainingSeconds !== null}
							<div
								class="flex items-center justify-between pt-2 border-t border-gray-200/60 dark:border-gray-700/50 text-xs"
							>
								<span class="text-gray-500 dark:text-gray-400 flex items-center gap-1.5">
									⏳ Verbleibende Ablaufzeit:
								</span>
								<span
									class="font-mono font-semibold px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200/60 dark:border-amber-800/40"
								>
									{formatTTL(remainingSeconds)}
								</span>
							</div>
						{/if}
					{:else}
						<div class="py-2 text-center sm:text-left">
							<p class="text-sm font-medium text-gray-700 dark:text-gray-300">
								Keine aktive Budget-Session vorhanden.
							</p>
							<p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
								Erstelle unten ein neues Limit, um Kosten-Schutz zu aktivieren.
							</p>
						</div>
					{/if}
				</div>

				<!-- Formular zum Erstellen / Ändern des EIGENEN Budgets -->
				<div class="space-y-4">
					<h4 class="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
						Eigenes Session-Budget festlegen
					</h4>
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<label
								for="max-budget"
								class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5"
							>
								Maximales Budget ($ USD)
							</label>
							<input
								id="max-budget"
								type="number"
								step="0.5"
								min="0.1"
								bind:value={maxBudgetInput}
								class="w-full px-3.5 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition text-gray-900 dark:text-gray-100"
							/>
						</div>

						<div>
							<label
								for="ttl-hours"
								class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5"
							>
								Ablaufzeit (Stunden)
							</label>
							<input
								id="ttl-hours"
								type="number"
								min="1"
								bind:value={ttlHoursInput}
								placeholder="z.B. 24"
								class="w-full px-3.5 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition text-gray-900 dark:text-gray-100"
							/>
						</div>
					</div>
				</div>

				<!-- Admin-Bereich: Nur zum gezielten Löschen bei Nutzer-Problemen -->
				{#if isAdmin}
					<div
						class="p-4 bg-rose-50/50 dark:bg-rose-950/20 rounded-2xl border border-rose-200/60 dark:border-rose-900/40 space-y-3"
					>
						<div>
							<span class="text-xs font-bold text-rose-900 dark:text-rose-300">
								🛠️ Admin-Sonderfunktion: Nutzer-Session zurücksetzen
							</span>
							<p class="text-[11px] text-rose-700/80 dark:text-rose-400/80 mt-0.5">
								Nutze dies nur, wenn ein Nutzer Probleme mit einer fehlerhaften Session hat.
							</p>
						</div>
						<div class="flex gap-2">
							<input
								type="email"
								bind:value={targetEmailToDelete}
								placeholder="user@beispiel.de"
								class="flex-1 px-3.5 py-1.5 bg-white dark:bg-gray-950 border border-rose-200 dark:border-rose-900/60 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-rose-500/50 transition"
							/>
							<button
								type="button"
								on:click={() => handleDeleteSession(targetEmailToDelete)}
								disabled={submitting || !targetEmailToDelete.trim()}
								class="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-xl transition disabled:opacity-50 whitespace-nowrap"
							>
								Fremde Session löschen
							</button>
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- Footer / Actions -->
		<div class="flex gap-3 justify-end pt-4 border-t border-gray-100 dark:border-gray-800">
			{#if session}
				<button
					type="button"
					on:click={() => handleDeleteSession()}
					disabled={submitting}
					class="px-4 py-2 bg-red-50 hover:bg-red-100 dark:bg-red-950/40 dark:hover:bg-red-900/60 text-red-600 dark:text-red-300 border border-red-200 dark:border-red-800/50 text-xs font-medium rounded-xl transition disabled:opacity-50"
				>
					Meine Session Löschen
				</button>
			{/if}

			<button
				type="button"
				on:click={handleSaveSession}
				disabled={submitting}
				class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow-md hover:shadow-emerald-500/20 transition disabled:opacity-50"
			>
				{submitting ? 'Speichere...' : 'Eigenes Budget Aktivieren'}
			</button>
		</div>
	</div>
</Modal>
