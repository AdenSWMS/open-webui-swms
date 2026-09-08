<script lang="ts">
	export let dailyModelData: Array<{ date: string; model: string; spend: number }> = [];
	export let modelUsage: Array<{ model: string; spend: number }> = [];

	const COLORS = ['#38bdf8', '#818cf8', '#f43f5e', '#fbbf24', '#34d399', '#a78bfa'];

	$: dates = [...new Set(dailyModelData.map((d) => d.date))];
	$: models = [...new Set(dailyModelData.map((d) => d.model))];

	$: dailyTotals = dates.map((date) =>
		dailyModelData.filter((d) => d.date === date).reduce((sum, item) => sum + item.spend, 0)
	);
	$: maxDailySpend = Math.max(...dailyTotals, 0.01);

	$: totalModelSpend = modelUsage.reduce((sum, item) => sum + item.spend, 0);

	$: sortedModelUsage = [...modelUsage].sort((a, b) => b.spend - a.spend);

	$: donutSegments = (() => {
		let accumulatedPercent = 0;
		return sortedModelUsage.map((m, idx) => {
			const percent = totalModelSpend > 0 ? m.spend / totalModelSpend : 0;
			const dasharray = `${percent * 100} ${100 - percent * 100}`;
			const offset = 100 - accumulatedPercent * 100 + 25; 
			accumulatedPercent += percent;
			return {
				...m,
				color: COLORS[idx % COLORS.length],
				dasharray,
				offset,
				percent: (percent * 100).toFixed(1)
			};
		});
	})();
</script>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 my-6">
	<div class="lg:col-span-2 border border-gray-200 dark:border-gray-800 rounded-xl p-5 bg-white dark:bg-gray-900">
		<h4 class="font-semibold text-sm mb-6 text-gray-500 uppercase tracking-wider">
			Ausgaben pro Tag & Modell ($)
		</h4>

		<div class="h-64 flex items-end gap-6 pt-6 pb-2 border-b border-gray-200 dark:border-gray-800 px-4">
			{#each dates as date, i}
				{@const dayData = dailyModelData.filter((d) => d.date === date)}
				{@const dayTotal = dailyTotals[i]}
				{@const barHeightPercent = (dayTotal / maxDailySpend) * 100}

				<div class="flex-1 flex flex-col items-center h-full justify-end group relative">
					<div class="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-900 text-white text-xs py-1 px-2 rounded pointer-events-none z-10 whitespace-nowrap shadow-lg">
						{date}: ${dayTotal.toFixed(4)}
					</div>

					<div class="w-full max-w-[48px] rounded-t overflow-hidden bg-gray-100 dark:bg-gray-800 flex flex-col-reverse" style="height: {barHeightPercent}%;">
						{#each dayData as item}
							{@const modelIdx = models.indexOf(item.model)}
							{@const segmentHeight = dayTotal > 0 ? (item.spend / dayTotal) * 100 : 0}
							<div
								style="height: {segmentHeight}%; background-color: {COLORS[modelIdx % COLORS.length]};"
								title="{item.model}: ${item.spend.toFixed(4)}"
							></div>
						{/each}
					</div>

					<span class="text-xs text-gray-400 mt-2 font-medium">{date.slice(5)}</span>
				</div>
			{/each}
		</div>

		<div class="flex flex-wrap gap-4 mt-4 justify-center">
			{#each models as model, idx}
				<div class="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-300">
					<span class="w-3 h-3 rounded-full" style="background-color: {COLORS[idx % COLORS.length]};"></span>
					<span>{model}</span>
				</div>
			{/each}
		</div>
	</div>

	<div class="border border-gray-200 dark:border-gray-800 rounded-xl p-5 bg-white dark:bg-gray-900 flex flex-col items-center justify-between">
		<h4 class="font-semibold text-sm mb-2 text-gray-500 uppercase tracking-wider w-full">
			Gesamtausgaben pro Modell
		</h4>

		<div class="relative w-44 h-44 my-2">
			<svg viewBox="0 0 42 42" class="w-full h-full -rotate-90">
				{#each donutSegments as segment}
					<circle
						cx="21"
						cy="21"
						r="15.91549430918954"
						fill="transparent"
						stroke={segment.color}
						stroke-width="6"
						stroke-dasharray={segment.dasharray}
						stroke-dashoffset={segment.offset}
					/>
				{/each}
			</svg>
			<div class="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
				<span class="text-xs text-gray-400 font-medium">Gesamt</span>
				<span class="text-lg font-bold">${totalModelSpend.toFixed(2)}</span>
			</div>
		</div>

		<div class="w-full flex flex-col gap-1.5 mt-2">
			{#each donutSegments as segment}
				<div class="flex items-center justify-between text-xs">
					<div class="flex items-center gap-2">
						<span class="w-2.5 h-2.5 rounded-full" style="background-color: {segment.color};"></span>
						<span class="font-medium">{segment.model}</span>
					</div>
					<span class="text-gray-500">{segment.percent}% (${segment.spend.toFixed(2)})</span>
				</div>
			{/each}
		</div>
	</div>
</div>