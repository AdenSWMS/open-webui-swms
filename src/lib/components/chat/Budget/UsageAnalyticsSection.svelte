<script lang="ts">
	import { onMount } from 'svelte';
	import { getUserAnalytics, getModelCostMap } from '$lib/apis/litellm';

	import UsageTables from './UsagtTables.svelte';
	import UsageTablesSkeleton from './Skeletons/TableSkeleton.svelte';
	import UsageCharts from './UsageChart.svelte';
	import UsageChartsSkeleton from './Skeletons/ChartSkeletom.svelte';
	import ModelTokenInspector from './ModelTokenInspector.svelte';

	let isLoading = true;
	let selectedFilter: '24h' | '7d' | '30d' | 'billing_cycle' |'custom' = '7d';
	
	let customStartDate = '';
	let customEndDate = '';

	let dailyUsage: any[] = [];
	let modelUsage: any[] = [];
	let modelTokenDetails: any[] = [];
	let dailyModelData: any[] = [];

	let modelCostMap: any[] = [];

	function getDateRange(filter: string) {
		const end = new Date();
		const start = new Date();

		if (filter === '24h') {
			start.setDate(end.getDate() - 1);
		} else if (filter === '7d') {
			start.setDate(end.getDate() - 7);
		} else if (filter === '30d') {
			start.setDate(end.getDate() - 30);
		} else if (filter === 'billing_cycle') {
			start.setDate(1);
		} else if (filter === 'custom' && customStartDate && customEndDate) {
			return { startDate: customStartDate, endDate: customEndDate };
		}

		return {
			startDate: start.toISOString().split('T')[0],
			endDate: end.toISOString().split('T')[0]
		};
	}

	async function fetchModelCostMap() {
		try {
			const token = localStorage.token;
			const cost_data = await getModelCostMap(token);
			
			modelCostMap = cost_data?.model_cost_map || [];
		} catch (err) {
			console.error('Fehler beim Abrufen der Modellkostenkarte:', err);
			modelCostMap = [];
		}
	}

	async function fetchAnalytics() {
	
		if (selectedFilter === 'custom' && (!customStartDate || !customEndDate)) return;

		isLoading = true;
		try {
			const token = localStorage.token;
			const { startDate, endDate } = getDateRange(selectedFilter);

			const data = await getUserAnalytics(token, startDate, endDate);
			

			dailyUsage = (data.daily_usage || []).slice().sort((a: any, b: any) => 
				(a.date || '').localeCompare(b.date || '')
			);

			dailyModelData = (data.daily_model_data || []).slice().sort((a: any, b: any) => 
				(a.date || '').localeCompare(b.date || '')
			);

			modelUsage = data.model_usage;
			modelTokenDetails = data.model_token_details;
		} catch (err) {
			console.error('Fehler beim Abrufen der Analytics-Daten:', err);
		} finally {
			isLoading = false;
		}
	}

	$: if (selectedFilter || customStartDate || customEndDate) {
		fetchAnalytics();
	}

	onMount(() => {
		fetchModelCostMap();
	});
</script>

<div>
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
		<h3 class="text-lg font-bold">Detaillierte Nutzungsanalyse</h3>
		
		<div class="flex flex-wrap gap-1.5 bg-gray-100 dark:bg-gray-800 p-1 rounded-xl w-fit">
			<button
				type="button"
				class="px-3 py-1 text-xs font-semibold rounded-lg transition cursor-pointer {selectedFilter === '24h' ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'}"
				on:click={() => (selectedFilter = '24h')}
			>
				24h
			</button>
			<button
				type="button"
				class="px-3 py-1 text-xs font-semibold rounded-lg transition cursor-pointer {selectedFilter === '7d' ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'}"
				on:click={() => (selectedFilter = '7d')}
			>
				7 Tage
			</button>
			<button
				type="button"
				class="px-3 py-1 text-xs font-semibold rounded-lg transition cursor-pointer {selectedFilter === '30d' ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'}"
				on:click={() => (selectedFilter = '30d')}
			>
				30 Tage
			</button>
					<button
				type="button"
				class="px-3 py-1 text-xs font-semibold rounded-lg transition cursor-pointer {selectedFilter === 'billing_cycle' ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'}"
				on:click={() => (selectedFilter = 'billing_cycle')}
			>
				Budget Zeitraum
			</button>
			<button
				type="button"
				class="px-3 py-1 text-xs font-semibold rounded-lg transition cursor-pointer {selectedFilter === 'custom' ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'}"
				on:click={() => (selectedFilter = 'custom')}
			>
				Custom
			</button>
		</div>
	</div>

	{#if selectedFilter === 'custom'}
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6 bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-200 dark:border-gray-700/50">
			<div>
				<label for="start-date" class="block text-xs font-semibold text-gray-500 uppercase mb-1">Von Datum</label>
				<input id="start-date" type="date" bind:value={customStartDate} class="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-1.5 text-sm" />
			</div>
			<div>
				<label for="end-date" class="block text-xs font-semibold text-gray-500 uppercase mb-1">Bis Datum</label>
				<input id="end-date" type="date" bind:value={customEndDate} class="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-1.5 text-sm" />
			</div>
		</div>
	{/if}

	{#if isLoading}
		<UsageTablesSkeleton />
		<UsageChartsSkeleton />
	{:else}
		<UsageTables {dailyUsage} {modelUsage} {modelCostMap}/>

		<UsageCharts {dailyModelData} {modelUsage} />

		<ModelTokenInspector {modelTokenDetails} />
	{/if}
</div>