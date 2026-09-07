<script lang="ts">
	export let modelTokenDetails: Array<{
		model: string;
		prompt_tokens: number;
		completion_tokens: number;
		total_tokens: number;
	}> = [];

	let selectedModel: string = '';

	$: if (modelTokenDetails.length > 0 && !selectedModel) {
		selectedModel = modelTokenDetails[0].model;
	}

	$: activeDetail = modelTokenDetails.find((m) => m.model === selectedModel);
</script>

<div class="border border-gray-200 dark:border-gray-800 rounded-xl p-5 bg-gray-50 dark:bg-gray-800/40 my-6">
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
		<h4 class="font-semibold text-sm text-gray-500 uppercase tracking-wider">Token-Inspektor nach Modell</h4>
		
		<select
			bind:value={selectedModel}
			class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-1.5 text-sm font-medium focus:ring-2 focus:ring-sky-500 outline-none"
		>
			{#each modelTokenDetails as m}
				<option value={m.model}>{m.model}</option>
			{/each}
		</select>
	</div>

	{#if activeDetail}
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center mt-2">
			<div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700/50">
				<span class="text-xs text-gray-400 font-semibold uppercase block mb-1">Input Tokens (Prompt)</span>
				<span class="text-xl font-bold text-sky-500">{activeDetail.prompt_tokens.toLocaleString('de-DE')}</span>
			</div>

			<div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700/50">
				<span class="text-xs text-gray-400 font-semibold uppercase block mb-1">Output Tokens (Completion)</span>
				<span class="text-xl font-bold text-indigo-500">{activeDetail.completion_tokens.toLocaleString('de-DE')}</span>
			</div>

			<div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700/50">
				<span class="text-xs text-gray-400 font-semibold uppercase block mb-1">Gesamt Tokens</span>
				<span class="text-xl font-bold text-emerald-500">{activeDetail.total_tokens.toLocaleString('de-DE')}</span>
			</div>
		</div>
	{:else}
		<p class="text-sm text-gray-400 italic">Keine Token-Daten verfügbar.</p>
	{/if}
</div>