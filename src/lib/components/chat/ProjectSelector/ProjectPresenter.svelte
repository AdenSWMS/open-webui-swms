<script lang="ts">
	import { getContext } from 'svelte';
	import { projects, selectedProject, settings } from '$lib/stores';
	import equal from 'fast-deep-equal';

	import Folder from '$lib/components/icons/Folder.svelte';
	import ProjectPresenter from './ProjectPresenter.svelte';

	const i18n = getContext('i18n');

	// Liste der ausgewählten Projekt-IDs (editierbar), z.B. ['', ''] für zwei Slots
	export let selectedProjects = [''];

	// Wenn true: editierbare Liste (Datei 2). Wenn false: kompaktes Badge (Datei 1).
	export let editable = false;

	// Nur relevant im Badge-Modus (editable = false)
	export let placeholder = $i18n.t('Kein Projekt');
	export let className = '';
	export let labelClassName = 'text-sm font-medium';

	// Reaktive Bereinigung: entfernte/ungültige Projekt-IDs zurücksetzen
	$: if (selectedProjects.length > 0 && $projects.length > 0) {
		const _selectedProjects = selectedProjects.map((project) =>
			$projects.map((p) => p.id).includes(project) ? project : ''
		);
		if (!equal(_selectedProjects, selectedProjects)) {
			selectedProjects = _selectedProjects;
		}
	}
</script>

{#if editable}
	<div class="flex flex-col w-full items-start">
		{#each selectedProjects as selectedProject, selectedProjectIdx}
			<div class="flex w-full max-w-fit">
				<div class="overflow-hidden w-full">
					<div class="max-w-full {($settings?.highContrastMode ?? false) ? 'm-1' : 'mr-1'}">
						<ProjectPresenter
							id={`${selectedProjectIdx}`}
							placeholder={$i18n.t('Wähle ein Projekt')}
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
{:else}
	<div class="inline-flex items-center gap-2 select-none {className}">
		<div
			class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 text-gray-700 dark:text-gray-300 truncate {($settings?.highContrastMode ?? false)
				? 'border-gray-400 dark:border-gray-600'
				: ''}"
			title={$selectedProject?.label ?? placeholder}
		>
			<Folder className="size-3.5 text-gray-500 dark:text-gray-400 shrink-0" />
			<span class="truncate {labelClassName}">
				{#if $selectedProject}
					{$selectedProject.name}
				{:else}
					<span class="text-gray-400 dark:text-gray-500">{placeholder}</span>
				{/if}
			</span>
		</div>
	</div>
{/if}