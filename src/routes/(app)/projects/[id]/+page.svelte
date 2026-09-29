<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	import { getModels } from '$lib/apis';
	import { getProjectSharedChatList } from '$lib/apis/chats';
	import { getAllowedModelsOfProject, getProjectInfoById } from '$lib/apis/projects';
	import ArrowLeft from '$lib/components/icons/ArrowLeft.svelte';
	import ChatBubbles from '$lib/components/icons/ChatBubbles.svelte';
	import Cube from '$lib/components/icons/Cube.svelte';
	import Folder from '$lib/components/icons/Folder.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Users from '$lib/components/icons/Users.svelte';

	const i18n: any = getContext('i18n');

	type Project = {
		id: string;
		name: string;
		description?: string;
		shared_chat_count?: number;
		allowed_model_ids?: string[];
	};

	type ProjectUser = {
		name?: string | null;
		email?: string | null;
	};

	type Model = {
		id: string;
		name?: string;
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

	type Section = 'overview' | 'chats';

	let project: Project | null = null;
	let projectUsers: ProjectUser[] = [];
	let allowedModels: Model[] = [];
	let sharedChats: SharedChat[] = [];
	let activeSection: Section = 'overview';
	let loading = true;
	let pageNumber = 1;
	let hasMore = false;

	$: allowedModelIds = project?.allowed_model_ids ?? [];
	$: memberCount = projectUsers.length;
	$: modelCount = allowedModels.length;

	const loadProject = async () => {
		const projectId = $page.params.id;
		if (!projectId) {
			await goto('/projects');
			return;
		}

		loading = true;
		pageNumber = 1;
		try {
			const [projectResponse, chatsResponse, allowedModelIdsResponse, modelsResponse] = await Promise.all([
				getProjectInfoById(localStorage.token, projectId),
				getProjectSharedChatList(localStorage.token, projectId, pageNumber),
				getAllowedModelsOfProject(localStorage.token, projectId),
				getModels(localStorage.token)
			]);

			project = projectResponse;
			projectUsers = projectResponse?.users ?? [];
			const modelIds = allowedModelIdsResponse ?? [];
			const models = modelsResponse ?? [];
			allowedModels = modelIds.map((id: string) => {
				const model = models.find((item: Model) => item.id === id);
				return model ?? { id, name: id };
			});
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

	const initials = (user: ProjectUser) =>
		(user.name || user.email || '?')
			.split(' ')
			.map((part) => part[0])
			.join('')
			.slice(0, 2)
			.toUpperCase();

	onMount(loadProject);
</script>

<div class="w-full min-w-0 px-4 py-4 md:px-8">
	<div class="mx-auto w-full max-w-6xl">
		<button
			class="mb-5 flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-gray-500 transition hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-800 dark:hover:text-white"
			type="button"
			on:click={() => goto('/projects')}
		>
			<ArrowLeft className="size-4" />
			{$i18n.t('Projects')}
		</button>

		{#if loading}
			<div class="flex h-64 items-center justify-center"><Spinner /></div>
		{:else if project}
			<header class="mb-6 rounded-2xl border border-gray-200/70 bg-white p-5 dark:border-gray-800 dark:bg-gray-900 md:p-7">
				<div class="flex flex-wrap items-start justify-between gap-5">
					<div class="flex min-w-0 items-center gap-4">
						<div class="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">
							<Folder className="size-6" />
						</div>
						<div class="min-w-0">
							<h1 class="truncate text-2xl font-semibold text-gray-900 dark:text-white">{project.name}</h1>
							{#if project.description}
								<p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">{project.description}</p>
							{/if}
						</div>
					</div>
					<div class="flex gap-2 text-xs text-gray-500 dark:text-gray-400">
						<span class="rounded-full bg-gray-100 px-3 py-1.5 dark:bg-gray-800">{memberCount} {$i18n.t('members')}</span>
						<span class="rounded-full bg-gray-100 px-3 py-1.5 dark:bg-gray-800">{modelCount} {$i18n.t('models')}</span>
					</div>
				</div>
			</header>

			<div class="mb-6 flex gap-1 overflow-x-auto border-b border-gray-200/70 dark:border-gray-800" role="tablist">
				<button
					class="flex min-w-fit items-center gap-2 border-b-2 px-3 py-3 text-sm transition {activeSection === 'overview' ? 'border-gray-900 font-medium text-gray-900 dark:border-white dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-white'}"
					type="button"
					role="tab"
					aria-selected={activeSection === 'overview'}
					on:click={() => (activeSection = 'overview')}
				>
					<Users className="size-4" />
					{$i18n.t('Project overview')}
				</button>
				<button
					class="flex min-w-fit items-center gap-2 border-b-2 px-3 py-3 text-sm transition {activeSection === 'chats' ? 'border-gray-900 font-medium text-gray-900 dark:border-white dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-white'}"
					type="button"
					role="tab"
					aria-selected={activeSection === 'chats'}
					on:click={() => (activeSection = 'chats')}
				>
					<ChatBubbles className="size-4" />
					{$i18n.t('Shared chats')}
					<span class="opacity-60">{project.shared_chat_count ?? sharedChats.length}</span>
				</button>
			</div>

			{#if activeSection === 'overview'}
				<div class="grid gap-5 lg:grid-cols-2">
					<section class="rounded-2xl border border-gray-200/70 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
						<div class="mb-4 flex items-center justify-between">
							<h2 class="flex items-center gap-2 font-medium text-gray-900 dark:text-white"><Users className="size-4" />{$i18n.t('Project members')}</h2>
							<span class="text-xs text-gray-400">{memberCount}</span>
						</div>
						{#if projectUsers.length > 0}
							<div class="space-y-2">
								{#each projectUsers as user}
									<div class="flex items-center gap-3 rounded-xl px-2 py-2 hover:bg-gray-50 dark:hover:bg-gray-800">
										<div class="flex size-9 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-medium text-blue-700 dark:bg-blue-900/40 dark:text-blue-200">{initials(user)}</div>
										<div class="min-w-0"><div class="truncate text-sm text-gray-900 dark:text-gray-100">{user.name || $i18n.t('Unknown user')}</div><div class="truncate text-xs text-gray-500 dark:text-gray-400">{user.email || ''}</div></div>
									</div>
								{/each}
							</div>
						{:else}<p class="text-sm text-gray-500">{$i18n.t('No members in this project')}</p>{/if}
					</section>

					<section class="rounded-2xl border border-gray-200/70 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
						<div class="mb-4 flex items-center justify-between"><h2 class="flex items-center gap-2 font-medium text-gray-900 dark:text-white"><Cube className="size-4" />{$i18n.t('Allowed models')}</h2><span class="text-xs text-gray-400">{modelCount}</span></div>
						{#if allowedModels.length > 0}
							<div class="flex flex-wrap gap-2">{#each allowedModels as model}<span class="rounded-lg bg-gray-100 px-3 py-2 text-sm text-gray-700 dark:bg-gray-800 dark:text-gray-200">{model.name || model.id}</span>{/each}</div>
						{:else}<p class="text-sm text-gray-500">{$i18n.t('No specific models are allowed')}</p>{/if}
					</section>
				</div>
			{:else if sharedChats.length === 0}
				<div class="flex h-64 flex-col items-center justify-center text-center"><div class="mb-1 text-sm font-semibold text-gray-800 dark:text-gray-200">{$i18n.t('No shared chats in this project')}</div><div class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Chats shared with this project will appear here.')}</div></div>
			{:else}
				<div class="space-y-2">{#each sharedChats as chat (chat.chat_id)}<button class="group flex w-full items-center justify-between rounded-xl border border-gray-200/70 bg-white px-4 py-3 text-left transition hover:border-gray-300 hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-gray-700" type="button" disabled={!chat.share_id} on:click={() => chat.share_id && goto(`/s/${chat.share_id}`)}><div class="min-w-0"><div class="truncate text-sm font-medium text-gray-900 group-hover:text-blue-600 dark:text-gray-100 dark:group-hover:text-blue-400">{chat.title || $i18n.t('Untitled chat')}</div><div class="mt-1 text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Shared by')} {chat.user_name ?? $i18n.t('Unknown user')} · {$i18n.t('Updated')} {chat.time_range ?? ''}</div></div><span class="text-xs text-gray-400">{$i18n.t('Open')}</span></button>{/each}</div>
				{#if hasMore}<div class="mt-5 flex justify-center"><button class="rounded-lg px-4 py-2 text-sm text-gray-600 transition hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800" type="button" on:click={loadMore}>{$i18n.t('Load more')}</button></div>{/if}
			{/if}
		{:else}<div class="py-16 text-center text-sm text-gray-500">{$i18n.t('Project not found')}</div>{/if}
	</div>
</div>
