<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	import { getProjectInfoById } from '$lib/apis/projects';
	import { getProjectSharedChatList } from '$lib/apis/chats';
	import ArrowLeft from '$lib/components/icons/ArrowLeft.svelte';
	import Folder from '$lib/components/icons/Folder.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n: any = getContext('i18n');

	type Project = {
		id: string;
		name: string;
		description?: string;
		shared_chat_count?: number;
	};

	type SharedChat = {
		chat_id: string;
		user_name?: string | null;
		share_id?: string | null;
		title: string;
		created_at: number;
		updated_at: number;
		time_range?: string;
	};

	let project: Project | null = null;
	let sharedChats: SharedChat[] = [];
	let loading = true;
	let pageNumber = 1;
	let hasMore = false;

	const loadProject = async () => {
		const projectId = $page.params.id;
		if (!projectId) {
			await goto('/projects');
			return;
		}

		loading = true;
		try {
			const [projectResponse, chatsResponse] = await Promise.all([
				getProjectInfoById(localStorage.token, projectId),
				getProjectSharedChatList(localStorage.token, projectId, pageNumber)
			]);

			project = projectResponse;
			sharedChats = chatsResponse ?? [];
			hasMore = sharedChats.length === 60;
		} catch (error) {
			toast.error(`${error}`);
		} finally {
			loading = false;
		}
	};

	const loadMore = async () => {
		if (!project || !hasMore) return;

		const nextPage = pageNumber + 1;
		try {
			const nextChats = await getProjectSharedChatList(localStorage.token, project.id, nextPage);
			sharedChats = [...sharedChats, ...(nextChats ?? [])];
			pageNumber = nextPage;
			hasMore = nextChats.length === 60;
		} catch (error) {
			toast.error(`${error}`);
		}
	};

	onMount(loadProject);
</script>

<div class="w-full min-w-0 px-4 py-4 md:px-8">
	<div class="mx-auto w-full max-w-5xl">
		<button
			class="mb-5 flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-gray-500 transition hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-800 dark:hover:text-white"
			type="button"
			on:click={() => goto('/projects')}
		>
			<ArrowLeft className="size-4" />
			{$i18n.t('Projects')}
		</button>

		{#if loading}
			<div class="flex h-64 items-center justify-center">
				<Spinner />
			</div>
		{:else if project}
			<header class="mb-6 border-b border-gray-200/70 pb-5 dark:border-gray-800">
				<div class="flex items-center gap-3">
					<div
						class="flex size-10 items-center justify-center rounded-xl bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"
					>
						<Folder className="size-5" />
					</div>
					<div>
						<h1 class="text-xl font-semibold text-gray-900 dark:text-white">{project.name}</h1>
						<p class="text-sm text-gray-500 dark:text-gray-400">
							{project.shared_chat_count ?? sharedChats.length}
							{$i18n.t('shared chats')}
						</p>
					</div>
				</div>
				{#if project.description}
					<p class="mt-4 max-w-2xl text-sm text-gray-600 dark:text-gray-400">
						{project.description}
					</p>
				{/if}
			</header>

			{#if sharedChats.length === 0}
				<div class="flex h-64 flex-col items-center justify-center text-center">
					<div class="mb-1 text-sm font-semibold text-gray-800 dark:text-gray-200">
						{$i18n.t('No shared chats in this project')}
					</div>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						{$i18n.t('Chats shared with this project will appear here.')}
					</div>
				</div>
			{:else}
				<div class="space-y-2">
					{#each sharedChats as chat (chat.chat_id)}
						<button
							class="group flex w-full items-center justify-between rounded-xl border border-gray-200/70 bg-white px-4 py-3 text-left transition hover:border-gray-300 hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-gray-700 dark:hover:bg-gray-850"
							type="button"
							disabled={!chat.share_id}
							on:click={() => chat.share_id && goto(`/s/${chat.share_id}`)}
						>
							<div class="min-w-0">
								<div
									class="truncate text-sm font-medium text-gray-900 group-hover:text-blue-600 dark:text-gray-100 dark:group-hover:text-blue-400"
								>
									{chat.title || $i18n.t('Untitled chat')}
								</div>
								<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
									{$i18n.t('Shared by')}
									{chat.user_name ?? $i18n.t('Unknown user')} ·
									{$i18n.t('Updated')}
									{chat.time_range ?? ''}
								</div>
							</div>
							<span class="text-xs text-gray-400">{$i18n.t('Open')}</span>
						</button>
					{/each}
				</div>

				{#if hasMore}
					<div class="mt-5 flex justify-center">
						<button
							class="rounded-lg px-4 py-2 text-sm text-gray-600 transition hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
							type="button"
							on:click={loadMore}
						>
							{$i18n.t('Load more')}
						</button>
					</div>
				{/if}
			{/if}
		{:else}
			<div class="py-16 text-center text-sm text-gray-500">{$i18n.t('Project not found')}</div>
		{/if}
	</div>
</div>
