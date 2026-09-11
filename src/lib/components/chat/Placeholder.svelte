<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	import { onMount, getContext, tick, createEventDispatcher } from 'svelte';
	import { blur, fade } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	import { updateFolderById } from '$lib/apis/folders';

	import {
		config,
		user,
		models as _models,
		temporaryChatEnabled,
		selectedFolder
	} from '$lib/stores';
	import { refreshChatList, refreshFolderChatLists } from '$lib/stores/chatList';
	import { sanitizeResponseContent, extractCurlyBraceWords } from '$lib/utils';
	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';

	import Suggestions from './Suggestions.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
	import MessageInput from './MessageInput.svelte';
	import FolderPlaceholder from './Placeholder/FolderPlaceholder.svelte';
	import FolderTitle from './Placeholder/FolderTitle.svelte';

	const i18n = getContext('i18n');

	export let createMessagePair: Function;
	export let stopResponse: Function;

	export let autoScroll = false;

	export let atSelectedModel: Model | undefined;
	export let selectedModels: [''];

	export let history;

	export let prompt = '';
	export let files = [];
	export let messageInput = null;

	export let selectedToolIds = [];
	export let selectedSkillIds = [];
	export let selectedFilterIds = [];
	export let pendingOAuthTools = [];

	export let showCommands = false;

	export let imageGenerationEnabled = false;
	export let codeInterpreterEnabled = false;
	export let webSearchEnabled = false;
	export let toolApprovalMode = 'full';
	export let onToolApprovalModeChange: Function = () => {};
	export let oauthRedirectHandler: Function = () => {};

	export let onUpload: Function = (e) => {};
	export let onUpdate: (data?: { file?: any }) => void = () => {};
	export let onSelect = (e) => {};
	export let onChange = (e) => {};
	export let onWebSearchToggle: Function = () => {};
	export let messageQueue: { id: string; prompt: string; files: any[] }[] = [];
	export let onQueueSendNow: (id: string) => void = () => {};
	export let onQueueEdit: (id: string) => void = () => {};
	export let onQueueDelete: (id: string) => void = () => {};
	export let askUser = {
		show: false,
		questions: [],
		allowOther: true,
		timeoutMs: null,
		onConfirm: (_value: any) => {},
		onCancel: () => {}
	};

	export let dragged = false;

	let models = [];
	let selectedModelIdx = 0;

	$: if (selectedModels.length > 0) {
		selectedModelIdx = models.length - 1;
	}

	function getTimeBasedTitles(): string[] {
		const hour = new Date().getHours();
		const day = new Date().getDay();

		// Nachts (0 - 5 Uhr)
		if (hour < 6)
			return [
				'Sonnenaufgangsgespräche!',
				'Vor dem ersten Kaffee?',
				'Schlummerlos, {name}?',
				'Schlaflos, {name}?',
				'Ausgeschlafen, {name}?',
				'Eulen-Klub!',
				'Frühschichtgedanken!',
				'Gedanken zur Geisterstunde!',
				'Wenn die Welt schläft...',
				'Nachtgedanken, {name}?',
				'Warum schläfst du nicht, {name}?',
				'Nachtcafe',
				'Worum geht, {name}?'
			];
		// Morgens (6 - 10 Uhr)
		if (hour < 11)
			return [
				'Morgenkaffee-Gespräche',
				'Frühaufsteher, {name}?',
				'Guten-Morgen-Runde',
				"Was gibt's Neues, {name}?",
				'Erster Kaffee, {name}?',
				'Frisch in den Tag!',
				'Morgen-Brainstorming!',
				'Startklar für heute, {name}?',
				'Morgen-Motivation!',
				'Kein Meeting, {name}?',
				'Worum geht, {name}?'
			];
		// Mittags (11 - 13 Uhr)
		if (hour < 14)
			return [
				'Mittagspause-Plauderei',
				'Kurzer Gedankenaustausch',
				"Was gibt's Neues, {name}?",
				'Halbzeit!',
				'Magenknurren, {name}?',
				'Lunch & Chat!',
				'Kopf frei für die Mittagspause!',
				'Kurze Pause, {name}?',
				'Mittagsgedanken!',
				'Mittagspausen-Flow!',
				'Worum geht, {name}?'
			];
		// Nachmittags (14 - 17 Uhr)
		if (hour < 18)
			return [
				'Nachmittagsgespräche',
				'Kopfkino-Session',
				'Ist noch was, {name}?',
				"Was gibt's Neues, {name}?",
				'Bald Feierabend, {name}?',
				'Noch ein kleiner Impuls?',
				'Nachmittags-Flow!',
				'Kaffeepause, {name}?',
				'Gedanken zum Feierabend!',
				'Noch einmal durchziehen',
				'Kreativ am Nachmittag!',
				'Letzte Kraftreserven!',
				'Worum geht, {name}?'
			];
		// Abends (18 - 23 Uhr)
		return [
			'Mondscheingespräche!',
			'Noch kein Feierabend, {name}?',
			'Abendgedanken, {name}?',
			'Sonnenuntergangsplauderei!',
			"Was gibt's Neues, {name}?",
			'Abend Routine!',
			'Entspannund am Abend',
			'Abend-Flow!',
			'Kopfkino am Abend!',
			'Abendliche Inspiration!',
			'Letzte Ideen vor dem Schlafen!',
			'Tagesrückblick, {name}?',
			'Feierabendmodus: AN!',
			'Später chat, {name}?',
			'Noch was wichtiges, {name}?',
			'Worum geht, {name}?'
		];
	}

	let randomFunTitle = '';

	onMount(() => {
		const titles = getTimeBasedTitles();
		const randomIndex = Math.floor(Math.random() * titles.length);

		randomFunTitle = titles[randomIndex].replace('{name}', $user?.name ?? '');
	});

	$: models = selectedModels.map((id) => $_models.find((m) => m.id === id));

	// True when viewing a shared folder the current user doesn't own AND lacks write access
	$: folderReadOnly =
		$selectedFolder != null &&
		$selectedFolder.user_id !== $user?.id &&
		$selectedFolder.permission !== 'write';
</script>

<div class="m-auto w-full max-w-[58rem] px-1 @2xl:px-20 translate-y-6 py-24 text-center">
	{#if $temporaryChatEnabled}
		<Tooltip
			content={$i18n.t("This chat won't appear in history and your messages will not be saved.")}
			className="w-full flex justify-center mb-0.5"
			placement="top"
		>
			<div class="flex items-center gap-1.5 text-gray-500 text-xs my-1 w-fit">
				<EyeSlash strokeWidth="2" className="size-3.5" />{$i18n.t('Temporary Chat')}
			</div>
		</Tooltip>
	{/if}

	<div class="w-full text-3xl text-gray-800 dark:text-gray-100 text-center flex items-center gap-4">
		<div class="w-full flex flex-col justify-center items-center">
			<div class="flex flex-row justify-center items-center gap-3 w-fit px-5">
				<div class="flex shrink-0 justify-center">
					<div class="flex -space-x-4" in:fade={{ duration: 100 }}>
						{#each models as model, modelIdx}
							<Tooltip
								content={(models[modelIdx]?.info?.meta?.tags ?? [])
									.map((tag) => tag.name.toUpperCase())
									.join(', ')}
								placement="top"
							>
								<button
									aria-hidden={models.length <= 1}
									aria-label={$i18n.t('Get information on {{name}} in the UI', {
										name: models[modelIdx]?.name
									})}
									on:click={() => {
										selectedModelIdx = modelIdx;
									}}
								>
									<!-- LOGO GROESSE ANPASSEN (size-11 statt size-9) -->
									<img
										src={`${WEBUI_API_BASE_URL}/models/model/profile/image?id=${model?.id}&lang=${$i18n.language}`}
										class="size-10 @sm:size-11 rounded-2xl"
										aria-hidden="true"
										draggable="false"
										on:error={(e) => {
											e.currentTarget.src = '/favicon.png';
										}}
									/>
								</button>
							</Tooltip>
						{/each}
					</div>
				</div>

				<div in:fade={{ duration: 100 }}>
					<span class="custom-title text-3xl @sm:text-4xl font-medium tracking-tight text-center">
						{randomFunTitle || $i18n.t('Hello, {{name}}', { name: $user?.name })}
					</span>
				</div>
			</div>

			<div class="flex mt-1 mb-2">
				<div in:fade={{ duration: 100, delay: 50 }}>
					{#if models[selectedModelIdx]?.info?.meta?.description ?? null}
						<Tooltip
							className=" w-fit"
							content={DOMPurify.sanitize(
								marked.parse(
									sanitizeResponseContent(
										models[selectedModelIdx]?.info?.meta?.description ?? ''
									).replaceAll('\n', '<br>')
								)
							)}
							placement="top"
						>
							<div
								class="mt-0.5 px-2 text-sm font-normal text-gray-500 dark:text-gray-400 line-clamp-2 max-w-xl markdown"
							>
								{@html DOMPurify.sanitize(
									marked.parse(
										sanitizeResponseContent(
											models[selectedModelIdx]?.info?.meta?.description ?? ''
										).replaceAll('\n', '<br>')
									)
								)}
							</div>
						</Tooltip>

						{#if models[selectedModelIdx]?.info?.meta?.user}
							<div class="mt-0.5 text-sm font-normal text-gray-400 dark:text-gray-500">
								By
								{#if models[selectedModelIdx]?.info?.meta?.user.community}
									<a
										href="https://openwebui.com/m/{models[selectedModelIdx]?.info?.meta?.user
											.username}"
										>{models[selectedModelIdx]?.info?.meta?.user.name
											? models[selectedModelIdx]?.info?.meta?.user.name
											: `@${models[selectedModelIdx]?.info?.meta?.user.username}`}</a
									>
								{:else}
									{models[selectedModelIdx]?.info?.meta?.user.name}
								{/if}
							</div>
						{/if}
					{/if}
				</div>
			</div>

			<div class="text-base font-normal @md:max-w-3xl w-full py-3 {atSelectedModel ? 'mt-2' : ''}">
				{#if !($selectedFolder && folderReadOnly)}
					<MessageInput
						bind:this={messageInput}
						{history}
						bind:selectedModels
						bind:files
						bind:prompt
						bind:autoScroll
						bind:selectedToolIds
						bind:selectedSkillIds
						bind:selectedFilterIds
						bind:imageGenerationEnabled
						bind:codeInterpreterEnabled
						bind:webSearchEnabled
						bind:atSelectedModel
						bind:showCommands
						bind:dragged
						{pendingOAuthTools}
						{oauthRedirectHandler}
						{toolApprovalMode}
						{onToolApprovalModeChange}
						{stopResponse}
						{createMessagePair}
						placeholder={$i18n.t('How can I help you today?')}
						{onChange}
						{onUpload}
						{onUpdate}
						{messageQueue}
						{onQueueSendNow}
						{onQueueEdit}
						{onQueueDelete}
						{askUser}
						{onWebSearchToggle}
						on:chatVariables
						on:submit={(e) => {
							dispatch('submit', e.detail);
						}}
					/>
				{/if}
			</div>
		</div>
	</div>

	{#if $selectedFolder}
		<div class="mx-auto px-4 md:max-w-3xl md:px-6 min-h-62" in:fade={{ duration: 200, delay: 200 }}>
			<FolderPlaceholder folder={$selectedFolder} />
		</div>
	{:else}
		<div class="mx-auto max-w-2xl mt-2" in:fade={{ duration: 200, delay: 200 }}>
			<div class="mx-5">
				<Suggestions
					suggestionPrompts={atSelectedModel?.info?.meta?.suggestion_prompts ??
						models[selectedModelIdx]?.info?.meta?.suggestion_prompts ??
						$config?.default_prompt_suggestions ??
						[]}
					inputValue={prompt}
					{onSelect}
				/>
			</div>
		</div>
	{/if}
</div>

<style>
	/* Google Font direkt importieren */
	@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700&display=swap');

	.custom-title {
		font-family: 'Plus Jakarta Sans', sans-serif;
		letter-spacing: -0.02em; /* Macht fette UI-Überschriften viel moderner */
	}
</style>
