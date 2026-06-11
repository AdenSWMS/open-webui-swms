<!-- ModelPermissions.svelte -->
<script lang="ts">
	import { getContext } from 'svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import { onMount } from 'svelte';
	import { getModels } from '$lib/apis';

	const i18n = getContext('i18n');

	export let allowedModelIds: string[] = [];
	export let onAdd: Function = () => {};
	export let onRemove: Function = () => {};

	let allModels = [];

	onMount(async () => {
		try {
			const res = await getModels(localStorage.token);
			allModels = res ?? [];
		} catch (error) {
			console.error('Failed to fetch models:', error);
		}
	});

	const isAllowed = (modelId: string) => allowedModelIds.includes(modelId);

	const handleChange = (modelId: string, enabled: boolean) => {
		if (enabled) {
			onAdd(modelId);
		} else {
			onRemove(modelId);
		}
	};
</script>

<div class="flex flex-col gap-2">
	<div class="text-sm font-medium px-1">
		{$i18n.t('Models')}
	</div>
	{#each allModels as model (model.id)}
		<div class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-850">
			<span class="text-sm">{model.name}</span>
			<Switch
				state={isAllowed(model.id)}
				on:change={(e) => handleChange(model.id, e.detail)}
			/>
		</div>
	{/each}
</div>