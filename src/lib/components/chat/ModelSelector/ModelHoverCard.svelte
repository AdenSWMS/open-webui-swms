<script lang="ts">
	export let model: any;
	export let info: any = null;

	export let costTier: string = 'FREE';
	export let costBadgeColor: string = '';


	$: tierLevel = costTier === 'FREE' ? 0 : costTier === '$' ? 1 : costTier === '$$' ? 2 : 3;

	let isHovered = false;
	let hoverTimeout: any;
	let anchorElement: HTMLDivElement;
	let cardPosition = { top: 0, left: 0 };

	const updateCardPosition = () => {
		if (!anchorElement) return;

		const rect = anchorElement.getBoundingClientRect();
		const cardWidth = 288;
		const gap = 8;
		const left =
			rect.right + gap + cardWidth <= window.innerWidth - gap
				? rect.right + gap
				: Math.max(gap, rect.left - cardWidth - gap);

		cardPosition = {
			top: Math.max(gap, Math.min(rect.top, window.innerHeight - 320 - gap)),
			left
		};
	};

	const handlePointerEnter = () => {
		hoverTimeout = setTimeout(() => {
			updateCardPosition();
			isHovered = true;
		}, 200);
	};

	const handlePointerLeave = () => {
		clearTimeout(hoverTimeout);
		isHovered = false;
	};
</script>

<div
	bind:this={anchorElement}
	class="relative inline-block w-full overflow-visible"
	role="presentation"
	on:pointerenter={handlePointerEnter}
	on:pointerleave={handlePointerLeave}
>
	<slot />

	{#if isHovered}
		<div
			class="fixed z-[10000] w-72 rounded-2xl border border-gray-200 bg-white/95 p-4 shadow-xl backdrop-blur-md transition-all duration-200 pointer-events-none dark:border-gray-800 dark:bg-gray-850"
			style={`top: ${cardPosition.top}px; left: ${cardPosition.left}px;`}
		>
			<div class="flex items-center gap-3 mb-3">
				<img
					src={model?.icon || '/favicon.png'}
					alt={model?.label}
					class="size-8 object-cover"
				/>
				<div class="min-w-0">
					<h4 class="font-semibold text-xs text-gray-900 dark:text-gray-100 truncate">
						{model?.label}
					</h4>
					<span class="text-[0.65rem] text-gray-500 capitalize">
						{info?.provider || 'Provider'}
					</span>
				</div>
			</div>

			{#if model?.description ?? model?.model?.info?.meta?.description}
				<p class="text-xs text-gray-600 dark:text-gray-400 mb-3 line-clamp-3 leading-relaxed">
					{model?.description ?? model?.model?.info?.meta?.description}
				</p>
			{/if}

			<div class="space-y-1.5 mb-3">
				<span class="text-[0.65rem] font-bold text-gray-400 uppercase tracking-wider"
					>Fähigkeiten</span
				>
				<div class="flex flex-wrap gap-1 mt-2">
					{#if info?.supports_vision}
						<span
							class="px-2 py-0.5 rounded-md text-[0.65rem] bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-medium"
						>
							Bildanalyse
						</span>
					{/if}
					{#if info?.supports_reasoning}
						<span
							class="px-2 py-0.5 rounded-md text-[0.65rem] bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-medium"
						>
							Reasoning
						</span>
					{/if}
                    {#if info?.supports_function_calling}
                        <span
                            class="px-2 py-0.5 rounded-md text-[0.65rem] bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-medium"
                        >
                            Tool Calling
                        </span>
                    {/if}
				</div>
			</div>
            {#if info && (info.input || info.output || costTier)}
                <div class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800/80">
                    
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-[0.65rem] font-bold text-gray-400 uppercase tracking-wider">
                            Kostenklasse
                        </span>
                        <span class="rounded-md border px-1.5 py-0.5 text-[0.65rem] font-bold tracking-wider uppercase {costBadgeColor}">
                            {costTier === 'FREE' ? 'Kostenlos' : `${costTier}`}
                        </span>
                    </div>

                    <div class="grid grid-cols-3 gap-1 mb-3">
                        <div class="h-1 rounded-full transition-all duration-300 {tierLevel >= 1 ? (tierLevel === 1 ? 'bg-emerald-500' : tierLevel === 2 ? 'bg-amber-500' : 'bg-red-500') : 'bg-gray-200 dark:bg-gray-900'}"></div>
                        <div class="h-1 rounded-full transition-all duration-300 {tierLevel >= 2 ? (tierLevel === 2 ? 'bg-amber-500' : 'bg-red-500') : 'bg-gray-200 dark:bg-gray-900'}"></div>
                        <div class="h-1 rounded-full transition-all duration-300 {tierLevel >= 3 ? 'bg-red-500' : 'bg-gray-200 dark:bg-gray-900'}"></div>
                    </div>

                    <div class="grid grid-cols-2 gap-1.5 text-[0.65rem]">
                        {#if info?.input}
                            <div class="flex flex-col rounded-lg bg-gray-50/80 dark:bg-gray-800/40 p-1.5 border border-gray-100 dark:border-gray-800">
                                <span class="text-gray-400 font-medium">Input / 1M</span>
                                <span class="font-semibold text-gray-800 dark:text-gray-200">{info.input}</span>
                            </div>
                        {/if}

                        {#if info?.output}
                            <div class="flex flex-col rounded-lg bg-gray-50/80 dark:bg-gray-800/40 p-1.5 border border-gray-100 dark:border-gray-800">
                                <span class="text-gray-400 font-medium">Output / 1M</span>
                                <span class="font-semibold text-gray-800 dark:text-gray-200">{info.output}</span>
                            </div>
                        {/if}

                        {#if info?.cacheRead}
                            <div class="flex flex-col rounded-lg bg-gray-50/50 dark:bg-gray-800/20 p-1.5 border border-gray-100/50 dark:border-gray-800/50">
                                <span class="text-gray-400 font-medium">Cache Read</span>
                                <span class="font-semibold text-gray-700 dark:text-gray-300">{info.cacheRead}</span>
                            </div>
                        {/if}

                        {#if info?.cacheWrite}
                            <div class="flex flex-col rounded-lg bg-gray-50/50 dark:bg-gray-800/20 p-1.5 border border-gray-100/50 dark:border-gray-800/50">
                                <span class="text-gray-400 font-medium">Cache Write</span>
                                <span class="font-semibold text-gray-700 dark:text-gray-300">{info.cacheWrite}</span>
                            </div>
                        {/if}
                    </div>

                </div>
            {/if}
		</div>
	{/if}
</div>
