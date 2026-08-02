
<script lang="ts">
	import { getContext, tick } from 'svelte';
	import dayjs from '$lib/dayjs';

	import { mobile, settings, user } from '$lib/stores';
	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { copyToClipboard, sanitizeResponseContent } from '$lib/utils';
	import ArrowUpTray from '$lib/components/icons/ArrowUpTray.svelte';
	import Check from '$lib/components/icons/Check.svelte';
	import EllipsisHorizontal from '$lib/components/icons/EllipsisHorizontal.svelte';
	import { toast } from 'svelte-sonner';
	import Tag from '$lib/components/icons/Tag.svelte';
	import Label from '$lib/components/icons/Label.svelte';

	const i18n = getContext('i18n');

	export let selectedProjectIdx: number = -1;
	export let item: any = {};
	export let index: number = -1;
	export let value: string = '';

	export let onClick: () => void = () => {};

	let showMenu = false;
</script>

<button
	role="option"
	aria-selected={value === item.value}
	aria-label={$i18n.t('Select {{projectName}} project', { projectName: item.name })}
	class="flex group/item w-full text-left font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-hidden transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl cursor-pointer data-highlighted:bg-muted {index ===
	selectedProjectIdx
		? 'bg-gray-100 dark:bg-gray-800 group-hover:bg-transparent'
		: ''}"
	data-arrow-selected={index === selectedProjectIdx}
	data-value={item.value}
	on:click={() => {
		onClick();
	}}
>
	<div class="flex flex-col flex-1 gap-1.5">
		<!-- {#if (item?.model?.tags ?? []).length > 0}
			<div
				class="flex gap-0.5 self-center items-start h-full w-full translate-y-[0.5px] overflow-x-auto scrollbar-none"
			>
				{#each item.model?.tags.sort((a, b) => a.name.localeCompare(b.name)) as tag}
					<Tooltip content={tag.name} className="flex-shrink-0">
						<div
							class=" text-xs font-semibold px-1 rounded-sm uppercase bg-gray-500/20 text-gray-700 dark:text-gray-200"
						>
							{tag.name}
						</div>
					</Tooltip>
				{/each}
			</div>
		{/if} -->

		<div class="flex items-center gap-2">
			<div class="flex items-center min-w-fit">

			<div class="flex items-center">
				<Tooltip content={`${item.name} (${item.id})`} placement="top-start">
					<div class="line-clamp-1">
						{item.name}
					</div>
				</Tooltip>
			</div>
		</div>
	</div>
</button>
