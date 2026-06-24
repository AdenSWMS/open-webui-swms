<script>
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { WEBUI_NAME, config, user, showSidebar, knowledge } from '$lib/stores';
	import { WEBUI_BASE_URL } from '$lib/constants';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import UsersSolid from '$lib/components/icons/UsersSolid.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import EditProjectModal from './Projects/EditProjectModal.svelte';
	import ProjectItem from './Projects/ProjectItem.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Check from '$lib/components/icons/Check.svelte';
	import Select from '$lib/components/common/Select.svelte';
	import { createNewProject, getProjects, removeAllowedModelsFromProject, addAllowedModelsToProject, getAllowedModelsOfProject } from '$lib/apis/projects';
	import {
		getUserDefaultPermissions,
		getAllUsers,
		updateUserDefaultPermissions
	} from '$lib/apis/users';

	const i18n = getContext('i18n');

	let loaded = false;

	let projects = [];
	let modelId = null;

	let query = '';
	let sortBy = 'members';

	const sortItems = [
		{ value: 'name', label: $i18n.t('Name') },
		{ value: 'members', label: $i18n.t('Members') }
	];

	$: filteredProjects = projects
		.filter((project) => {
			if (query === '') {
				return true;
			} else {
				let name = project.name.toLowerCase();
				const q = query.toLowerCase();
				return name.includes(q);
			}
		})
		.sort((a, b) => {
			if (sortBy === 'name') {
				return a.name.localeCompare(b.name);
			} else if (sortBy === 'members') {
				return (b.member_count ?? 0) - (a.member_count ?? 0);
			}
			return 0;
		});

	let defaultPermissions = {};

	let showAddProjectModal = false;
	let showDefaultPermissionsModal = false;

	const setProjects = async () => {
		projects = await getProjects(localStorage.token);
	};

	const addProjectHandler = async (project) => {
		const res = await createNewProject(localStorage.token, project).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Project created successfully'));
			projects = await getProjects(localStorage.token);
		}
	};

	const updateDefaultPermissionsHandler = async (project) => {
		console.debug(project.permissions);

		const res = await updateUserDefaultPermissions(localStorage.token, project.permissions).catch(
			(error) => {
				toast.error(`${error}`);
				return null;
			}
		);

		if (res) {
			toast.success($i18n.t('Default permissions updated successfully'));
			defaultPermissions = await getUserDefaultPermissions(localStorage.token);
		}
	};

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
			return;
		}

		defaultPermissions = await getUserDefaultPermissions(localStorage.token);
		await setProjects();
		loaded = true;
	});
</script>

{#if loaded}
	<EditProjectModal
		bind:show={showAddProjectModal}
		edit={false}
		tabs={['general', 'permissions']}
		permissions={defaultPermissions}
		onSubmit={addProjectHandler}
	/>

	<div class="flex flex-col gap-1 px-1 mt-1.5 mb-3">
		<div class="flex justify-between items-center">
			<div class="flex items-center md:self-center text-xl font-medium px-0.5 gap-2 shrink-0">
				<div>
					{$i18n.t('Projects')}
				</div>

				<div class="text-lg font-medium text-gray-500 dark:text-gray-500">
					{projects.length}
				</div>
			</div>

			<div class="flex w-full justify-end gap-1.5">
				<button
					class="px-2 py-1.5 rounded-xl bg-black text-white dark:bg-white dark:text-black transition font-medium text-sm flex items-center"
					on:click={() => {
						showAddProjectModal = !showAddProjectModal;
					}}
				>
					<Plus className="size-3" strokeWidth="2.5" />

					<div class="hidden md:block md:ml-1 text-xs">{$i18n.t('New Project')}</div>
				</button>
			</div>
		</div>
	</div>

	<div
		class="py-2 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100/30 dark:border-gray-850/30"
	>
		<div class="flex items-center w-full space-x-2 py-0.5 px-3.5">
			<div class="flex flex-1">
				<div class="self-center ml-1 mr-3">
					<Search className="size-3.5" />
				</div>
				<input
					class="w-full text-sm py-1 rounded-r-xl outline-hidden bg-transparent"
					bind:value={query}
					aria-label={$i18n.t('Search Projects')}
					placeholder={$i18n.t('Search Projects')}
				/>
				{#if query}
					<div class="self-center pl-1.5 translate-y-[0.5px] rounded-l-xl bg-transparent">
						<button
							class="p-0.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-900 transition"
							aria-label={$i18n.t('Clear search')}
							on:click={() => {
								query = '';
							}}
						>
							<XMark className="size-3" strokeWidth="2" />
						</button>
					</div>
				{/if}
			</div>

			<Select
				bind:value={sortBy}
				items={sortItems}
				placeholder={$i18n.t('Sort by')}
				triggerClass="relative flex items-center gap-0.5 px-2.5 py-1.5 text-sm bg-gray-50 dark:bg-gray-850 rounded-xl shrink-0"
				align="end"
			>
				<svelte:fragment slot="trigger" let:selectedLabel>
					<span
						class="inline-flex h-input px-0.5 outline-hidden bg-transparent truncate placeholder-gray-400 focus:outline-hidden"
					>
						{selectedLabel}
					</span>
					<ChevronDown className="size-3.5" strokeWidth="2.5" />
				</svelte:fragment>

				<svelte:fragment slot="item" let:item let:selected>
					{item.label}
					{#if selected}
						<div class="ml-auto">
							<Check />
						</div>
					{/if}
				</svelte:fragment>
			</Select>
		</div>

		{#if filteredProjects.length !== 0}
			<div class="my-2 px-3 grid grid-cols-1 gap-1">
				{#each filteredProjects as project}
					<ProjectItem {project} {setProjects} {defaultPermissions} />
				{/each}
			</div>
		{:else}
			<div class="w-full h-full flex flex-col justify-center items-center my-16 mb-24">
				<div class="max-w-md text-center">
					<div class="text-3xl mb-3">👥</div>
					<div class="text-lg font-medium mb-1">{$i18n.t('No projects found')}</div>
					<div class="text-gray-500 text-center text-xs">
						{$i18n.t('Use projects to organize your work and assign model permissions.')}
					</div>
				</div>
			</div>
		{/if}
	</div>
{/if}
