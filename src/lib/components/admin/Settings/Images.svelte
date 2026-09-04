<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { createEventDispatcher, onMount, getContext } from 'svelte';
	import { config as backendConfig, user } from '$lib/stores';

	import { getBackendConfig } from '$lib/apis';
	import {
		getImageGenerationModels,
		getImageGenerationConfig,
		updateImageGenerationConfig,
		getConfig,
		updateConfig,
		verifyConfigUrl
	} from '$lib/apis/images';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';
	import CodeEditorModal from '$lib/components/common/CodeEditorModal.svelte';
	import SettingsSelect from '$lib/components/common/SettingsSelect.svelte';
	import AdminSettingField from './AdminSettingField.svelte';
	import AdminSettingRow from './AdminSettingRow.svelte';
	import AdminSettingSection from './AdminSettingSection.svelte';
	import Engine from './Images/Engine.svelte';
	import ModelSelect from './Images/ModelInput.svelte';
	import ResolutionInput from './Images/ResolutionInput.svelte';

	const dispatch = createEventDispatcher();

	const i18n: any = getContext('i18n');

	let loading = false;

	let config = null;
	export const inputClass =
		'w-full h-7 rounded-lg border border-gray-100/50 bg-gray-50/40 px-2 text-xs text-gray-700 outline-hidden transition-colors placeholder:text-gray-300 focus:border-blue-400 dark:border-white/[0.04] dark:bg-white/[0.03] dark:text-gray-300 dark:placeholder:text-gray-700 dark:focus:border-blue-500';
	const textareaClass =
		'w-full rounded-lg border border-gray-100/50 bg-gray-50/40 px-2 py-1.5 text-xs text-gray-700 outline-hidden transition-colors placeholder:text-gray-300 focus:border-blue-400 dark:border-white/[0.04] dark:bg-white/[0.03] dark:text-gray-300 dark:placeholder:text-gray-700 dark:focus:border-blue-500';

	let showComfyUIWorkflowEditor = false;
	let REQUIRED_WORKFLOW_NODES = [
		{
			type: 'prompt',
			key: 'text',
			node_ids: ''
		},
		{
			type: 'model',
			key: 'ckpt_name',
			node_ids: ''
		},
		{
			type: 'width',
			key: 'width',
			node_ids: ''
		},
		{
			type: 'height',
			key: 'height',
			node_ids: ''
		},
		{
			type: 'steps',
			key: 'steps',
			node_ids: ''
		},
		{
			type: 'seed',
			key: 'seed',
			node_ids: ''
		}
	];

	let showComfyUIEditWorkflowEditor = false;
	let REQUIRED_EDIT_WORKFLOW_NODES = [
		{
			type: 'image',
			key: 'image',
			node_ids: ''
		},
		{
			type: 'prompt',
			key: 'prompt',
			node_ids: ''
		},
		{
			type: 'model',
			key: 'unet_name',
			node_ids: ''
		},
		{
			type: 'width',
			key: 'width',
			node_ids: ''
		},
		{
			type: 'height',
			key: 'height',
			node_ids: ''
		}
	];

	const updateConfigHandler = async () => {
		if (config.ENABLE_IMAGE_GENERATION && Array.isArray(config.IMAGE_GENERATION_MODELS)) {

			for (const model of config.IMAGE_GENERATION_MODELS) {
				const engineType = model.IMAGE_GENERATION_ENGINE;

				if (engineType === 'automatic1111' && !model.AUTOMATIC1111_BASE_URL) {
					toast.error($i18n.t(`AUTOMATIC1111 Base URL is required (${model}).`));
					return null;
				} else if (engineType === 'comfyui' && !model.COMFYUI_BASE_URL) {
					toast.error($i18n.t(`ComfyUI Base URL is required (${model}).`));
					return null;
				} else if (engineType === 'openai' && !model.IMAGES_OPENAI_API_KEY) {
					toast.error($i18n.t(`OpenAI API Key is required (${model}).`));
					return null;
				} else if (engineType === 'gemini' && !model.IMAGES_GEMINI_API_KEY) {
					toast.error($i18n.t(`Gemini API Key is required (${model}).`));
					return null;
				}
			}
		}

		const processedModels = (config.IMAGE_GENERATION_MODELS || []).map((model) => {
			let automatic1111Params = {};
			let openaiParams = {};

			if (typeof model.AUTOMATIC1111_PARAMS === 'string' && model.AUTOMATIC1111_PARAMS.trim() !== '') {
				try {
					automatic1111Params = JSON.parse(model.AUTOMATIC1111_PARAMS);
				} catch (e) {
					automatic1111Params = {};
				}
			} else {
				automatic1111Params = model.AUTOMATIC1111_PARAMS || {};
			}

			if (typeof model.IMAGES_OPENAI_API_PARAMS === 'string' && model.IMAGES_OPENAI_API_PARAMS.trim() !== '') {
				try {
					openaiParams = JSON.parse(model.IMAGES_OPENAI_API_PARAMS);
				} catch (e) {
					openaiParams = {};
				}
			} else {
				openaiParams = model.IMAGES_OPENAI_API_PARAMS || {};
			}

			return {
				...model,
				AUTOMATIC1111_PARAMS: automatic1111Params,
				IMAGES_OPENAI_API_PARAMS: openaiParams
			};
		});

		const res = await updateConfig(localStorage.token, {
			...config,
			IMAGE_GENERATION_MODELS: processedModels
		}).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			config = res;
			backendConfig.set(await getBackendConfig());

			return res;
		}

		return null;
	};

	const validateJSON = (json) => {
		try {
			const obj = JSON.parse(json);

			if (obj && typeof obj === 'object') {
				return true;
			}
		} catch (e) {}
		return false;
	};

	const saveHandler = async () => {
		loading = true;

		const currentConfig = config;

		if (currentConfig?.IMAGE_GENERATION_MODELS && Array.isArray(currentConfig.IMAGE_GENERATION_MODELS)) {
			for (const model of currentConfig.IMAGE_GENERATION_MODELS) {
				
				if (model.IMAGE_GENERATION_ENGINE === 'comfyui') {
					const modelName = model.title || model.name || model.id;

					if (model.COMFYUI_WORKFLOW) {
						if (!validateJSON(model.COMFYUI_WORKFLOW)) {
							toast.error($i18n.t(`Invalid JSON format for ComfyUI Workflow in model "${modelName}".`));
							loading = false;
							return;
						}

						const requiredNodes = model.REQUIRED_WORKFLOW_NODES || REQUIRED_WORKFLOW_NODES || [];

						model.COMFYUI_WORKFLOW_NODES = requiredNodes.map((node) => {
							return {
								type: node.type,
								key: node.key,
								node_ids:
									typeof node.node_ids === 'string' && node.node_ids.trim() !== ''
										? node.node_ids.split(',').map((id) => id.trim())
										: Array.isArray(node.node_ids) ? node.node_ids : []
							};
						});
					}

					if (model.IMAGES_EDIT_COMFYUI_WORKFLOW) {
						if (!validateJSON(model.IMAGES_EDIT_COMFYUI_WORKFLOW)) {
							toast.error($i18n.t(`Invalid JSON format for ComfyUI Edit Workflow in model "${modelName}".`));
							loading = false;
							return;
						}

						const requiredEditNodes = model.REQUIRED_EDIT_WORKFLOW_NODES || REQUIRED_EDIT_WORKFLOW_NODES || [];

						model.IMAGES_EDIT_COMFYUI_WORKFLOW_NODES = requiredEditNodes.map((node) => {
							return {
								type: node.type,
								key: node.key,
								node_ids:
									typeof node.node_ids === 'string' && node.node_ids.trim() !== ''
										? node.node_ids.split(',').map((id) => id.trim())
										: Array.isArray(node.node_ids) ? node.node_ids : []
							};
						});
					}
				}
			}
		}

		// 2. Den eigentlichen Update-Handler aufrufen (sendet alles ans Backend)
	const res = await updateConfigHandler();
		if (res) {
			dispatch('save');
		}

		loading = false;
	};

	const removeModelHandler = (index) => {
		config.IMAGE_GENERATION_MODELS = config.IMAGE_GENERATION_MODELS.filter((_, i) => i !== index);
		
		// Fallback für den Index, falls das aktuell ausgewählte/letzte Modell gelöscht wurde
		if (selectedModelIndex >= config.IMAGE_GENERATION_MODELS.length) {
			selectedModelIndex = Math.max(0, config.IMAGE_GENERATION_MODELS.length - 1);
		}
	};

	let selectedModelIndex = 0;

	const addModelHandler = () => {
		if (!config.IMAGE_GENERATION_MODELS) {
			config.IMAGE_GENERATION_MODELS = [];
		}

		const newModel = {

			id: crypto.randomUUID(),
			title: `Model ${config.IMAGE_GENERATION_MODELS.length + 1}`,
			IMAGE_GENERATION_ENGINE: 'openai',
			IMAGE_GENERATION_MODEL: '',

			IMAGE_SIZE: ['1024x1024'],
			IMAGE_STEPS: 0,

			IMAGES_OPENAI_API_KEY: '',
			IMAGES_OPENAI_API_BASE_URL: 'https://api.openai.com/v1',
			IMAGES_OPENAI_API_PARAMS: '',
			IMAGES_GEMINI_API_KEY: '',


			AUTOMATIC1111_BASE_URL: '',
			AUTOMATIC1111_PARAMS: '',

			COMFYUI_BASE_URL: '',
			COMFYUI_API_KEY: '',
			COMFYUI_WORKFLOW: ''
		};

		config.IMAGE_GENERATION_MODELS = [...config.IMAGE_GENERATION_MODELS, newModel];
		
		selectedModelIndex = config.IMAGE_GENERATION_MODELS.length - 1;

	};

	onMount(async () => {
		if ($user?.role === 'admin') {
			const res = await getConfig(localStorage.token).catch((error) => {
				toast.error(`${error}`);
				return null;
			});

			if (res) {

				config = res;
			}

			if (!config) return;

			if (!config.IMAGE_GENERATION_MODELS) {
				config.IMAGE_GENERATION_MODELS = [];
			}

			if (config.IMAGE_GENERATION_MODELS.length > 0) {
				selectedModelIndex = 0; 
			}
		}
	});
</script>

<form
	class="flex h-full flex-col justify-between text-sm"
	on:submit|preventDefault={async () => {
		saveHandler();
	}}
>
	<h2 class="text-sm font-medium text-gray-900 dark:text-white mb-4">{$i18n.t('Images')}</h2>

	<div class="flex-1 min-h-0 overflow-y-auto scrollbar-hover pr-1.5">
	{#if config}
		<div class="flex flex-col gap-4">
			<!-- Globale Schalter -->
			<AdminSettingSection first>
				<AdminSettingRow
					label={$i18n.t('Image Generation')}
					description={$i18n.t('Allow users to generate images from prompts.')}
					let:labelId
				>
					<Switch bind:state={config.ENABLE_IMAGE_GENERATION} ariaLabelledbyId={labelId} />
				</AdminSettingRow>
			</AdminSettingSection>

			<AdminSettingSection>
				<AdminSettingRow
					label={$i18n.t('Image Prompt Generation')}
					description={$i18n.t('Generate an image prompt before sending the request.')}
					let:labelId
				>
					<Switch
						bind:state={config.ENABLE_IMAGE_PROMPT_GENERATION}
						ariaLabelledbyId={labelId}
					/>
				</AdminSettingRow>
			</AdminSettingSection>

			<!-- Modellspezifischer Bereich -->
			{#if config.ENABLE_IMAGE_GENERATION}
				<AdminSettingSection title={$i18n.t('Model Konfigurationen')}>
					
					<!-- TAB LEISTE: Aktives Modell wählen -->
					<div class="flex items-center gap-2 border-b border-gray-200 dark:border-gray-800 pb-2 mb-4 overflow-x-auto">
						{#each config.IMAGE_GENERATION_MODELS ?? [] as model, idx (model.id || idx)}
							<button
								type="button"
								class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors whitespace-nowrap flex items-center gap-2
									{selectedModelIndex === idx 
										? 'bg-black text-white dark:bg-white dark:text-black' 
										: 'bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'}"
								on:click={() => (selectedModelIndex = idx)}
							>
								<span>{model.IMAGE_GENERATION_MODEL || model.title || `Model #${idx + 1}`}</span>
								<span class="text-[10px] opacity-70 uppercase">({model.IMAGE_GENERATION_ENGINE})</span>
							</button>
						{/each}

						<!-- Button: Neues Modell -->
						<button
							class="px-3 py-1.5 text-xs font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-lg flex items-center gap-1 shrink-0 ml-auto"
							type="button"
							on:click={addModelHandler}
						>
							+ {$i18n.t('Add Model')}
						</button>
					</div>

					<!-- AKTIVES MODELL FORMULAR -->
					{#if config.IMAGE_GENERATION_MODELS?.length > 0 && config.IMAGE_GENERATION_MODELS[selectedModelIndex]}
						{@const currentModel = config.IMAGE_GENERATION_MODELS[selectedModelIndex]}

						<div class="space-y-4">
							
							<!-- Modell Engine Auswahl -->
							<Engine bind:config={config.IMAGE_GENERATION_MODELS[selectedModelIndex]} />

							<div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
								<AdminSettingField label={$i18n.t('Model')}>
									<ModelSelect
										bind:value={currentModel.IMAGE_GENERATION_MODEL}
										{inputClass}
										{i18n}
									/>
								</AdminSettingField>

								<AdminSettingField label={$i18n.t('Image Size')}>
									<ResolutionInput
										bind:value={currentModel.IMAGE_SIZE}
										{inputClass}
										{i18n}
										on:change={() => {
											config.IMAGE_GENERATION_MODELS = [...config.IMAGE_GENERATION_MODELS];
										}}
									/>
								</AdminSettingField>

								{#if ['comfyui', 'automatic1111', ''].includes(currentModel?.IMAGE_GENERATION_ENGINE)}
									<AdminSettingField label={$i18n.t('Steps')}>
										<input
											class={inputClass}
											placeholder={$i18n.t('Enter Number of Steps (e.g. 50)')}
											bind:value={currentModel.IMAGE_STEPS}
											required
										/>
									</AdminSettingField>
								{/if}
							</div>

							<!-- OPENAI SETTINGS -->
							{#if currentModel?.IMAGE_GENERATION_ENGINE === 'openai'}
								<div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
									<AdminSettingField label={$i18n.t('API Base URL')}>
										<input
											class={inputClass}
											placeholder={$i18n.t('API Base URL')}
											bind:value={currentModel.IMAGES_OPENAI_API_BASE_URL}
										/>
									</AdminSettingField>

									<AdminSettingField label={$i18n.t('API Key')}>
										<SensitiveInput
											variant="settings"
											placeholder={$i18n.t('API Key')}
											bind:value={currentModel.IMAGES_OPENAI_API_KEY}
											required={false}
										/>
									</AdminSettingField>
								</div>

								<AdminSettingField label={$i18n.t('API Version')}>
									<input
										class={inputClass}
										placeholder={$i18n.t('API Version')}
										bind:value={currentModel.IMAGES_OPENAI_API_VERSION}
									/>
								</AdminSettingField>

								<AdminSettingField
									label={$i18n.t('Additional Parameters')}
									description={$i18n.t('Send extra JSON parameters with each image generation request.')}
								>
									<Textarea
										className={textareaClass}
										bind:value={currentModel.IMAGES_OPENAI_API_PARAMS}
										placeholder={$i18n.t('Enter additional parameters in JSON format')}
										minSize={100}
									/>
								</AdminSettingField>

							<!-- AUTOMATIC1111 SETTINGS -->
							{:else if (currentModel?.IMAGE_GENERATION_ENGINE ?? 'automatic1111') === 'automatic1111'}
								<AdminSettingField
									label={$i18n.t('Base URL')}
									description={$i18n.t('Connect to a stable-diffusion-webui server running with the `--api` flag.')}
								>
									<div class="flex w-full gap-2">
										<input
											class={inputClass}
											placeholder={$i18n.t('Enter URL (e.g. http://127.0.0.1:7860/)')}
											bind:value={currentModel.AUTOMATIC1111_BASE_URL}
										/>
										<button
											class="shrink-0 text-gray-400 transition-colors hover:text-gray-900 dark:text-gray-600 dark:hover:text-white"
											type="button"
											aria-label="verify connection"
											on:click={async () => {
												await updateConfigHandler();
												const res = await verifyConfigUrl(localStorage.token).catch((error) => {
													toast.error(`${error}`);
													return null;
												});
												if (res) toast.success($i18n.t('Server connection verified'));
											}}
										>
											<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
												<path fill-rule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z" clip-rule="evenodd" />
											</svg>
										</button>
									</div>
								</AdminSettingField>

								<AdminSettingField
									label={$i18n.t('API Auth String')}
									description={$i18n.t('Provide the --api-auth username and password when required.')}
								>
									<SensitiveInput
										variant="settings"
										placeholder={$i18n.t('Enter api auth string (e.g. username:password)')}
										bind:value={currentModel.AUTOMATIC1111_API_AUTH}
										required={false}
									/>
								</AdminSettingField>

								<AdminSettingField
									label={$i18n.t('Additional Parameters')}
									description={$i18n.t('Send extra JSON parameters with each AUTOMATIC1111 request.')}
								>
									<Textarea
										className={textareaClass}
										bind:value={currentModel.AUTOMATIC1111_PARAMS}
										placeholder={$i18n.t('Enter additional parameters in JSON format')}
										minSize={100}
									/>
								</AdminSettingField>

							<!-- COMFYUI SETTINGS -->
							{:else if currentModel?.IMAGE_GENERATION_ENGINE === 'comfyui'}
								<AdminSettingField
									label={$i18n.t('Base URL')}
									description={$i18n.t('Connect to the ComfyUI server used for generation.')}
								>
									<div class="flex w-full gap-2">
										<input
											class={inputClass}
											placeholder={$i18n.t('Enter URL (e.g. http://127.0.0.1:7860/)')}
											bind:value={currentModel.COMFYUI_BASE_URL}
										/>
									</div>
								</AdminSettingField>

								<AdminSettingField label={$i18n.t('API Key')}>
									<SensitiveInput
										variant="settings"
										placeholder={$i18n.t('sk-1234')}
										bind:value={currentModel.COMFYUI_API_KEY}
										required={false}
									/>
								</AdminSettingField>

							<!-- GEMINI SETTINGS -->
							{:else if currentModel?.IMAGE_GENERATION_ENGINE === 'gemini'}
								<AdminSettingField label={$i18n.t('Base URL')}>
									<input
										class={inputClass}
										placeholder={$i18n.t('API Base URL')}
										bind:value={currentModel.IMAGES_GEMINI_API_BASE_URL}
									/>
								</AdminSettingField>

								<AdminSettingField label={$i18n.t('API Key')}>
									<SensitiveInput
										variant="settings"
										placeholder={$i18n.t('API Key')}
										bind:value={currentModel.IMAGES_GEMINI_API_KEY}
										required={true}
									/>
								</AdminSettingField>
							{/if}

							<!-- LÖSCHEN BUTTON FÜR DIESES MODELL -->
							<div class="flex justify-end pt-4 border-t border-gray-100 dark:border-gray-800">
								<button
									class="px-3 py-1.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition"
									type="button"
									on:click={() => removeModelHandler(selectedModelIndex)}
								>
									{$i18n.t('Remove Model Configuration')}
								</button>
							</div>

						</div>
					{:else}
						<div class="text-center py-6 text-sm text-gray-500">
							{$i18n.t('No image generation models configured yet. Click "+ Add Model" to create one.')}
						</div>
					{/if}
				</AdminSettingSection>
			{/if}
		</div>
	{/if}
</div>
				<!--	
				<AdminSettingSection title={$i18n.t('Edit Image')}>
					<AdminSettingRow
						label={$i18n.t('Image Edit')}
						description={$i18n.t('Allow users to edit existing images.')}
						let:labelId
					>
						<Switch bind:state={config.ENABLE_IMAGE_EDIT} ariaLabelledbyId={labelId} />
					</AdminSettingRow>

					<AdminSettingRow
						label={$i18n.t('Image Edit Engine')}
						description={$i18n.t('Choose the provider used for image edits.')}
					>
						<SettingsSelect
							bind:value={config.IMAGE_EDIT_ENGINE}
							placeholder={$i18n.t('Select Engine')}
						>
							<option value="openai">{$i18n.t('Default (Open AI)')}</option>
							<option value="comfyui">{$i18n.t('ComfyUI')}</option>
							<option value="gemini">{$i18n.t('Gemini')}</option>
						</SettingsSelect>
					</AdminSettingRow>

					{#if config?.ENABLE_IMAGE_GENERATION && config?.ENABLE_IMAGE_EDIT}
						<div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
							<AdminSettingField label={$i18n.t('Model')}>
								<input
									list="model-list"
									class={inputClass}
									bind:value={config.IMAGE_EDIT_MODEL}
									placeholder={$i18n.t('Select a model')}
								/>

								<datalist id="model-list">
									{#each models ?? [] as model}
										<option value={model.id}>{model.name}</option>
									{/each}
								</datalist>
							</AdminSettingField>

							<AdminSettingField label={$i18n.t('Image Size')}>
								<input
									class={inputClass}
									placeholder={$i18n.t('Enter Image Size (e.g. 512x512)')}
									bind:value={config.IMAGE_EDIT_SIZE}
								/>
							</AdminSettingField>
						</div>
					{/if}

					{#if config?.IMAGE_EDIT_ENGINE === 'openai'}
						<div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
							<AdminSettingField label={$i18n.t('API Base URL')}>
								<input
									class={inputClass}
									placeholder={$i18n.t('API Base URL')}
									bind:value={config.IMAGES_EDIT_OPENAI_API_BASE_URL}
								/>
							</AdminSettingField>

							<AdminSettingField label={$i18n.t('API Key')}>
								<SensitiveInput
									variant="settings"
									placeholder={$i18n.t('API Key')}
									bind:value={config.IMAGES_EDIT_OPENAI_API_KEY}
									required={false}
								/>
							</AdminSettingField>
						</div>

						<AdminSettingField label={$i18n.t('API Version')}>
							<input
								class={inputClass}
								placeholder={$i18n.t('API Version')}
								bind:value={config.IMAGES_EDIT_OPENAI_API_VERSION}
							/>
						</AdminSettingField>
					{:else if config?.IMAGE_EDIT_ENGINE === 'comfyui'}
						<AdminSettingField
							label={$i18n.t('Base URL')}
							description={$i18n.t('Connect to the ComfyUI server used for image edits.')}
						>
							<div class="flex w-full gap-2">
								<input
									class={inputClass}
									placeholder={$i18n.t('Enter URL (e.g. http://127.0.0.1:7860/)')}
									bind:value={config.IMAGES_EDIT_COMFYUI_BASE_URL}
								/>
								<button
									class="shrink-0 text-gray-400 transition-colors hover:text-gray-900 dark:text-gray-600 dark:hover:text-white"
									type="button"
									aria-label="verify connection"
									on:click={async () => {
										await updateConfigHandler();
										const res = await verifyConfigUrl(localStorage.token).catch((error) => {
											toast.error(`${error}`);
											return null;
										});

										if (res) {
											toast.success($i18n.t('Server connection verified'));
										}
									}}
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										viewBox="0 0 20 20"
										fill="currentColor"
										class="w-4 h-4"
									>
										<path
											fill-rule="evenodd"
											d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z"
											clip-rule="evenodd"
										/>
									</svg>
								</button>
							</div>
						</AdminSettingField>

						<AdminSettingField
							label={$i18n.t('API Key')}
							description={$i18n.t('Use an API key when your ComfyUI server requires one.')}
						>
							<SensitiveInput
								variant="settings"
								placeholder={$i18n.t('sk-1234')}
								bind:value={config.IMAGES_EDIT_COMFYUI_API_KEY}
								required={false}
							/>
						</AdminSettingField>

						<div>
							<input
								id="upload-comfyui-edit-workflow-input"
								hidden
								type="file"
								accept=".json"
								on:change={(e) => {
									const file = e.target.files[0];
									const reader = new FileReader();

									reader.onload = (e) => {
										config.IMAGES_EDIT_COMFYUI_WORKFLOW = e.target.result;
										e.target.value = null;
									};

									reader.readAsText(file);
								}}
							/>
							<AdminSettingRow
								label={$i18n.t('ComfyUI Workflow')}
								description={$i18n.t(
									'Upload a workflow.json file exported as API format from ComfyUI.'
								)}
							>
								<div class="flex items-center justify-end gap-2">
									{#if config.IMAGES_EDIT_COMFYUI_WORKFLOW}
										<button
											class="text-xs text-gray-500 transition-colors hover:text-gray-900 hover:underline dark:text-gray-500 dark:hover:text-white"
											type="button"
											aria-label={$i18n.t('Edit workflow.json content')}
											on:click={() => {
												// open code editor modal
												showComfyUIEditWorkflowEditor = true;
											}}
										>
											{$i18n.t('Edit')}
										</button>
									{/if}

									<Tooltip content={$i18n.t('Click here to upload a workflow.json file.')}>
										<button
											class="text-xs text-gray-500 transition-colors hover:text-gray-900 hover:underline dark:text-gray-500 dark:hover:text-white"
											type="button"
											aria-label={$i18n.t('Click here to upload a workflow.json file.')}
											on:click={() => {
												document.getElementById('upload-comfyui-edit-workflow-input')?.click();
											}}
										>
											{$i18n.t('Upload')}
										</button>
									</Tooltip>
								</div>
							</AdminSettingRow>

							<CodeEditorModal
								bind:show={showComfyUIEditWorkflowEditor}
								value={config.IMAGES_EDIT_COMFYUI_WORKFLOW}
								lang="json"
								onChange={(e) => {
									config.IMAGES_EDIT_COMFYUI_WORKFLOW = e;
								}}
								onSave={() => {
									console.log('Saved');
								}}
							/>
						</div>

						{#if config.IMAGES_EDIT_COMFYUI_WORKFLOW}
							<AdminSettingField
								label={$i18n.t('ComfyUI Workflow Nodes')}
								description={$i18n.t('Map workflow node inputs used for image edits.')}
							>
								<div class="flex flex-col gap-1.5 text-xs">
									{#each REQUIRED_EDIT_WORKFLOW_NODES as node}
										<div class="flex w-full flex-col">
											<div class="shrink-0">
												<div class=" capitalize line-clamp-1 w-20 text-gray-400 dark:text-gray-500">
													{node.type}{['prompt', 'image'].includes(node.type) ? '*' : ''}
												</div>
											</div>

											<div class="flex mt-0.5 items-center">
												<div class="">
													<Tooltip content={$i18n.t('Input Key (e.g. text, unet_name, steps)')}>
														<input
															class="{inputClass} w-24"
															placeholder={$i18n.t('Key')}
															bind:value={node.key}
															required
														/>
													</Tooltip>
												</div>

												<div class="px-2 text-gray-400 dark:text-gray-500">:</div>

												<div class="w-full">
													<Tooltip
														content={$i18n.t('Comma separated Node Ids (e.g. 1 or 1,2)')}
														placement="top-start"
													>
														<input
															class={inputClass}
															placeholder={$i18n.t('Node Ids')}
															bind:value={node.node_ids}
														/>
													</Tooltip>
												</div>
											</div>
										</div>
									{/each}
								</div>

								<div class="mt-1 text-xs text-gray-400 dark:text-gray-500">
									{$i18n.t('*Prompt node ID(s) are required for image generation')}
								</div>
							</AdminSettingField>
						{/if}
					{:else if config?.IMAGE_EDIT_ENGINE === 'gemini'}
						<div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
							<AdminSettingField label={$i18n.t('Base URL')}>
								<input
									class={inputClass}
									placeholder={$i18n.t('API Base URL')}
									bind:value={config.IMAGES_EDIT_GEMINI_API_BASE_URL}
								/>
							</AdminSettingField>

							<AdminSettingField label={$i18n.t('API Key')}>
								<SensitiveInput
									variant="settings"
									placeholder={$i18n.t('API Key')}
									bind:value={config.IMAGES_EDIT_GEMINI_API_KEY}
									required={true}
								/>
							</AdminSettingField>
						</div>
					{/if}
				</AdminSettingSection>
			-->
				
	<div class="flex justify-end pt-6 text-sm font-normal">
		<button
			class="px-3.5 py-1.5 text-sm font-normal bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full flex items-center gap-2 whitespace-nowrap {loading
				? ' cursor-not-allowed'
				: ''}"
			type="submit"
			disabled={loading}
		>
			{$i18n.t('Save')}

			{#if loading}
				<span class="shrink-0">
					<Spinner />
				</span>
			{/if}
		</button>
	</div>
</form>
