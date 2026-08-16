<script lang="ts">
	import { getContext } from 'svelte';
	import { selectedProject, settings } from '$lib/stores';
	import Folder from '$lib/components/icons/Folder.svelte';

	const i18n = getContext('i18n');

	export let placeholder = $i18n.t('Kein Projekt');
	export let className = '';
	export let labelClassName = 'text-sm font-medium';
</script>

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