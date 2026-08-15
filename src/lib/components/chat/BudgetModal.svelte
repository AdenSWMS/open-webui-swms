<script lang="ts">
	import Modal from '$lib/components/common/Modal.svelte'; 

	export let show = false;
	export let size = 'md';

	export let userData: {
		spend: number;
		max_budget: number;
		budget_duration?: string;
		budget_reset_at: string;
	} | null = null;

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
	
	$: passedDays = Math.min(Math.floor(elapsedMs / (1000 * 60 * 60 * 24)), 30);
	$: remainingDays = Math.max(30 - passedDays, 0);

	$: timePercent = Math.min(Math.round((elapsedMs / totalPeriodMs) * 100), 100);

	$: budgetLabel = `${spend.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} € / ${maxBudget.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;
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

	const closeModal = () => {
		show = false;
	};
</script>

<Modal bind:show {size}>
	<div class="p-6 text-gray-900 dark:text-white relative">
		
		<button
			type="button"
			class="absolute top-4 right-4 p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg transition cursor-pointer"
			on:click={closeModal}
			aria-label="Schließen"
		>
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
			</svg>
		</button>

		<h2 class="text-xl font-bold mb-6 text-center">Chat Budget Übersicht</h2>

		<!-- Ring-Diagramm -->
		<div class="grid grid-cols-3 items-center gap-4 my-4">
			
			<!-- Links: Zeit-Fortschritt -->
			<div class="text-right">
				<div class="text-2xl font-bold text-sky-400">{timePercent}%</div>
				<div class="text-xs font-semibold uppercase tracking-wider text-gray-400">Zeitraum</div>
				<div class="text-xs text-gray-500 mt-1">{timeLabel}</div>
			</div>

			<!-- Mitte: Ringe -->
			<div class="flex justify-center items-center relative">
				<svg width={sizePx} height={sizePx} class="transform -rotate-90 overflow-visible">
					<!-- Hintergründe -->
					<circle cx={center} cy={center} r={outerRadius} stroke="currentColor" stroke-width={strokeWidth} fill="transparent" class="text-gray-200 dark:text-gray-800" />
					<circle cx={center} cy={center} r={innerRadius} stroke="currentColor" stroke-width={strokeWidth} fill="transparent" class="text-gray-200 dark:text-gray-800" />

					<!-- Äußerer Ring (Budget) -->
					<circle cx={center} cy={center} r={outerRadius} stroke="currentColor" stroke-width={strokeWidth} stroke-dasharray={outerCircumference} stroke-dashoffset={outerOffset} stroke-linecap="round" fill="transparent" class="{budgetColorClass()} transition-all duration-500 ease-out" />

					<!-- Innerer Ring (Zeit) -->
					<circle cx={center} cy={center} r={innerRadius} stroke="currentColor" stroke-width={strokeWidth} stroke-dasharray={innerCircumference} stroke-dashoffset={innerOffset} stroke-linecap="round" fill="transparent" class="text-sky-400 transition-all duration-500 ease-out" />
				</svg>

				<div class="absolute inset-0 flex items-center justify-center pointer-events-none">
					<span class="text-xl font-extrabold tracking-tighter opacity-80">€</span>
				</div>
			</div>

			<!-- Rechts: Budget-Fortschritt -->
			<div class="text-left">
				<div class="text-2xl font-bold {budgetColorClass()}">{spentPercent}%</div>
				<div class="text-xs font-semibold uppercase tracking-wider text-gray-400">Verbraucht</div>
				<div class="text-xs text-gray-500 mt-1">{budgetLabel}</div>
			</div>
		</div>

		<!-- Status / Bewertungsschild -->
		<div class="mt-6 p-4 rounded-xl border text-sm {statusInfo().bg} transition-colors duration-300">
			<div class="font-bold mb-1">{statusInfo().title}</div>
			<div class="opacity-90">{statusInfo().text}</div>
		</div>

		<!-- Schließen-Button -->
		<div class="mt-6 flex justify-end">
			<button
				type="button"
				class="px-4 py-2 text-sm font-medium bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-xl transition cursor-pointer"
				on:click={closeModal}
			>
				Schließen
			</button>
		</div>

	</div>
</Modal>