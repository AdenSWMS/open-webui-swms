<script lang="ts">
	import { projects, showSettings, settings, user, mobile, config } from '$lib/stores';
	import { onMount, tick, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import Selector from './ProjectSelector/Selector.svelte';
	import Tooltip from '../common/Tooltip.svelte';

	import { updateUserSettings } from '$lib/apis/users';
	import equal from 'fast-deep-equal';
	const i18n = getContext('i18n');

	export let selectedProjects = [''];
	

	$: if (selectedProjects.length > 0 && $projects.length > 0) {
		const _selectedProjects = selectedProjects.map((project) =>
			$projects.map((p) => p.id).includes(project) ? project : ''
		);

		if (!equal(_selectedProjects, selectedProjects)) {
			selectedProjects = _selectedProjects;
		}
	}
</script>

<div class="flex flex-col w-full items-start">
	{#each selectedProjects as selectedProject, selectedProjectIdx}
		<div class="flex w-full max-w-fit">
			<div class="overflow-hidden w-full">
				<div class="max-w-full {($settings?.highContrastMode ?? false) ? 'm-1' : 'mr-1'}">
					<Selector
						id={`${selectedProjectIdx}`}
						placeholder={$i18n.t('Select a project')}
						items={$projects.map((project) => ({
							value: project.id,
							label: project.name,
							model: project
						}))}
						bind:value={selectedProject}
					/>
				</div>
			</div>

		</div>
	{/each}
</div>
