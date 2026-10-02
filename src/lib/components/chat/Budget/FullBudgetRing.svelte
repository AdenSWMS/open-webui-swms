<script lang="ts">
	import { increaseUserBudget } from '$lib/apis/litellm';

	export let userData: {
		spend: number;
		max_budget: number;
		budget_duration?: string;
		budget_reset_at: string;
		budget_increase_count: number;
	} | null = null;

	let budgetIncreaseLoading = false;
	let budgetIncreaseError: string | null = null;
	const budgetIncreaseTierColors = ['bg-emerald-500', 'bg-amber-500', 'bg-red-500'];

	$: budgetIncreaseCount = Math.min(3, Math.max(0, Number(userData?.budget_increase_count) || 0));
	$: budgetIncreaseCountLoaded = userData !== null;

	async function increaseBudget() {
		if (!userData || !canIncreaseBudget || budgetIncreaseLoading) return;

		budgetIncreaseLoading = true;
		budgetIncreaseError = null;
		try {
			const result = await increaseUserBudget(localStorage.token);
			userData = {
				...userData,
				max_budget: result.max_budget,
				budget_increase_count: result.budget_increase_count
			};
		} catch (error) {
			budgetIncreaseError = typeof error === 'string' ? error : 'Das Budget konnte nicht erhöht werden.';
		} finally {
			budgetIncreaseLoading = false;
		}
	}

	$: spend = userData?.spend ?? 0;
	$: maxBudget = userData?.max_budget ?? 0;
	$: canIncreaseBudget =
		budgetIncreaseCountLoaded && maxBudget > 0 && spend >= maxBudget && budgetIncreaseCount < 3;

	$: spentPercent = maxBudget > 0 
		? Math.min(Math.round((spend / maxBudget) * 100), 100) 
		: 0;

	$: resetDate = userData?.budget_reset_at ? new Date(userData.budget_reset_at) : new Date();
	$: now = new Date();

	$: startDate = new Date(resetDate.getTime() - 30 * 24 * 60 * 60 * 1000);

	$: totalPeriodMs = Math.max(resetDate.getTime() - startDate.getTime(), 1);
	$: elapsedMs = Math.min(Math.max(now.getTime() - startDate.getTime(), 0), totalPeriodMs);

	$: passedDays = Math.min(Math.floor(elapsedMs / (1000 * 60 * 60 * 24)), 30);
	$: remainingDays = Math.max(30 - passedDays, 0);

	$: timePercent = Math.min(Math.round((elapsedMs / totalPeriodMs) * 100), 100);

	$: budgetLabel = `$${spend.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 4 })} von $${maxBudget.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
	$: timeLabel = `(${remainingDays} T. übrig)`;

	$: diff = spentPercent - timePercent;

	$: budgetColorClass = () => {
		if (diff > 15) return 'text-red-500';
		if (diff > 5) return 'text-amber-500';
		return 'text-emerald-500';
	};

	$: statusInfo = () => {
		if (diff > 15) {
			return {
				title: 'Kritischer Verbrauch',
				text: 'Du verbrauchst dein Budget deutlich schneller als die Zeit verstreicht. Passe deine Nutzung an, um am Ende des Monats nicht ohne Budget dazustehen.',
				bg: 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20'
			};
		}
		if (diff > 5) {
			return {
				title: 'Erhöhter Verbrauch',
				text: 'Dein Budgetverbrauch liegt leicht über dem Zeitplan (+ ' + Math.abs(diff) + '%).',
				bg: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'
			};
		}
		if (diff < -15) {
			return {
				title: 'Sehr sparsam',
				text: 'Du hast noch reichlich Budget übrig.',
				bg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
			};
		}
		return {
			title: 'Optimaler Verbrauch',
			text: 'Dein Budgetverbrauch verläuft genau im Rahmen der Zeit.',
			bg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
		};
	};

	const sizePx = 180;
	const strokeWidth = 12;
	const center = sizePx / 2;

	const outerRadius = center - strokeWidth;
	const innerRadius = outerRadius - strokeWidth - 6;

	const outerCircumference = 2 * Math.PI * outerRadius;
	const innerCircumference = 2 * Math.PI * innerRadius;

	$: outerOffset = outerCircumference - (spentPercent / 100) * outerCircumference;
	$: innerOffset = innerCircumference - (timePercent / 100) * innerCircumference;
</script>

<div>
	<!-- Mobile: Flex Column (Diagramm oben, Werte unten nebeneinander). Desktop (md:): Original 3-Spalten Grid -->
	<div class="flex flex-col md:grid md:grid-cols-3 items-center gap-6 md:gap-4 my-4">
		
		<!-- Diagramm (Auf Mobile als Erstes oben zentriert) -->
		<div class="flex justify-center items-center relative order-1 md:order-2">
			<svg 
				viewBox="0 0 {sizePx} {sizePx}" 
				class="w-[160px] h-[160px] sm:w-[180px] sm:h-[180px] transform -rotate-90 overflow-visible"
			>
				<circle cx={center} cy={center} r={outerRadius} stroke="currentColor" stroke-width={strokeWidth} fill="transparent" class="text-gray-200 dark:text-gray-800" />
				<circle cx={center} cy={center} r={innerRadius} stroke="currentColor" stroke-width={strokeWidth} fill="transparent" class="text-gray-200 dark:text-gray-800" />

				<circle cx={center} cy={center} r={outerRadius} stroke="currentColor" stroke-width={strokeWidth} stroke-dasharray={outerCircumference} stroke-dashoffset={outerOffset} stroke-linecap="round" fill="transparent" class="{budgetColorClass()} transition-all duration-500 ease-out" />
				<circle cx={center} cy={center} r={innerRadius} stroke="currentColor" stroke-width={strokeWidth} stroke-dasharray={innerCircumference} stroke-dashoffset={innerOffset} stroke-linecap="round" fill="transparent" class="text-sky-400 transition-all duration-500 ease-out" />
			</svg>

			<div class="absolute inset-0 flex items-center justify-center pointer-events-none">
				<span class="text-xl font-extrabold tracking-tighter opacity-80">$</span>
			</div>
		</div>

		<!-- Zeitraum (Mobile: Links unten, Desktop: Links) -->
		<div class="w-full text-center md:text-right order-2 md:order-1 flex-1">
			<div class="text-2xl font-bold text-sky-400">{timePercent}%</div>
			<div class="text-xs font-semibold uppercase tracking-wider text-gray-400">Zeitraum</div>
			<div class="text-xs text-gray-500 mt-1">{timeLabel}</div>
		</div>

		<!-- Verbraucht (Mobile: Rechts unten, Desktop: Rechts) -->
		<div class="w-full text-center md:text-left order-3 flex-1">
			<div class="text-2xl font-bold {budgetColorClass()}">{spentPercent}%</div>
			<div class="text-xs font-semibold uppercase tracking-wider text-gray-400">Verbraucht</div>
			<!-- break-words schützt vor Overflow bei lange Formatierungen -->
			<div class="text-xs text-gray-500 mt-1 break-words">{budgetLabel}</div>
		</div>

	</div>

	<div class="mt-6 p-4 rounded-xl border text-sm {statusInfo().bg} transition-colors duration-300">
		<div class="font-bold mb-1">{statusInfo().title}</div>
		<div class="opacity-90">{statusInfo().text}</div>
	</div>

	<div class="mt-6 flex w-full flex-col items-center gap-3">
		<button
			type="button"
			class="w-full rounded-xl px-5 py-2.5 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50 {canIncreaseBudget
				? 'bg-sky-600 hover:bg-sky-700'
				: 'bg-gray-500'}"
			disabled={!canIncreaseBudget || budgetIncreaseLoading}
			on:click={increaseBudget}
		>
			{budgetIncreaseLoading
				? 'Wird erhöht …'
				: !budgetIncreaseCountLoaded
					? 'Lade Erhöhungsstatus …'
					: budgetIncreaseCount >= 3
						? 'Alle Erhöhungen verbraucht'
						: canIncreaseBudget
							? 'Budget um $5 erhöhen'
							: 'Bei 100 % verfügbar'}
		</button>

		<div class="grid w-full grid-cols-3 gap-1" aria-label="{budgetIncreaseCount} von 3 Budgeterhöhungen verwendet">
			<div
				class="h-2 rounded-full transition-all duration-300 {budgetIncreaseCount >= 1
					? (budgetIncreaseCount === 1 ? 'bg-emerald-500' : budgetIncreaseCount === 2 ? 'bg-amber-500' : 'bg-red-500')
					: 'bg-gray-200 dark:bg-gray-700'}"
			></div>

			<div
				class="h-2 rounded-full transition-all duration-300 {budgetIncreaseCount >= 2
					? (budgetIncreaseCount === 2 ? 'bg-amber-500' : 'bg-red-500')
					: 'bg-gray-200 dark:bg-gray-700'}"
			></div>

			<div
				class="h-2 rounded-full transition-all duration-300 {budgetIncreaseCount >= 3
					? 'bg-red-500'
					: 'bg-gray-200 dark:bg-gray-700'}"
			></div>
		</div>

		<div class="text-xs text-gray-500">{budgetIncreaseCount} von 3 Erhöhungen verwendet</div>

		{#if budgetIncreaseError}
			<div class="text-sm text-red-500" role="alert">{budgetIncreaseError}</div>
		{/if}
	</div>
</div>
