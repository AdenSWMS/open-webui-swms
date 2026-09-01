<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	import {
		WEBUI_NAME,
		banners,
		chatId,
		config,
		mobile,
		settings,
		showControls,
		showSidebar,
		temporaryChatEnabled,
		user
	} from '$lib/stores';

	import { slide } from 'svelte/transition';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	import ShareChatModal from '../chat/ShareChatModal.svelte';
	import ProjectPresenter from './ProjectSelector/ProjectPresenter.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import Menu from '$lib/components/layout/Navbar/Menu.svelte';
	import AdjustmentsHorizontal from '../icons/AdjustmentsHorizontal.svelte';

	import PencilSquare from '../icons/PencilSquare.svelte';
	import Banner from '../common/Banner.svelte';
	import Sidebar from '../icons/Sidebar.svelte';

	import ChatBubbleDotted from '../icons/ChatBubbleDotted.svelte';
	import ChatBubbleDottedChecked from '../icons/ChatBubbleDottedChecked.svelte';

	import EllipsisHorizontal from '../icons/EllipsisHorizontal.svelte';
	import ChatPlus from '../icons/ChatPlus.svelte';
	import ChatCheck from '../icons/ChatCheck.svelte';
	import Knobs from '../icons/Knobs.svelte';
	import { isTemporaryChatId } from '$lib/utils/chatId';
	import { getUserInfo } from '$lib/apis/litellm';
	import type { UserInfoResponse } from '$lib/apis/litellm';
	import NavbarBudgetButton from './NavbarBudgetButton.svelte';
	const i18n = getContext('i18n');

	export let initNewChat: Function;
	export let readOnly: boolean = false;
	export let shareEnabled: boolean = false;
	export let scrollTop = 0;
	export let scrollToTop: (() => void) | null = null;

	export let chat;
	export let history;
	export let title = '';

	export let selectedProjects;

	export let onSaveTempChat: () => {};
	export let archiveChatHandler: (id: string) => void;
	export let deleteChatHandler: (id: string) => void;
	export let moveChatHandler: (id: string, folderId: string) => void;

	let closedBannerIds = [];

	const getDismissedBannerIds = (): string[] => {
		try {
			return JSON.parse(localStorage.getItem('dismissedBannerIds') ?? '[]');
		} catch {
			return [];
		}
	};

	let showShareChatModal = false;
	let showDownloadChatModal = false;

	import OpenCodeModal from './OpenCodeModal.svelte';
	let showOpenCodeModal = false;

	import BudgetModal from './BudgetModal.svelte';
	let showBudgetModal = false;
	let userData: UserInfoResponse | null = null;
	let error: string | null = null;
	async function loadUserData() {
		error = null;

		try {
			const token = localStorage.getItem('token') || '';

			if (!token) {
				throw new Error('Kein Authentifizierungs-Token gefunden.');
			}

			userData = await getUserInfo(token);
		} catch (err: any) {
			console.error('Fehler beim Laden der Budgetdaten:', err);
			error = typeof err === 'string' ? err : err?.message || 'Fehler beim Laden der Daten.';
		}
	}

	async function openBudgetModal() {
		showBudgetModal = true;
		await loadUserData();
	}

	onMount(async () => {
		try {
			const token = localStorage.getItem('token') || '';
			if (token) {
				userData = await getUserInfo(token);
			}
		} catch (err) {
			console.error('Fehler beim Abrufen der Nutzerdaten für Navbar:', err);
		}
	});
</script>

<ShareChatModal bind:show={showShareChatModal} chatId={$chatId} />

<button
	id="new-chat-button"
	class="hidden"
	on:click={() => {
		initNewChat();
	}}
	aria-label="New Chat"
/>

<nav
	class="sticky top-0 z-30 w-full {$mobile
		? 'pt-1.5'
		: 'pt-0.5'} pb-1 -mb-12 flex flex-col items-center drag-region"
>
	<div class="flex items-center w-full {$mobile ? 'px-2.5' : 'pl-1.5 pr-1'}">
		<div
			id="navbar-bg-gradient-to-b"
			class="{chat?.id
				? 'visible'
				: 'invisible'} bg-linear-to-b via-40% to-97% from-white/90 via-white/50 to-transparent dark:from-gray-900/90 dark:via-gray-900/50 dark:to-transparent pointer-events-none absolute inset-0 -bottom-10 z-[-1]"
		></div>
		<div class=" flex max-w-full w-full mx-auto bg-transparent">
			<div class="flex items-center w-full max-w-full gap-2 md:gap-4">
				{#if $mobile && !$showSidebar}
					<div class="mr-1 flex flex-none items-center self-center">
						<Tooltip content={$showSidebar ? $i18n.t('Close Sidebar') : $i18n.t('Open Sidebar')}>
							<button
								id="sidebar-toggle-button"
								class="flex cursor-pointer rounded-lg text-gray-500 transition hover:bg-gray-50/40 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800/40 dark:hover:text-gray-200"
								on:click={() => {
									showSidebar.set(!$showSidebar);
								}}
								aria-label={$showSidebar ? $i18n.t('Close Sidebar') : $i18n.t('Open Sidebar')}
							>
								<div class="self-center p-1.5">
									<Sidebar className="size-4" />
								</div>
							</button>
						</Tooltip>
					</div>
				{/if}

				<!-- Linker Bereich: Titel / Chat-Info -->
				<div
					class="flex-none flex items-center gap-2 overflow-hidden max-w-[30%] mt-0.5 py-0.5 {$showSidebar
						? 'ml-1'
						: ''}"
				>
					<div class="shrink-0">
						<ProjectPresenter bind:selectedProjects />
					</div>
					{#if chat?.id}
						<div class="flex max-w-full min-w-0 items-center gap-2 mr-2">
							<div
								class="min-w-0 truncate py-1 text-left text-[0.9375rem] font-normal text-gray-700 dark:text-gray-300"
							>
								{title || chat?.chat?.title || $i18n.t('New Chat')}
							</div>

							{#if shareEnabled && chat && (chat.id || $temporaryChatEnabled)}
								<Menu
									{chat}
									{shareEnabled}
									{readOnly}
									{scrollToTop}
									shareHandler={() => {
										showShareChatModal = !showShareChatModal;
									}}
									archiveChatHandler={() => {
										archiveChatHandler(chat.id);
									}}
									deleteChatHandler={() => {
										deleteChatHandler(chat.id);
									}}
									{moveChatHandler}
								>
									<button
										class="flex size-6 shrink-0 cursor-pointer items-center justify-center rounded-lg text-gray-500 transition hover:bg-gray-50/40 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800/40 dark:hover:text-gray-200"
										id="chat-context-menu-button"
										aria-label={$i18n.t('Chat actions')}
									>
										<EllipsisHorizontal className="size-4.5" strokeWidth="1.5" />
									</button>
								</Menu>
							{/if}
						</div>
					{:else}
						<div class="pointer-events-none invisible flex max-w-full min-w-0 items-center gap-2">
							<div
								class="min-w-0 truncate py-1 text-left text-[0.9375rem] font-normal text-gray-700 dark:text-gray-300"
							>
								{$i18n.t('New Chat')}
							</div>
						</div>
					{/if}
				</div>

				<div class="lg:mr-1 flex-1 flex justify-center items-center gap-2 self-center">
					<div class="w-full max-w-2xl flex items-center justify-center">
						{#if userData}
							<NavbarBudgetButton
								{userData}
								onClick={openBudgetModal}
							/>
						{:else if error}
							<div
								class="w-full text-center px-3 py-1.5 text-xs text-red-500 bg-red-100 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800/30"
							>
								{error}
							</div>
						{:else}
							<button
								type="button"
								on:click={openBudgetModal}
								class="w-full inline-flex items-center justify-center gap-2 px-3 py-1 text-xs font-medium bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition cursor-pointer"
							>
								Budget abrufen
							</button>
						{/if}

						<BudgetModal bind:show={showBudgetModal} {userData} />
					</div>
				</div>

				<div class="flex-none flex items-center gap-2 text-gray-600 dark:text-gray-400">
					<div class="flex items-center gap-2">
						<button
							class="px-3 py-1 text-xs font-medium bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition cursor-pointer"
							on:click={() => (showOpenCodeModal = true)}
						>
							OpenCode & API-Key
						</button>
						<OpenCodeModal bind:show={showOpenCodeModal} />
					</div>

					{#if $user?.role === 'user' ? ($user?.permissions?.chat?.temporary ?? true) && !($user?.permissions?.chat?.temporary_enforced ?? false) : true}
						{#if !chat?.id}
							<Tooltip content={$i18n.t(`Temporary Chat`)}>
								<button
									class="flex size-6 cursor-pointer items-center justify-center rounded-lg text-gray-500 transition hover:bg-gray-50/40 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800/40 dark:hover:text-gray-200"
									id="temporary-chat-button"
									on:click={async () => {
										if (($settings?.temporaryChatByDefault ?? false) && $temporaryChatEnabled) {
											await temporaryChatEnabled.set(null);
										} else {
											await temporaryChatEnabled.set(!$temporaryChatEnabled);
										}

										if ($page.url.pathname !== '/') {
											await goto('/');
										}

										if ($temporaryChatEnabled) {
											window.history.replaceState(null, '', '?temporary-chat=true');
										} else {
											window.history.replaceState(null, '', location.pathname);
										}
									}}
									aria-label={$i18n.t(`Temporary Chat`)}
								>
									{#if $temporaryChatEnabled}
										<ChatBubbleDottedChecked className="size-4.5" strokeWidth="1.5" />
									{:else}
										<ChatBubbleDotted className="size-4.5" strokeWidth="1.5" />
									{/if}
								</button>
							</Tooltip>
						{:else if $temporaryChatEnabled}
							<Tooltip content={$i18n.t(`Save Chat`)}>
								<button
									class="flex size-6 cursor-pointer items-center justify-center rounded-lg text-gray-500 transition hover:bg-gray-50/40 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800/40 dark:hover:text-gray-200"
									id="save-temporary-chat-button"
									on:click={async () => {
										onSaveTempChat();
									}}
									aria-label={$i18n.t(`Save Chat`)}
								>
									<ChatCheck className="size-4.5" strokeWidth="1.5" />
								</button>
							</Tooltip>
						{/if}
					{/if}

					{#if $mobile && !$temporaryChatEnabled && chat && chat.id}
						<Tooltip content={$i18n.t('New Chat')}>
							<button
								class="flex size-6 {$showSidebar
									? 'md:hidden'
									: ''} cursor-pointer items-center justify-center rounded-lg text-gray-500 transition hover:bg-gray-50/40 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800/40 dark:hover:text-gray-200"
								on:click={() => {
									initNewChat();
								}}
								aria-label="New Chat"
							>
								<ChatPlus className="size-4.5" strokeWidth="1.5" />
							</button>
						</Tooltip>
					{/if}

					{#if $user?.role === 'admin' || ($user?.permissions.chat?.controls ?? true)}
						<Tooltip content={$i18n.t('Controls')}>
							<button
								class="flex size-6 cursor-pointer items-center justify-center rounded-lg text-gray-500 transition hover:bg-gray-50/40 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800/40 dark:hover:text-gray-200"
								on:click={async () => {
									await showControls.set(!$showControls);
								}}
								aria-label="Controls"
							>
								<Knobs className="size-5" strokeWidth="1" />
							</button>
						</Tooltip>
					{/if}
				</div>
			</div>
		</div>
	</div>

	{#if $temporaryChatEnabled && isTemporaryChatId($chatId)}
		<div class=" w-full z-30 text-center">
			<div class="text-xs text-gray-500">{$i18n.t('Temporary Chat')}</div>
		</div>
	{/if}

	<div class="absolute top-[100%] left-0 right-0 h-fit">
		{#if !history.currentId && !$chatId && ($banners.length > 0 || ($config?.license_metadata?.type ?? null) === 'trial' || (($config?.license_metadata?.seats ?? null) !== null && $config?.user_count > $config?.license_metadata?.seats))}
			<div class=" w-full z-30">
				<div
					class=" flex flex-col gap-1 w-full max-h-28 overflow-y-auto overscroll-contain md:max-h-none md:overflow-visible"
				>
					{#if ($config?.license_metadata?.type ?? null) === 'trial'}
						<Banner
							banner={{
								type: 'info',
								title: 'Trial License',
								content: $i18n.t(
									'You are currently using a trial license. Please contact support to upgrade your license.'
								)
							}}
						/>
					{/if}

					{#if ($config?.license_metadata?.seats ?? null) !== null && $config?.user_count > $config?.license_metadata?.seats}
						<Banner
							banner={{
								type: 'error',
								title: 'License Error',
								content: $i18n.t(
									'Exceeded the number of seats in your license. Please contact support to increase the number of seats.'
								)
							}}
						/>
					{/if}

					{#each $banners.filter((b) => ![...getDismissedBannerIds(), ...closedBannerIds].includes(b.id)) as banner (banner.id)}
						<Banner
							{banner}
							on:dismiss={(e) => {
								const bannerId = e.detail;

								if (banner.dismissible) {
									localStorage.setItem(
										'dismissedBannerIds',
										JSON.stringify(
											[bannerId, ...getDismissedBannerIds()].filter((id) =>
												$banners.find((b) => b.id === id)
											)
										)
									);
								} else {
									closedBannerIds = [...closedBannerIds, bannerId];
								}
							}}
						/>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</nav>
