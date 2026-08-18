<script lang="ts">
	import Fuse from 'fuse.js';
	import { getContext, tick } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import ProjectItem from './ProjectSelector/ProjectItem.svelte';
	import { user } from '$lib/stores';
	import { getProjectsByUser } from '$lib/apis/projects';

	const i18n = getContext('i18n');

	export let show = false;
	export let onSelect: (project: any) => void;

	export let searchEnabled = true;
	export let searchPlaceholder = $i18n.t('Suche nach Projekten');


	let rawProjects: any[] = [];
	let items: { name: string; id: string; project: any; [key: string]: any }[] = [];
	let loading = false;
	let searchValue = '';
	let selectedProjectIdx = 0;
	export let selectedProject: any = null;

	const ITEM_HEIGHT = 42;
	const OVERSCAN = 10;
	let listScrollTop = 0;
	let listContainer: HTMLElement;

	$: if (show) {
		loadProjects();
	}

	async function loadProjects() {
		loading = true;
		searchValue = '';
		listScrollTop = 0;
		selectedProjectIdx = 0;
		try {
			const response = await getProjectsByUser(localStorage.token);
			rawProjects = response ?? [];

			items = rawProjects.map((p) => ({
				name: p.name,
				id: p.id,
				project: p
			}));
		} catch (error) {
			console.error('Fehler beim Laden der Projekte:', error);
			items = [];
		} finally {
			loading = false;
			await tick();
			focusSearchInput();
		}
	}

	function focusSearchInput() {
		if (searchEnabled) {
			document.getElementById('modal-project-search-input')?.focus();
		}
	}

	let fuse: Fuse<any>;

	$: fuse = new Fuse(
		items.map((item) => ({
			...item,
			projectName: item.project?.name ?? item.label,
			tags: (item.project?.tags ?? []).map((t: any) => t.name).join(' '),
			desc: item.project?.info?.meta?.description
		})),
		{
			keys: ['value', 'tags', 'projectName'],
			threshold: 0.4
		}
	);

	$: filteredItems = (
		searchValue
			? fuse.search(searchValue).map((e) => e.item)
			: items
	).filter((item) => !(item.project?.info?.meta?.hidden ?? false));

	$: if (searchValue !== undefined) {
		resetView();
	}

	const resetView = async () => {
		await tick();
		selectedProjectIdx = 0;
		listScrollTop = 0;

		if (listContainer) {
			listContainer.scrollTop = 0;
		}
	};

	$: visibleStart = Math.max(0, Math.floor(listScrollTop / ITEM_HEIGHT) - OVERSCAN);
	$: visibleEnd = Math.min(
		filteredItems.length,
		Math.ceil((listScrollTop + 256) / ITEM_HEIGHT) + OVERSCAN
	);

	function confirmSelection(item: any | null) {
		onSelect(item);
	}

	function handleSkip() {
		confirmSelection(null);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.code === 'Enter' && filteredItems.length > 0) {
			e.preventDefault();
			const selectedItem = filteredItems[selectedProjectIdx];
			if (selectedItem) {
				confirmSelection(selectedItem);
			}
		} else if (e.code === 'ArrowDown') {
			e.preventDefault();
			selectedProjectIdx = Math.min(selectedProjectIdx + 1, filteredItems.length - 1);
			scrollToSelected();
		} else if (e.code === 'ArrowUp') {
			e.preventDefault();
			selectedProjectIdx = Math.max(selectedProjectIdx - 1, 0);
			scrollToSelected();
		}
	}

	async function scrollToSelected() {
		await tick();
		const item = document.querySelector(`[data-arrow-selected="true"]`);
		item?.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
	}
</script>

<Modal bind:show size="md">
	<div class="p-6 text-gray-900 dark:text-gray-100 flex flex-col max-h-[85vh]">
		<h3 class="text-xl font-semibold mb-1">
			{$i18n.t('Wähle ein Projekt')}
		</h3>
		<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
			{$i18n.t('Dieses Projets wird dem Chat zugewiesen. Dadurch werden genau die Modelle freigeschaltet, die für dieses Projekt vorgesehen sind. Wenn kein Projekt ausgewählt wird, dann wird der Chat keinem Projekt zugeordnet und es werden alle Modelle freigeschaltet.')}
		</p>

		{#if searchEnabled && !loading && items.length > 0}
			<div class="flex items-center gap-2.5 px-3 py-2 border border-gray-200 dark:border-gray-800 rounded-xl mb-3 bg-gray-50 dark:bg-gray-900">
				<Search className="size-4 text-gray-400" strokeWidth="2.5" />
				<input
					id="modal-project-search-input"
					bind:value={searchValue}
					class="w-full text-sm bg-transparent outline-hidden"
					placeholder={searchPlaceholder}
					autocomplete="off"
					aria-label={$i18n.t('Suche nach Projekten')}
					on:keydown={handleKeydown}
				/>
			</div>
		{/if}

		<div class="flex-1 overflow-hidden group relative min-h-[16rem]">
			{#if loading}
				<div class="flex items-center justify-center py-12 text-sm text-gray-500">
					{$i18n.t('Lade Projekte...')}
				</div>
			{:else if filteredItems.length === 0}
				{#if items.length === 0 && $user?.role === 'admin'}
					<div class="flex flex-col items-start justify-center py-6 px-4 text-start">
						<div class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
							{$i18n.t('Keine Projekte gefunden')}
						</div>
					</div>
				{:else}
					<div class="py-8 text-center text-sm text-gray-500">
						{$i18n.t('Keine Ergebnisse für die Suche gefunden')}
					</div>
				{/if}
			{:else}
				<div
					class="max-h-64 overflow-y-auto pr-1"
					role="listbox"
					aria-label={$i18n.t('Available projects')}
					bind:this={listContainer}
					on:scroll={() => {
						listScrollTop = listContainer.scrollTop;
					}}
				>
					<div style="height: {visibleStart * ITEM_HEIGHT}px;" />
					{#each filteredItems.slice(visibleStart, visibleEnd) as item, i (item.id)}
						{@const index = visibleStart + i}
						<ProjectItem
							{selectedProjectIdx}
							{item}
							{index}
							value={selectedProject?.id ?? ''}
							onClick={() => confirmSelection(item)}
						/>
					{/each}
					<div style="height: {(filteredItems.length - visibleEnd) * ITEM_HEIGHT}px;" />
				</div>
			{/if}
		</div>

		<div class="mt-6 flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
			<button
				type="button"
				on:click={handleSkip}
				class="px-4 py-2 text-sm rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
			>
				{$i18n.t('Überspringen')}
			</button>
			<button
				type="button"
				disabled={filteredItems.length === 0}
				on:click={() => confirmSelection(filteredItems[selectedProjectIdx])}
				class="px-4 py-2 text-sm font-medium rounded-lg bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200 transition-colors disabled:opacity-50"
			>
				{$i18n.t('Bestätigen')}
			</button>
		</div>
	</div>
</Modal>