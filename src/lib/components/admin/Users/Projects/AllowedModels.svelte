<!-- ModelPermissions.svelte -->
<script lang="ts">
	import { getContext, onDestroy } from 'svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import { addAllowedModelsToProject, removeAllowedModelsFromProject, getAllowedModelsOfProject } from '$lib/apis/projects';
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import { getModels } from '$lib/apis';

	const i18n = getContext('i18n');

	export let allowedModelIds: string[] = [];
	let allModels = [];
	export let projectId: string;
	let searchDebounceTimer: ReturnType<typeof setTimeout>;
	let query = '';

	let page = 1;

	onMount(async () => {
		try {
			const res = await getModels(localStorage.token);
			allModels = res ?? [];
		} catch (error) {
			console.error('Failed to fetch models:', error);
		}
	});

	const isAllowed = (modelId: string) => allowedModelIds.includes(modelId);

	const getAllowedModels = async () => {
		try {
			const res = await getAllowedModelsOfProject(localStorage.token, projectId).catch((error) => {
				toast.error(`${error}`);
				return null;
			});

			if (res) {
				allowedModelIds = res ?? [];
			}
		} catch (err) {
			console.error(err);
		}
		
	};

	const handleChange = async (modelId: string, enabled: boolean) => {
			if (enabled) {
				await addAllowedModelsToProject(localStorage.token, projectId, [modelId]).catch((error) => {
					toast.error(`${error}`);
					return null;
				});
			} else {
				await removeAllowedModelsFromProject(localStorage.token, projectId, [modelId]).catch((error) => {
					toast.error(`${error}`);
					return null;
				});
			}
		getAllowedModels();
	};

	$: if (page !== null) {
		getAllowedModels();
	}

	$: if (query !== undefined) {
		clearTimeout(searchDebounceTimer);
		searchDebounceTimer = setTimeout(() => {
			page = 1;
			getAllowedModels();
		}, 300);
	}

	onDestroy(() => {
		clearTimeout(searchDebounceTimer);
	});
</script>

<div class="flex flex-col gap-2">
	<div class="text-sm font-medium px-1">
		{$i18n.t('Models')}
	</div>
	{#if allModels === null}
		<div class="my-10">
			<Spinner className="size-5" />
		</div>
	{:else}
		{#if allModels.length > 0}
			{#each allModels as model (model.id)}
				<div class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-850">
					<span class="text-sm">{model.name}</span>
					<Switch
						state={isAllowed(model.id)} 
						on:change={(e) => handleChange(model.id, e.detail)}
					/>
				</div>
			{/each}
		{:else}
			<div class="text-gray-500 text-xs text-center py-2 px-10">
				{$i18n.t('No models were found.')}
			</div>
		{/if}
	{/if}
</div>