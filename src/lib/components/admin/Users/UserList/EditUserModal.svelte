<script lang="ts">
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import { createEventDispatcher } from 'svelte';
	import { onMount, getContext } from 'svelte';

	import { goto } from '$app/navigation';

	import { updateUserById, getUserGroupsById } from '$lib/apis/users';
	import { updateUserBudget } from '$lib/apis/litellm';

	import Modal from '$lib/components/common/Modal.svelte';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	import XMark from '$lib/components/icons/XMark.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import UserProfileImage from '$lib/components/chat/Settings/Account/UserProfileImage.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();
	dayjs.extend(localizedFormat);

	export let show = false;
	export let selectedUser: any;
	export let sessionUser: any;
	export let userBudgets: Record<string, any> = {};
	export let defaultBudget = 0;

	$: if (show) {
		init();
	}

	const getInitialBudgetData = () => {
		if (!selectedUser) return null;
		return userBudgets[selectedUser.id] ?? userBudgets[selectedUser.email] ?? null;
	};

	let budgetMode: 'default' | 'custom' = 'default';
	let customBudget: number | null = null;

	const init = () => {
		if (selectedUser) {
			const existingBudgetData = getInitialBudgetData();
			const currentBudget =
				existingBudgetData?.maxBudget ??
				selectedUser?.info?.max_budget ??
				selectedUser?.max_budget ??
				null;
			customBudget = currentBudget;
			budgetMode = selectedUser.has_default_budget ? 'default' : 'custom';

			_user = {
				...selectedUser,
				password: '',
				budget: currentBudget ?? defaultBudget
			};
			loadUserGroups();
		}
	};

	let _user = {
		profile_image_url: '',
		role: 'pending',
		name: '',
		email: '',
		password: '',
		budget: null as number | null,
		has_default_budget: false
	};

	let userGroups: any[] | null = null;

	$: _user.budget = budgetMode === 'default' ? defaultBudget : customBudget;
	$: _user.has_default_budget = budgetMode === 'default';
	$: budgetStats = calculateLiveBudget(selectedUser, userBudgets, _user.budget);

	function calculateLiveBudget(
		userItem: any,
		budgetsMap: Record<string, any>,
		newMaxBudget: number | null
	) {
		// 1. Bereits verarbeitete Daten aus der Map holen
		const existingData = userItem?.id
			? (budgetsMap[userItem.id] ?? budgetsMap[userItem.email])
			: null;

		const spend = existingData?.spend ?? userItem?.info?.spend ?? userItem?.spend ?? 0;

		// 2. Max Budget bestimmen (Neuer Input hat Vorrang für Live-Vorschau)
		const maxBudget =
			newMaxBudget !== null && !isNaN(Number(newMaxBudget))
				? Number(newMaxBudget)
				: (existingData?.maxBudget ?? userItem?.info?.max_budget ?? userItem?.max_budget ?? 0);

		// 3. Verbrauch in %
		const rawSpentPercent = maxBudget > 0 ? (spend / maxBudget) * 100 : 0;
		const spentPercent = Math.min(Math.round(rawSpentPercent), 100);

		// 4. Zeitfortschritt (bereits aus formatUserBudget in der Oberkomponente vorhanden)
		// Falls zeitliche Daten in existingData vorhanden sind, nutzen wir sie, sonst den Prozentwert
		const timePercent = existingData?.timePercent ?? null;

		let barColorClass = 'bg-emerald-500';

		if (timePercent !== null) {
			// Dasselbe 'diff' wie in deiner Oberkomponente
			const diff = spentPercent - timePercent;
			barColorClass = diff > 15 ? 'bg-red-500' : diff > 5 ? 'bg-amber-500' : 'bg-emerald-500';
		} else {
			// Fallback, falls timePercent nicht existiert
			barColorClass =
				rawSpentPercent >= 100
					? 'bg-red-500'
					: rawSpentPercent >= 80
						? 'bg-amber-500'
						: 'bg-emerald-500';
		}

		const decimals = maxBudget > 0 && maxBudget < 0.01 ? 4 : 2;
		const formattedSpend = spend.toLocaleString('de-DE', {
			minimumFractionDigits: decimals,
			maximumFractionDigits: decimals
		});
		const formattedMaxBudget = maxBudget.toLocaleString('de-DE', {
			minimumFractionDigits: decimals,
			maximumFractionDigits: decimals
		});

		return {
			spend,
			maxBudget,
			spentPercent,
			barColorClass,
			formattedSpend,
			formattedMaxBudget
		};
	}

	const submitHandler = async () => {
		try {
			const res = await updateUserById(localStorage.token, selectedUser.id, _user);

			if (_user.budget !== null && _user.budget !== undefined) {
				await updateUserBudget(localStorage.token, Number(_user.budget), selectedUser);
			}

			if (res) {
				dispatch('save');
				show = false;
			}
		} catch (error) {
			toast.error(`${error}`);
		}
	};

	const loadUserGroups = async () => {
		if (!selectedUser?.id) return;
		userGroups = null;

		userGroups = await getUserGroupsById(localStorage.token, selectedUser.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
	};
</script>

<Modal size="md" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-4 pt-3 pb-1">
			<div class=" text-sm font-medium self-center">{$i18n.t('Edit User')}</div>
			<button
				class="self-center rounded-lg p-1 text-gray-500 transition hover:bg-gray-50 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
				aria-label={$i18n.t('Close')}
				on:click={() => {
					show = false;
				}}
			>
				<XMark className={'size-4'} />
			</button>
		</div>

		<div class="flex flex-col md:flex-row w-full md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={() => {
						submitHandler();
					}}
				>
					<div class=" px-5 pt-3 pb-5 w-full">
						<div class="flex self-center w-full">
							<div class=" self-start h-full mr-6">
								<UserProfileImage
									imageClassName="size-14"
									bind:profileImageUrl={_user.profile_image_url}
									user={_user}
								/>
							</div>

							<div class=" flex-1 min-w-0">
								<div class="overflow-hidden w-ful mb-2">
									<div class=" self-center capitalize font-normal truncate">
										{selectedUser?.name}
									</div>

									<div class="text-xs text-gray-500">
										{$i18n.t('Created at')}
										{dayjs(selectedUser?.created_at * 1000).format('LL')}
									</div>
								</div>

								<div class=" flex flex-col space-y-1.5">
									{#if (userGroups ?? []).length > 0}
										<div class="flex flex-col w-full text-sm">
											<div class="mb-1 text-xs text-gray-500">{$i18n.t('User Groups')}</div>

											<div class="flex flex-wrap gap-1 my-0.5 -mx-1">
												{#each userGroups as userGroup}
													<span
														class="px-1.5 py-0.5 rounded-xl bg-gray-100 dark:bg-gray-850 text-xs"
													>
														<a
															href={'/admin/users/groups?id=' + userGroup.id}
															on:click|preventDefault={() =>
																goto('/admin/users/groups?id=' + userGroup.id)}
														>
															{userGroup.name}
														</a>
													</span>
												{/each}
											</div>
										</div>
									{/if}

									<div class="flex flex-col w-full">
										<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Role')}</div>

										<div class="flex-1">
											<select
												class="w-full text-sm bg-transparent disabled:text-gray-500 dark:disabled:text-gray-500 outline-hidden"
												bind:value={_user.role}
												aria-label={$i18n.t('Role')}
												disabled={_user.id == sessionUser?.id}
												required
											>
												<option value="admin">{$i18n.t('Admin')}</option>
												<option value="user">{$i18n.t('User')}</option>
												<option value="pending">{$i18n.t('Pending')}</option>
											</select>
										</div>
									</div>

									<div class="flex flex-col w-full">
										<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Name')}</div>

										<div class="flex-1">
											<input
												class="w-full text-sm bg-transparent outline-hidden"
												type="text"
												bind:value={_user.name}
												aria-label={$i18n.t('Name')}
												placeholder={$i18n.t('Enter Your Name')}
												autocomplete="off"
												required
											/>
										</div>
									</div>

									<div class="flex flex-col w-full">
										<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Email')}</div>

										<div class="flex-1">
											<input
												class="w-full text-sm bg-transparent disabled:text-gray-500 dark:disabled:text-gray-500 outline-hidden"
												type="email"
												bind:value={_user.email}
												aria-label={$i18n.t('Email')}
												placeholder={$i18n.t('Enter Your Email')}
												autocomplete="off"
												required
											/>
										</div>
									</div>

									{#if _user?.oauth}
										<div class="flex flex-col w-full">
											<div class=" mb-1 text-xs text-gray-500">{$i18n.t('OAuth ID')}</div>

											<div class="flex-1 text-sm break-all mb-1 flex flex-col space-y-1">
												{#each Object.keys(_user.oauth) as key}
													<div>
														<span class="text-gray-500">{key}</span>
														<span class="">{_user.oauth[key]?.sub}</span>
													</div>
												{/each}
											</div>
										</div>
									{/if}

									<div class="flex flex-col w-full">
										<div class=" mb-1 text-xs text-gray-500">{$i18n.t('New Password')}</div>

										<div class="flex-1">
											<SensitiveInput
												class="w-full text-sm bg-transparent outline-hidden"
												type="password"
												aria-label={$i18n.t('New Password')}
												placeholder={$i18n.t('Enter New Password')}
												bind:value={_user.password}
												autocomplete="new-password"
												required={false}
											/>
										</div>
									</div>

									<!-- Abgetrennter Budget-Bereich mit Live-Vorschau -->
									<div class="pt-3 mt-2 border-t border-gray-100 dark:border-gray-800">
										<div
											class="p-3 rounded-lg bg-gray-50/50 dark:bg-gray-850/50 border border-gray-100 dark:border-gray-800/60 space-y-2"
										>
											<div class="flex justify-between items-center text-xs">
												<span class="font-medium text-gray-500 dark:text-gray-400">
													{$i18n.t('User Budget')}
												</span>
												<span class="font-mono text-gray-600 dark:text-gray-300">
													${budgetStats.formattedSpend} /${budgetStats.formattedMaxBudget}
												</span>
											</div>

											<!-- Fortschrittsbalken mit dynamischer Ampelfarbe -->
											<div
												class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
											>
												<div
													class="h-full transition-all duration-300 rounded-full {budgetStats.barColorClass}"
													style="width: {budgetStats.spentPercent}%"
												></div>
											</div>

											<div class="flex items-center justify-between gap-3 pt-1">
												<label class="text-xs text-gray-400" for="user-budget-mode">
													{$i18n.t('Budget type')}
												</label>
												<select
													id="user-budget-mode"
													class="max-w-40 text-right text-sm bg-transparent outline-hidden"
													bind:value={budgetMode}
												>
													<option value="default">{$i18n.t('Default')} (${defaultBudget})</option>
													<option value="custom">{$i18n.t('Custom')}</option>
												</select>
											</div>
											{#if budgetMode === 'custom'}
												<div class="flex items-center justify-between pt-1">
													<label class="text-xs text-gray-400" for="user-custom-budget">
														{$i18n.t('Max Budget')} ($)
													</label>
													<input
														id="user-custom-budget"
														class="w-32 text-right text-sm bg-transparent font-mono outline-hidden border-b border-gray-200 dark:border-gray-700 focus:border-black dark:focus:border-white transition"
														type="number"
														step="0.01"
														min="0"
														required
														bind:value={customBudget}
														aria-label={$i18n.t('Budget')}
														placeholder={$i18n.t('Enter budget')}
													/>
												</div>
											{:else}
												<div class="flex items-center justify-between pt-1 text-xs text-gray-400">
													<span>{$i18n.t('Max Budget')} ($)</span>
													<span class="font-mono">{defaultBudget.toLocaleString('de-DE')}</span>
												</div>
											{/if}
										</div>
									</div>
								</div>
							</div>
						</div>

						<div class="flex justify-end pt-4 text-sm font-normal">
							<button
								class="px-3.5 py-1.5 text-sm font-normal bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full flex flex-row space-x-1 items-center"
								type="submit"
							>
								{$i18n.t('Save')}
							</button>
						</div>
					</div>
				</form>
			</div>
		</div>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}

	.tabs::-webkit-scrollbar {
		display: none;
	}

	.tabs {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}

	input[type='number'] {
		-moz-appearance: textfield;
	}
</style>
