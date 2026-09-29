<script lang="ts">
	import Modal from '$lib/components/common/Modal.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import { roadmap, type RoadmapItem } from './roadmap';

	export let show = false;
	export let items: RoadmapItem[] = roadmap;

	const GAP = 220;
	const PAD = 120;
	const HEIGHT = 360;
	const TOP = 130;
	const BOTTOM = 230;

	const statusColor = {
		done: 'bg-emerald-500',
		'in-progress': 'bg-blue-500 animate-pulse',
		planned: 'bg-gray-300 dark:bg-gray-600'
	};

	$: points = items.map((item, i) => ({ item, x: PAD + i * GAP, y: i % 2 ? BOTTOM : TOP }));
	$: width = PAD * 2 + Math.max(items.length - 1, 0) * GAP;
	$: path = points
		.map((p, i) => {
			if (i === 0) return `M ${p.x - PAD} ${p.y} L ${p.x} ${p.y}`;
			const prev = points[i - 1];
			const mx = (prev.x + p.x) / 2;
			return `C ${mx} ${prev.y}, ${mx} ${p.y}, ${p.x} ${p.y}`;
		})
		.join(' ') + (points.length ? ` L ${width} ${points.at(-1).y}` : '');

	const onWheel = (e: WheelEvent) => {
		if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
			e.preventDefault();
			(e.currentTarget as HTMLElement).scrollLeft += e.deltaY;
		}
	};
</script>

<Modal bind:show size="xl">
	<div class="flex justify-between dark:text-gray-300 px-5 pt-4 pb-2">
		<div class="text-lg font-medium self-center">Roadmap</div>
		<button
			class="self-center rounded-lg p-1 text-gray-500 transition hover:bg-gray-50 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
			aria-label="Close"
			on:click={() => (show = false)}
		>
			<XMark className="size-4" />
		</button>
	</div>

	<div class="overflow-x-auto scrollbar-none pb-4" on:wheel|nonpassive={onWheel}>
		<div class="relative" style="width: {width}px; height: {HEIGHT}px;">
			<svg class="absolute inset-0" {width} height={HEIGHT}>
				<path
					d={path}
					fill="none"
					stroke-width="4"
					stroke-dasharray="10 8"
					stroke-linecap="round"
					class="stroke-gray-300 dark:stroke-gray-700"
				/>
			</svg>

			{#each points as { item, x, y }}
				<div
					class="absolute size-5 -translate-x-1/2 -translate-y-1/2 rounded-full ring-4 ring-white dark:ring-gray-900 {statusColor[
						item.status
					]}"
					style="left: {x}px; top: {y}px;"
				/>
				<div
					class="absolute w-48 -translate-x-1/2 text-center {y === TOP
						? '-translate-y-full'
						: ''}"
					style="left: {x}px; top: {y === TOP ? y - 20 : y + 20}px;"
				>
					{#if item.date}
						<div class="text-xs text-gray-500">{item.date}</div>
					{/if}
					<div class="text-sm font-medium dark:text-gray-100">{item.title}</div>
					{#if item.description}
						<div class="text-xs text-gray-500 mt-0.5">{item.description}</div>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</Modal>
