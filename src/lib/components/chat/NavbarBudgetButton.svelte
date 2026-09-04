<script lang="ts">
	import type { UserInfoResponse } from '$lib/apis/litellm';

	export let userData: UserInfoResponse | null = null;
	export let onClick: () => void;

	$: spend = userData?.spend ?? 0;
	$: maxBudget = userData?.max_budget ?? 0;

	$: spentPercent = maxBudget > 0 ? Math.min(Math.round((spend / maxBudget) * 100), 100) : 0;

	$: resetDate = userData?.budget_reset_at ? new Date(userData.budget_reset_at) : new Date();
	$: now = new Date();

	$: startDate = new Date(resetDate.getTime() - 30 * 24 * 60 * 60 * 1000);

	$: totalPeriodMs = Math.max(resetDate.getTime() - startDate.getTime(), 1);
	$: elapsedMs = Math.min(Math.max(now.getTime() - startDate.getTime(), 0), totalPeriodMs);
	$: timePercent = Math.min(Math.round((elapsedMs / totalPeriodMs) * 100), 100);

	$: diff = spentPercent - timePercent;

	$: barColorClass = diff > 15 
		? 'bg-red-500' 
		: diff > 5 
			? 'bg-amber-500' 
			: 'bg-emerald-500';

	$: textColorClass = diff > 15 
		? 'text-red-500 dark:text-red-400' 
		: diff > 5 
			? 'text-amber-600 dark:text-amber-400' 
			: 'text-emerald-600 dark:text-emerald-400';
</script>

<button
	type="button"
	on:click={onClick}
	class="w-full relative overflow-hidden group inline-flex items-center justify-center gap-2 px-3 py-1 text-xs font-medium bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition cursor-pointer text-center"
	title="Klicken für detaillierte Budget-Übersicht"
>
	<div
		class="absolute left-0 top-0 bottom-0 transition-all duration-500 ease-out pointer-events-none {barColorClass}"
		style="width: {spentPercent}%;"
	></div>

	<div class="relative z-10 flex w-full items-center justify-center gap-1.5 text-center">
		<span>
			Budget: ${spend.toLocaleString('de-DE', {
				minimumFractionDigits: 2,
				maximumFractionDigits: 4
			})} von ${maxBudget.toLocaleString('de-DE', {
				minimumFractionDigits: 2,
				maximumFractionDigits: 4
			})}
		</span>
		<span class="font-semibold {textColorClass}">
			({spentPercent}%)
		</span>
	</div>

	<div
		class="h-full transition-all duration-500 ease-out {barColorClass}"
		style="width: {spentPercent}%;"
	></div>
</button>
