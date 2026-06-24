<script>
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { page } from '$app/stores';

	const i18n = getContext('i18n');

	import { deleteProjectById, updateProjectById } from '$lib/apis/projects';

	import Pencil from '$lib/components/icons/Pencil.svelte';
	import EditProjectModal from './EditProjectModal.svelte';

	export let project = {
		name: 'Admins',
		user_ids: [1, 2, 3]
	};
	export let defaultPermissions = {};

	export let setProjects = () => {};

	let showEdit = false;

	const updateHandler = async (_project) => {
		const res = await updateProjectById(localStorage.token, project.id, _project).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Project updated successfully'));
			setProjects();
		}
	};

	const deleteHandler = async () => {
		const res = await deleteProjectById(localStorage.token, project.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Project deleted successfully'));
			setProjects();
		}
	};

	onMount(() => {
		const projectId = $page.url.searchParams.get('id');
		if (projectId && projectId === project.id) {
			showEdit = true;
		}
	});
</script>

<EditProjectModal
	bind:show={showEdit}
	edit
	{project}
	{defaultPermissions}
	tabs={['general', 'permissions', 'allowed_models', 'users']}
	onSubmit={updateHandler}
	onDelete={deleteHandler}
/>

<button
	class="flex space-x-4 cursor-pointer text-left w-full px-3.5 py-2.5 dark:hover:bg-gray-850/50 hover:bg-gray-50 transition rounded-2xl"
	on:click={() => {
		showEdit = true;
	}}
>
	<div class="w-full">
		<div class="flex items-center justify-between">
			<div class="flex-1">
				<div class="flex items-center gap-2">
					<div class="text-sm font-medium line-clamp-1">{project.name}</div>
				</div>

				<div class="flex items-center gap-2 mt-0.5 line-clamp-1">
					<div class="text-xs text-gray-500 shrink-0">
						{$i18n.t('{{COUNT}} members', { COUNT: project?.member_count ?? 0 })}
					</div>

					{#if project?.description}
						<div class="text-xs text-gray-500 line-clamp-1">
							{project.description}
						</div>
					{/if}
				</div>
			</div>

			<div class="flex self-center ml-2">
				<Pencil className="size-3.5" />
			</div>
		</div>
	</div>
</button>
