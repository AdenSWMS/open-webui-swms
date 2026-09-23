<script lang="ts">
	import { goto } from '$app/navigation';
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import Search from '../icons/Search.svelte';
	import XMark from '../icons/XMark.svelte';
	import { getProjectsByUser } from '$lib/apis/projects';

	const i18n: any = getContext('i18n');
	type Project = {
		id: string;
		name: string;
		description?: string;
		counts?: {
			notes?: number;
			prompts?: number;
			chats?: number;
		};
		shared_chat_count?: number;
	};

	// Daten aus +page.server.js (nur getteten Projekten)
	export let data: { projects?: Project[] } = { projects: [] };

	let projectItems: Project[] = data?.projects ?? [];
	let query = '';

	const setProjects = async () => {
		const response = await getProjectsByUser(localStorage.token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (Array.isArray(response)) {
			projectItems = response;
		}
	};

	onMount(async () => {
		await setProjects();
	});

	$: projects = projectItems.filter((p) => p.name.toLowerCase().includes(query.toLowerCase()));
</script>

<div class="w-full min-w-0 space-y-1">
	<div class="flex flex-col h-full justify-between font-primary w-full">
		<div class="px-4 py-3 min-w-full">
			<!-- Header-Navigation im Open WebUI Style -->
			<div class="flex items-center justify-between pb-2">
				<div class="flex items-center space-x-4 text-sm font-medium">
					<div class="text-black dark:text-white">
						{$i18n.t('Projects')} <span class="text-gray-500 font-normal">{projects.length}</span>
					</div>
				</div>
			</div>

			<!-- Suchleiste im Workspace-Stil -->
			<div class="flex h-8 w-full items-center gap-2">
				<div class="flex min-w-0 flex-1 items-center">
					<div class="self-center ml-1 mr-3">
						<Search className="size-3.5" />
					</div>
					<input
						type="text"
						bind:value={query}
						aria-label={$i18n.t('Search projects')}
						placeholder={$i18n.t('Search projects')}
						maxlength="500"
						class="w-full rounded-r-xl bg-transparent py-1 text-sm outline-hidden"
					/>

					{#if query}
						<div class="self-center pl-1.5 translate-y-[0.5px] rounded-l-xl bg-transparent">
							<button
								type="button"
								class="rounded-full p-0.5 transition hover:bg-gray-100 dark:hover:bg-gray-900"
								aria-label={$i18n.t('Clear search')}
								on:click={() => (query = '')}
							>
								<XMark className="size-3" strokeWidth="2" />
							</button>
						</div>
					{/if}
				</div>
			</div>

			<!-- Inhaltsbereich / Liste -->
			{#if projects.length === 0}
				<!-- Empty State genau wie auf dem Screenshot -->
				<div class="flex flex-col items-center justify-center h-64 text-center my-12">
					<div class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-1">
						{$i18n.t('No projects found')}
					</div>
					<div class="text-xs text-gray-500 max-w-sm">
						{$i18n.t(
							'Try adjusting your search or contact an admin if you are missing access to a project.'
						)}
					</div>
				</div>
			{:else}
				<!-- Projektübersicht / Liste -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 my-2">
					{#each projects as project (project.id)}
						<button
							class="flex flex-col text-left p-3.5 rounded-xl border border-gray-100 dark:border-gray-850 bg-gray-50/50 dark:bg-gray-900/50 hover:bg-gray-100 dark:hover:bg-gray-900 transition cursor-pointer group"
							on:click={() => goto(`/projects/${project.id}`)}
						>
							<div class="flex items-center justify-between w-full mb-1">
								<div
									class="font-medium text-sm text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition"
								>
									{project.name}
								</div>
							</div>

							<div class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
								{project.description || $i18n.t('No description available')}
							</div>

							<!-- Schlanke Zähler für Ressourcen -->
							<div
								class="mt-auto pt-2 flex items-center gap-3 text-[11px] text-gray-400 border-t border-gray-200/40 dark:border-gray-800/40 w-full"
							>
								<!--<span>📝 {project.counts?.notes ?? 0}</span>
								<span>⚡ {project.counts?.prompts ?? 0}</span>-->
								<span>💬 {project.shared_chat_count ?? 0}</span>
							</div>
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
