<script lang="ts">
	export let dailyUsage: Array<{ date: string; spend: number; tokens: number }> = [];
	export let modelUsage: Array<{ model: string; spend: number; tokens: number; calls: number }> =
		[];
	export let modelCostMap: Array<{
		model: string;
		input: string;
		output: string;
		cacheRead: string;
		cacheWrite: string;
		maxInput: string;
		maxOutput: string;
	}> = [];

	let activeTab: 'usage' | 'rates' = 'usage';

	$: sortedModelUsage = [...modelUsage].sort((a, b) => b.spend - a.spend);
	$: sortedModelCostMap = [...modelCostMap].sort((a, b) => b.output.localeCompare(a.output));
</script>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
	<!-- Linke Karte: Nutzung pro Tag (nimmt 1 Spalte ein -> 1/3) -->
	<div class="border border-gray-200 dark:border-gray-800 rounded-xl p-4 bg-white dark:bg-gray-900 lg:col-span-1">
		<h4 class="font-semibold text-sm mb-3 text-gray-500 uppercase tracking-wider">
			Nutzung pro Tag
		</h4>
		<div class="h-72 overflow-y-auto overflow-x-auto pr-2">
			<table class="w-full text-left text-sm">
				<thead class="sticky top-0 bg-white dark:bg-gray-900 z-10">
					<tr class="border-b border-gray-200 dark:border-gray-800 text-xs text-gray-400">
						<th class="pb-2 px-2 bg-white dark:bg-gray-900">Datum</th>
						<th class="pb-2 px-2 bg-white dark:bg-gray-900">Tokens</th>
						<th class="pb-2 px-2 text-right bg-white dark:bg-gray-900">Kosten</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
					{#each dailyUsage as item}
						<tr>
							<td class="py-2 px-2">{item.date}</td>
							<td class="py-2 px-2 text-gray-500">{item.tokens.toLocaleString('de-DE')}</td>
							<td class="py-2 px-2 text-right font-medium">${item.spend.toFixed(4)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>

	<!-- Rechte Karte: Nutzung & Preisübersicht (nimmt 2 Spalten ein -> 2/3) -->
	<div class="border border-gray-200 dark:border-gray-800 rounded-xl p-4 bg-white dark:bg-gray-900 lg:col-span-2">
		<div class="flex items-center justify-between mb-3">
			<h4 class="font-semibold text-sm text-gray-500 uppercase tracking-wider">
				{activeTab === 'usage' ? 'Nutzung pro Modell' : 'Modell-Preise (/1M Tokens)'}
			</h4>

			<div class="flex bg-gray-100 dark:bg-gray-800 p-0.5 rounded-lg text-xs font-medium">
				<button
					type="button"
					on:click={() => (activeTab = 'usage')}
					class="px-2.5 py-1 rounded-md transition-colors {activeTab === 'usage'
						? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
						: 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}"
				>
					Nutzung
				</button>
				<button
					type="button"
					on:click={() => (activeTab = 'rates')}
					class="px-2.5 py-1 rounded-md transition-colors {activeTab === 'rates'
						? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
						: 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}"
				>
					Preise
				</button>
			</div>
		</div>

		<div class="h-72 overflow-y-auto overflow-x-auto pr-2">
			{#if activeTab === 'usage'}
				<table class="w-full text-left text-sm">
					<thead class="sticky top-0 bg-white dark:bg-gray-900 z-10">
						<tr class="border-b border-gray-200 dark:border-gray-800 text-xs text-gray-400">
							<th class="pb-2 px-2 bg-white dark:bg-gray-900">Modell</th>
							<th class="pb-2 px-2 bg-white dark:bg-gray-900">Aufrufe</th>
							<th class="pb-2 px-2 text-right bg-white dark:bg-gray-900">Kosten</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
						{#each sortedModelUsage as item}
							<tr>
								<td class="py-2 px-2 font-medium">{item.model}</td>
								<td class="py-2 px-2 text-gray-500">{item.calls}</td>
								<td class="py-2 px-2 text-right font-medium">${item.spend.toFixed(4)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{:else}
				<table class="w-full text-left text-sm">
					<thead class="sticky top-0 bg-white dark:bg-gray-900 z-10">
						<tr class="border-b border-gray-200 dark:border-gray-800 text-xs text-gray-400">
							<th class="pb-2 px-2 bg-white dark:bg-gray-900">Modell</th>
							<th class="pb-2 px-2 text-right bg-white dark:bg-gray-900">Input / 1M</th>
							<th class="pb-2 px-2 text-right bg-white dark:bg-gray-900">Output / 1M</th>
							<th class="pb-2 px-2 text-right bg-white dark:bg-gray-900">Cache Read</th>
							<th class="pb-2 px-2 text-right bg-white dark:bg-gray-900">Cache Write</th>
							<th class="pb-2 px-2 text-right bg-white dark:bg-gray-900">Max In Tkn.</th>
							<th class="pb-2 px-2 text-right bg-white dark:bg-gray-900">Max Out Tkn.</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-100 dark:divide-gray-800 text-xs">
						{#each sortedModelCostMap as rate}
							<tr>
								<td class="py-2 px-2 font-medium text-sm">{rate.model}</td>
								<td class="py-2 px-2 text-right text-gray-600 dark:text-gray-300">{rate.input}</td>
								<td class="py-2 px-2 text-right text-gray-600 dark:text-gray-300">{rate.output}</td>
								<td class="py-2 px-2 text-right text-gray-400">{rate.cacheRead}</td>
								<td class="py-2 px-2 text-right text-gray-400">{rate.cacheWrite}</td>
								<td class="py-2 px-2 text-right text-gray-500">{rate.maxInput}</td>
								<td class="py-2 px-2 text-right text-gray-500">{rate.maxOutput}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{/if}
		</div>
	</div>
</div>