<script lang="ts">
	import Modal from '$lib/components/common/Modal.svelte';
	import BudgetRingCard from './Budget/FullBudgetRing.svelte';
	import UsageAnalyticsSection from './Budget/UsageAnalyticsSection.svelte';

	export let show = false;
	export let size = '2xl';

	export let userData: {
		spend: number;
		max_budget: number;
		budget_duration?: string;
		budget_reset_at: string;
	} | null = null;

	export let dailyUsage: Array<{ date: string; spend: number; tokens: number }> = [];
	export let modelUsage: Array<{ model: string; spend: number; tokens: number; calls: number }> =
	
		[];

	const closeModal = () => {
		show = false;
	};
</script>

<Modal bind:show {size}>
	<div class="p-6 text-gray-900 dark:text-white relative max-h-[85vh] overflow-y-auto">
		<button
			type="button"
			class="absolute top-4 right-4 p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg transition cursor-pointer"
			on:click={closeModal}
			aria-label="Schließen"
		>
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
		</button>

		<h2 class="text-xl font-bold mb-6 text-center">Chat Budget Übersicht</h2>

		<BudgetRingCard {userData} />

		<hr class="my-8 border-gray-200 dark:border-gray-800" />

		<UsageAnalyticsSection {dailyUsage} {modelUsage} />

		<div class="mt-8 flex justify-end">
			<button
				type="button"
				class="px-5 py-2.5 text-sm font-medium bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-xl transition cursor-pointer"
				on:click={closeModal}
			>
				Schließen
			</button>
		</div>
	</div>
</Modal>
