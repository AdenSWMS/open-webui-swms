<script lang="ts">
	import type { UserInfoResponse } from '$lib/apis/litellm';

	export let userData: UserInfoResponse | null = null;
	export let onClick: () => void;

	$: spend = userData?.spend ?? 0;
	$: maxBudget = userData?.max_budget ?? 0;

	$: spentPercent = maxBudget > 0 
		? Math.min(Math.round((spend / maxBudget) * 100), 100) 
		: 0;

	$: resetDate = userData?.budget_reset_at ? new Date(userData.budget_reset_at) : new Date();
	$: now = new Date();

	$: startDate = new Date(resetDate.getTime() - 30 * 24 * 60 * 60 * 1000);

	$: totalPeriodMs = Math.max(resetDate.getTime() - startDate.getTime(), 1);
	$: elapsedMs = Math.min(Math.max(now.getTime() - startDate.getTime(), 0), totalPeriodMs);
	$: timePercent = Math.min(Math.round((elapsedMs / totalPeriodMs) * 100), 100);

	$: diff = spentPercent - timePercent;

	$: barColorClass = () => {
		if (diff > 15) return 'bg-red-500';
		if (diff > 5) return 'bg-amber-500';
		return 'bg-emerald-500';
	};

	$: textColorClass = () => {
		if (diff > 15) return 'text-red-500 dark:text-red-400';
		if (diff > 5) return 'text-amber-600 dark:text-amber-400';
		return 'text-emerald-600 dark:text-emerald-400';
	};
</script>

<button
	type="button"
	on:click={onClick}
	class="relative overflow-hidden group inline-flex items-center gap-2 px-3 py-1 text-xs font-medium bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition cursor-pointer"
	title="Klicken für detaillierte Budget-Übersicht"
>
	<div
		class="absolute left-0 top-0 bottom-0 opacity-15 dark:opacity-20 transition-all duration-500 ease-out pointer-events-none {barColorClass()}"
		style="width: {spentPercent}%;"
	></div>

	<div class="relative z-10 flex items-center gap-1.5">
		<span>
			Budget: {spend.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} / {maxBudget.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} €
		</span>
		<span class="font-semibold {textColorClass()}">
			({spentPercent}%)
		</span>
	</div>

	<div class="absolute bottom-0 left-0 right-0 h-[2px] bg-gray-100 dark:bg-gray-700/50">
		<div 
			class="h-full transition-all duration-500 ease-out {barColorClass()}" 
			style="width: {spentPercent}%;"
		></div>
	</div>
</button>