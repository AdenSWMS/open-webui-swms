<script lang="ts">
	import { marked } from 'marked';
	import Fuse from 'fuse.js';

	import dayjs from '$lib/dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	import { flyAndScale } from '$lib/utils/transitions';

	import { createEventDispatcher, onMount, getContext, tick } from 'svelte';
	import { goto } from '$app/navigation';
    

	import {
		user,
		projects,
		selectedProject,
		mobile,
		temporaryChatEnabled,
		settings,
		config
	} from '$lib/stores';
	import { getProjectsByUser } from '$lib/apis/projects';

	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Check from '$lib/components/icons/Check.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import ChatBubbleOval from '$lib/components/icons/ChatBubbleOval.svelte';

	import ProjectItem from './ProjectItem.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let id = '';
	export let value = '';
	export let placeholder = $i18n.t('Select a project');
	export let searchEnabled = true;
	export let searchPlaceholder = $i18n.t('Search a project');

	export let items: {
		label: string;
		value: string;
		project: Project;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		[key: string]: any;
	}[] = [];

	export let className = 'w-[32rem]';
	export let triggerClassName = 'text-lg';

	let tagsContainerElement;

	let show = false;
	let triggerElement: HTMLElement | null = null;
	let contentElement: HTMLElement | null = null;
	let dropdownPosition = { top: 0, left: 0, width: 0 };

	const portal = (node: HTMLElement) => {
		document.body.appendChild(node);
		return {
			destroy() {
				node.remove();
			}
		};
	};

	const updatePosition = () => {
		if (!show || !triggerElement) return;
		const rect = triggerElement.getBoundingClientRect();
		dropdownPosition = {
			top: rect.bottom + 2,
			left: $mobile ? 8 : rect.left,
			width: $mobile ? window.innerWidth - 16 : 0
		};
	};

	const toggleOpen = () => {
		show = !show;
		if (show) {
			searchValue = '';
			listScrollTop = 0;
			resetView();
			updatePosition();
			window.setTimeout(() => document.getElementById('project-search-input')?.focus(), 0);
		} else {
			document.getElementById(`project-selector-${id}-button`)?.blur();
		}
	};

	const handlePointerDown = (e: PointerEvent) => {
		if (!show) return;
		const target = e.target as Node;
		if (
			(triggerElement && triggerElement.contains(target)) ||
			(contentElement && contentElement.contains(target))
		) {
			return;
		}
		show = false;
		document.getElementById(`project-selector-${id}-button`)?.blur();
	};

	const handleKeydown = (e: KeyboardEvent) => {
		if (show && e.key === 'Escape') {
			e.preventDefault();
			e.stopPropagation();
			show = false;
			document.getElementById(`project-selector-${id}-button`)?.blur();
		}
	};

	let tags = [];

	$: {
		const item = items.find((item) => item.value === value) ?? '';
		selectedProject.set(item);
	}

	let searchValue = '';

	let selectedTag = '';
	let selectedConnectionType = '';

	let selectedProjectIdx = 0;

	const fuse = new Fuse(
		items.map((item) => {
			const _item = {
				...item,
				projectName: item.project?.name,
				tags: (item.project?.tags ?? []).map((tag) => tag.name).join(' '),
				desc: item.project?.info?.meta?.description
			};
			return _item;
		}),
		{
			keys: ['value', 'tags', 'projectName'],
			threshold: 0.4
		}
	);

	const updateFuse = () => {
		if (fuse) {
			fuse.setCollection(
				items.map((item) => {
					const _item = {
						...item,
						projectName: item.project?.name,
						tags: (item.project?.tags ?? []).map((tag) => tag.name).join(' '),
						desc: item.project?.info?.meta?.description
					};
					return _item;
				})
			);
		}
	};

	$: if (items) {
		updateFuse();
	}

	$: filteredItems = (
		searchValue
			? fuse
					.search(searchValue)
					.map((e) => {
						return e.item;
					})
					.filter((item) => {
						if (selectedTag === '') {
							return true;
						}

						return (item.project?.tags ?? [])
							.map((tag) => tag.name.toLowerCase())
							.includes(selectedTag.toLowerCase());
					})
					.filter((item) => {
						if (selectedConnectionType === '') {
							return true;
						} else if (selectedConnectionType === 'local') {
							return item.project?.connection_type === 'local';
						} else if (selectedConnectionType === 'external') {
							return item.project?.connection_type === 'external';
						} else if (selectedConnectionType === 'direct') {
							return item.project?.direct;
						}
					})
			: items
					.filter((item) => {
						if (selectedTag === '') {
							return true;
						}
						return (item.project?.tags ?? [])
							.map((tag) => tag.name.toLowerCase())
							.includes(selectedTag.toLowerCase());
					})
					.filter((item) => {
						if (selectedConnectionType === '') {
							return true;
						} else if (selectedConnectionType === 'local') {
							return item.project?.connection_type === 'local';
						} else if (selectedConnectionType === 'external') {
							return item.project?.connection_type === 'external';
						} else if (selectedConnectionType === 'direct') {
							return item.project?.direct;
						}
					})
	).filter((item) => !(item.project?.info?.meta?.hidden ?? false));

	$: if (
		selectedTag !== undefined ||
		selectedConnectionType !== undefined ||
		searchValue !== undefined
	) {
		resetView();
	}

	const resetView = async () => {
		await tick();

		const selectedInFiltered = filteredItems.findIndex((item) => item.value === value);

		if (selectedInFiltered >= 0) {
			// The selected project is visible in the current filter
			selectedProjectIdx = selectedInFiltered;
		} else {
			// The selected project is not visible, default to first item in filtered list
			selectedProjectIdx = 0;
		}

		// Set the virtual scroll position so the selected item is rendered and centered
		const targetScrollTop = Math.max(0, selectedProjectIdx * ITEM_HEIGHT - 128 + ITEM_HEIGHT / 2);
		listScrollTop = targetScrollTop;

		await tick();

		if (listContainer) {
			listContainer.scrollTop = targetScrollTop;
		}

		await tick();
		const item = document.querySelector(`[data-arrow-selected="true"]`);
		item?.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
	};

	const ITEM_HEIGHT = 42;
	const OVERSCAN = 10;

	let listScrollTop = 0;
	let listContainer;

	$: visibleStart = Math.max(0, Math.floor(listScrollTop / ITEM_HEIGHT) - OVERSCAN);
	$: visibleEnd = Math.min(
		filteredItems.length,
		Math.ceil((listScrollTop + 256) / ITEM_HEIGHT) + OVERSCAN
	);
</script>

<svelte:window
	on:pointerdown={handlePointerDown}
	on:keydown={handleKeydown}
	on:resize={updatePosition}
/>

<div class="relative w-full">
	<button
		bind:this={triggerElement}
		class="relative w-full {($settings?.highContrastMode ?? false)
			? ''
			: 'outline-hidden focus:outline-hidden'}"
		aria-label={$selectedProject
			? $i18n.t('Selected project: {{projectName}}', { projectName: $selectedProject.label })
			: placeholder}
		aria-haspopup="listbox"
		aria-expanded={show}
		id="project-selector-{id}-button"
		type="button"
		on:click={toggleOpen}
	>
		<div
			class="flex w-full text-left px-0.5 bg-transparent truncate {triggerClassName} justify-between {($settings?.highContrastMode ??
			false)
				? 'dark:placeholder-gray-100 placeholder-gray-800'
				: 'placeholder-gray-400'}"
			on:mouseenter={async () => {
				projects.set(
					await getProjectsByUser(
						localStorage.token,
					)
				);
			}}
		>
			{#if $selectedProject}
				{$selectedProject.label}
			{:else}
				{placeholder}
			{/if}
			<ChevronDown className=" self-center ml-2 size-3" strokeWidth="2.5" />
		</div>
	</button>

	{#if show}
		<div
			use:portal
			bind:this={contentElement}
			style="position: fixed; z-index: 9999; top: {dropdownPosition.top}px; left: {dropdownPosition.left}px;{$mobile
				? ` width: ${dropdownPosition.width}px;`
				: ''}"
		>
			<div
				class="z-40 {$mobile
					? `w-full`
					: `${className}`} max-w-[calc(100vw-1rem)] justify-start rounded-2xl bg-white dark:bg-gray-850 dark:text-white shadow-lg outline-hidden"
				transition:flyAndScale
			>
				<slot>
					{#if searchEnabled}
						<div class="flex items-center gap-2.5 px-4.5 pt-3.5 mb-1.5">
							<Search className="size-4" strokeWidth="2.5" />

							<input
								id="projectk-search-input"
								bind:value={searchValue}
								class="w-full text-sm bg-transparent outline-hidden"
								placeholder={searchPlaceholder}
								autocomplete="off"
								aria-label={$i18n.t('Search In Projects')}
								on:keydown={(e) => {
									if (e.code === 'Enter' && filteredItems.length > 0) {
										value = filteredItems[selectedProjectIdx].value;
										show = false;
										return; // dont need to scroll on selection
									} else if (e.code === 'ArrowDown') {
										e.stopPropagation();
										selectedProjectIdx = Math.min(selectedProjectIdx + 1, filteredItems.length - 1);
									} else if (e.code === 'ArrowUp') {
										e.stopPropagation();
										selectedProjectIdx = Math.max(selectedProjectIdx - 1, 0);
									} else {
										// if the user types something, reset to the top selection.
										selectedProjectIdx = 0;
									}

									const item = document.querySelector(`[data-arrow-selected="true"]`);
									item?.scrollIntoView({
										block: 'center',
										inline: 'nearest',
										behavior: 'instant'
									});
								}}
							/>
						</div>
					{/if}

					<div class="px-2.5 group relative">
						{#if filteredItems.length === 0}
							{#if items.length === 0 && $user?.role === 'admin'}
								<div class="flex flex-col items-start justify-center py-6 px-4 text-start">
									<div class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
										{$i18n.t('No projects available')}
									</div>
								</div>
							{:else}
								<div class="">
									<div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
										{$i18n.t('No results found')}
									</div>
								</div>
							{/if}
						{:else}
							<!-- svelte-ignore a11y-no-static-element-interactions -->
							<div
								class="max-h-64 overflow-y-auto"
								role="listbox"
								aria-label={$i18n.t('Available projects')}
								bind:this={listContainer}
								on:scroll={() => {
									listScrollTop = listContainer.scrollTop;
								}}
							>
								<div style="height: {visibleStart * ITEM_HEIGHT}px;" />
								{#each filteredItems.slice(visibleStart, visibleEnd) as item, i (item.value)}
									{@const index = visibleStart + i}
									<ProjectItem
										{selectedProjectIdx}
										{item}
										{index}
										{value}
										onClick={() => {
											value = item.value;
											selectedProjectIdx = index;

											show = false;
										}}
									/>
								{/each}
								<div style="height: {(filteredItems.length - visibleEnd) * ITEM_HEIGHT}px;" />
							</div>
						{/if}
					</div>

					<div class="pb-2.5"></div>

					<div class="hidden w-[42rem]" />
					<div class="hidden w-[32rem]" />
				</slot>
			</div>
		</div>
	{/if}
</div>
