<script lang="ts">
	import { getContext } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let project: any = null;

	$: models = project?.project?.allowed_model_ids ?? [];
</script>

<Modal bind:show size="md">
	<div class="p-6 text-gray-900 dark:text-gray-100 flex flex-col max-h-[85vh] overflow-y-auto">
		{#if project}
			<!-- Header -->
			<div class="flex justify-between items-start mb-4">
				<div>
					<h3 class="text-xl font-bold">{project.name}</h3>
					{#if project.id}
						<span class="text-xs text-gray-400 font-mono">ID: {project.id}</span>
					{/if}
				</div>
			</div>

			<div class="mb-5">
				<h4 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
					{$i18n.t('Beschreibung')}
				</h4>
				<p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
					{project.project?.description || $i18n.t('Keine Beschreibung vorhanden.')}
				</p>
			</div>

			<!-- Modell-Liste -->
			<div class="mb-5">
				<div class="flex items-center justify-between mb-2">
					<h4 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
						{$i18n.t('Freigeschaltete Modelle')}
					</h4>
					{#if models.length > 0}
						<span class="text-xs text-gray-400 font-mono">({models.length})</span>
					{/if}
				</div>

				{#if models.length > 0}
					<!-- Scrollbarer Container für ~7 Modelle (max-h ~200px) -->
					<div class="max-h-[200px] overflow-y-auto pr-1">
						<ul class="divide-y divide-gray-100 dark:divide-gray-800/60">
							{#each models as model}
								<li class="py-1.5 px-2 flex items-center justify-between text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/40 rounded transition-colors">
									<span class="font-medium truncate">
										{model.name ?? model.id ?? model}
									</span>
								</li>
							{/each}
						</ul>
					</div>
				{:else}
					<p class="text-xs text-gray-400 italic">
						{$i18n.t('Keine spezifischen Modelle zugewiesen.')}
					</p>
				{/if}
			</div>

		{:else}
			<div class="py-8 text-center text-sm text-gray-500">
				{$i18n.t('Keine Projektdaten verfügbar.')}
			</div>
		{/if}

		<!-- Footer -->
		<div class="mt-6 flex justify-end pt-3 border-t border-gray-100 dark:border-gray-800">
			<button
				type="button"
				on:click={() => (show = false)}
				class="px-4 py-2 text-sm font-medium rounded-lg bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200 transition-colors cursor-pointer"
			>
				{$i18n.t('Schließen')}
			</button>
		</div>
	</div>
</Modal>