<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import { getProjectInfoById } from '$lib/apis/projects'; // Passe den Import-Pfad bei Bedarf an

	const i18n = getContext('i18n');

	export let show = false;
	export let project: any = null;

	let projectInfo: any = null;
	let loading = false;
	let loadedProjectId: string | null = null;

	// API aufrufen, wenn das Modal geöffnet wird oder sich das Projekt ändert
	$: if (show && project?.id && project.id !== loadedProjectId) {
		fetchProjectData(project.id);
	}

	async function fetchProjectData(id: string) {
		loading = true;
		loadedProjectId = id;
		try {
			// Falls der Token woanders her kommt (z.B. aus einem Store), hier anpassen
			const token = localStorage.getItem('token') || '';
			projectInfo = await getProjectInfoById(token, id);
		} catch (error) {
			console.error('Fehler beim Laden der Projekt-Infos:', error);
			projectInfo = null;
		} finally {
			loading = false;
		}
	}

	// Modelle sortieren
	$: rawModels = project?.project?.allowed_model_ids ?? [];
	$: models = [...rawModels].sort((a, b) => {
		const nameA = (a.name ?? a.id ?? a).toString().toLowerCase();
		const nameB = (b.name ?? b.id ?? b).toString().toLowerCase();
		return nameA.localeCompare(nameB);
	});

	// Benutzer aus den geladenen API-Daten (unterstützt verschiedene Datenstrukturen)
	$: projectUsers = projectInfo?.users ?? projectInfo?.members ?? projectInfo?.project?.users ?? [];
</script>

<Modal bind:show size="md">
	<div class="p-6 text-gray-900 dark:text-gray-100 flex flex-col max-h-[85vh] overflow-y-auto">
		{#if project}
			<!-- Header -->
			<div class="flex justify-between items-start mb-4">
				<div>
					<h3 class="text-xl font-bold">{project.name}</h3>
					{#if project.id}
						<span class="text-xs text-gray-400 font-mono">ID: {project.id}</span>
					{/if}
				</div>
			</div>

			<!-- Beschreibung -->
			<div class="mb-5">
				<h4 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
					{$i18n.t('Beschreibung')}
				</h4>
				<p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
					{project.project?.description || $i18n.t('Keine Beschreibung vorhanden.')}
				</p>
			</div>

			<!-- Modell-Liste -->
			<div class="mb-5">
				<div class="flex items-center justify-between mb-2">
					<h4 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
						{$i18n.t('Freigeschaltete Modelle')}
					</h4>
					{#if models.length > 0}
						<span class="text-xs text-gray-400 font-mono">({models.length})</span>
					{/if}
				</div>

				{#if models.length > 0}
					<div class="max-h-[160px] overflow-y-auto pr-1">
						<ul class="divide-y divide-gray-100 dark:divide-gray-800/60">
							{#each models as model}
								<li class="py-1.5 px-2 flex items-center justify-between text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/40 rounded transition-colors">
									<span class="font-medium truncate">
										{model.name ?? model.id ?? model}
									</span>
								</li>
							{/each}
						</ul>
					</div>
				{:else}
					<p class="text-xs text-gray-400 italic">
						{$i18n.t('Keine spezifischen Modelle zugewiesen.')}
					</p>
				{/if}
			</div>

			<!-- Nutzer-Liste (aus API-Info) -->
			<div class="mb-5">
				<div class="flex items-center justify-between mb-2">
					<h4 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
						{$i18n.t('Zugewiesene Nutzer')}
					</h4>
					{#if projectUsers.length > 0}
						<span class="text-xs text-gray-400 font-mono">({projectUsers.length})</span>
					{/if}
				</div>

				{#if loading}
					<p class="text-xs text-gray-400 animate-pulse">
						{$i18n.t('Lade Nutzerdaten...')}
					</p>
				{:else if projectUsers.length > 0}
					<div class="max-h-[160px] overflow-y-auto pr-1">
						<ul class="divide-y divide-gray-100 dark:divide-gray-800/60">
							{#each projectUsers as user}
								<li class="py-1.5 px-2 flex items-center justify-between text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/40 rounded transition-colors min-w-0">
									<div class="flex flex-col min-w-0 mr-2">
										<span class="font-medium truncate">
											{user.name ?? user.email ?? user.username ?? user.id ?? user}
										</span>
										{#if user.email && user.name}
											<span class="text-[11px] text-gray-400 dark:text-gray-500 truncate">
												{user.email}
											</span>
										{/if}
									</div>
									{#if user.role}
										<span class="text-[10px] text-gray-400 uppercase font-mono shrink-0">{user.role}</span>
									{/if}
								</li>
							{/each}
						</ul>
					</div>
				{:else}
					<p class="text-xs text-gray-400 italic">
						{$i18n.t('Keine Nutzer zugewiesen.')}
					</p>
				{/if}
			</div>

		{:else}
			<div class="py-8 text-center text-sm text-gray-500">
				{$i18n.t('Keine Projektdaten verfügbar.')}
			</div>
		{/if}

		<!-- Footer -->
		<div class="mt-6 flex justify-end pt-3 border-t border-gray-100 dark:border-gray-800">
			<button
				type="button"
				on:click={() => (show = false)}
				class="px-4 py-2 text-sm font-medium rounded-lg bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200 transition-colors cursor-pointer"
			>
				{$i18n.t('Schließen')}
			</button>
		</div>
	</div>
</Modal>