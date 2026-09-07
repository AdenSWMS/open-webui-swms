<script lang="ts">
	export let dailyUsage: Array<{ date: string; spend: number; tokens: number }> = [];
	export let modelUsage: Array<{ model: string; spend: number; tokens: number; calls: number }> = [];
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
	<div class="border border-gray-200 dark:border-gray-800 rounded-xl p-4">
		<h4 class="font-semibold text-sm mb-3 text-gray-500 uppercase tracking-wider">Nutzung pro Tag</h4>
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead>
					<tr class="border-b border-gray-200 dark:border-gray-800 text-xs text-gray-400">
						<th class="pb-2">Datum</th>
						<th class="pb-2">Tokens</th>
						<th class="pb-2 text-right">Kosten</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
					{#each dailyUsage as item}
						<tr>
							<td class="py-2">{item.date}</td>
							<td class="py-2 text-gray-500">{item.tokens.toLocaleString('de-DE')}</td>
							<td class="py-2 text-right font-medium">${item.spend.toFixed(4)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>

	<div class="border border-gray-200 dark:border-gray-800 rounded-xl p-4">
		<h4 class="font-semibold text-sm mb-3 text-gray-500 uppercase tracking-wider">Nutzung pro Modell</h4>
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead>
					<tr class="border-b border-gray-200 dark:border-gray-800 text-xs text-gray-400">
						<th class="pb-2">Modell</th>
						<th class="pb-2">Aufrufe</th>
						<th class="pb-2 text-right">Kosten</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
					{#each modelUsage as item}
						<tr>
							<td class="py-2 font-medium">{item.model}</td>
							<td class="py-2 text-gray-500">{item.calls}</td>
							<td class="py-2 text-right font-medium">${item.spend.toFixed(4)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>