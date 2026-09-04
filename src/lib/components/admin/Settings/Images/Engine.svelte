<script lang="ts">
	import { getContext } from 'svelte';
	export let config: any;
	import AdminSettingField from '../AdminSettingField.svelte';
	import AdminSettingSection from '../AdminSettingSection.svelte';
	import SettingsSelect from '$lib/components/common/SettingsSelect.svelte';	
	
	const i18n: any = getContext('i18n');

	// Säubert engine-spezifische Keys, sobald der Provider gewechselt wird
	function handleEngineChange(event: Event) {
		const newEngine = (event.target as HTMLSelectElement).value;
		config.IMAGE_GENERATION_ENGINE = newEngine;

		if (newEngine !== 'openai') {
			delete config.IMAGES_OPENAI_API_KEY;
			delete config.IMAGES_OPENAI_API_BASE_URL;
			delete config.IMAGES_OPENAI_API_PARAMS;
		}

		if (newEngine !== 'gemini') {
			delete config.IMAGES_GEMINI_API_KEY;
			delete config.IMAGES_GEMINI_API_BASE_URL;
		}

		if (newEngine !== 'automatic1111') {
			delete config.AUTOMATIC1111_BASE_URL;
			delete config.AUTOMATIC1111_PARAMS;
			delete config.AUTOMATIC1111_CFG_SCALE;
			delete config.AUTOMATIC1111_SAMPLER;
		}

		if (newEngine !== 'comfyui') {
			delete config.COMFYUI_BASE_URL;
			delete config.COMFYUI_WORKFLOW;
			delete config.COMFYUI_WORKFLOW_NODES;
		}
	}
</script>

<AdminSettingField
	label={$i18n.t('Image Generation Engine')}
	description={$i18n.t('Choose the provider used for image generation.')}
>
	<SettingsSelect
		bind:value={config.IMAGE_GENERATION_ENGINE}
		on:change={handleEngineChange}
		placeholder={$i18n.t('Select Engine')}
	>
		<option value="openai">{$i18n.t('Default (Open AI)')}</option>
		<!-- <option value="comfyui">{$i18n.t('ComfyUI')}</option> -->
		<!-- <option value="automatic1111">{$i18n.t('Automatic1111')}</option> -->
		<option value="gemini">{$i18n.t('Gemini')}</option>
	</SettingsSelect>
</AdminSettingField>