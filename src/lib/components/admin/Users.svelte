<script>
	import { getContext, onMount } from 'svelte';

	import { goto } from '$app/navigation';
	import { adminGroupCount, adminUserCount, config, user } from '$lib/stores';
	import { page } from '$app/stores';
	import { getGroups } from '$lib/apis/groups';
	import { getUsers } from '$lib/apis/users';
	import { formatNumber } from '$lib/utils';

	import UserList from './Users/UserList.svelte';
	import Groups from './Users/Groups.svelte';
	import Projects from './Users/Projects.svelte';

	const i18n = getContext('i18n');

	let selectedTab;
	$: {
		const pathParts = $page.url.pathname.split('/');
		const tabFromPath = pathParts[pathParts.length - 1];
		selectedTab = ['overview', 'groups', 'projects'].includes(tabFromPath) ? tabFromPath : 'overview';
	}

	$: if (selectedTab) {
		// scroll to selectedTab
		scrollToTab(selectedTab);
	}

	$: if (loaded && selectedTab) {
		loadCounts();
	}

	const scrollToTab = (tabId) => {
		const tabElement = document.getElementById(tabId);
		if (tabElement) {
			tabElement.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
		}
	};

	let loaded = false;
	$: usersSeatLimit = $config?.license_metadata?.seats ?? null;
	$: usersCountExceeded = usersSeatLimit !== null && ($adminUserCount ?? 0) > usersSeatLimit;
	$: formattedUserCount =
		$adminUserCount === null
			? null
			: usersSeatLimit !== null
				? `${formatNumber($adminUserCount)} of ${formatNumber(usersSeatLimit)}`
				: formatNumber($adminUserCount);
	$: formattedGroupCount = $adminGroupCount === null ? null : formatNumber($adminGroupCount);

	const loadCounts = async () => {
		const [usersRes, groupsRes] = await Promise.all([
			getUsers(localStorage.token, undefined, 'created_at', 'asc', 1).catch(() => null),
			getGroups(localStorage.token).catch(() => null)
		]);

		adminUserCount.set(usersRes?.total ?? null);
		adminGroupCount.set(Array.isArray(groupsRes) ? groupsRes.length : null);
	};

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
		}

		loaded = true;

		const containerElement = document.getElementById('users-tabs-container');

		if (containerElement) {
			containerElement.addEventListener('wheel', function (event) {
				if (event.deltaY !== 0) {
					// Adjust horizontal scroll position based on vertical scroll
					containerElement.scrollLeft += event.deltaY;
				}
			});
		}

		// Scroll to the selected tab on mount
		scrollToTab(selectedTab);
	});
</script>

{#if loaded}
	<div class="flex flex-col lg:flex-row w-full h-full pb-2">
		<div
			id="users-tabs-container"
			class="tabs mx-2 px-2 sm:mx-2.5 lg:mx-0 lg:px-2.5 flex flex-row overflow-x-auto gap-2.5 max-w-full lg:gap-0 lg:flex-col lg:flex-none lg:w-50 dark:text-gray-200 text-sm font-normal text-left scrollbar-none"
		>
			<a
				id="overview"
				href="/admin/users/overview"
				draggable="false"
				class="px-0.5 py-1 min-w-fit rounded-lg lg:flex-none flex items-center gap-1.5 text-right transition select-none {selectedTab ===
				'overview'
					? ''
					: ' text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'}"
			>
				<div class=" self-center">{$i18n.t('Overview')}</div>
				{#if formattedUserCount !== null}
					<div
						class="self-center text-sm {usersCountExceeded
							? `text-red-500 ${selectedTab === 'overview' ? '' : 'opacity-50'}`
							: 'opacity-60'}"
					>
						{formattedUserCount}
					</div>
				{/if}
			</a>

		<a
			id="groups"
			href="/admin/users/groups"
			draggable="false"
			class="px-0.5 py-1 min-w-fit rounded-lg lg:flex-none flex text-right transition select-none {selectedTab ===
			'groups'
				? ''
				: ' text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'}"
		>
			<div class=" self-center mr-2">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 16 16"
					fill="currentColor"
					class="size-4"
				>
					<path
						d="M8 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5ZM3.156 11.763c.16-.629.44-1.21.813-1.72a2.5 2.5 0 0 0-2.725 1.377c-.136.287.102.58.418.58h1.449c.01-.077.025-.156.045-.237ZM12.847 11.763c.02.08.036.16.046.237h1.446c.316 0 .554-.293.417-.579a2.5 2.5 0 0 0-2.722-1.378c.374.51.653 1.09.813 1.72ZM14 7.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0ZM3.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM5 13c-.552 0-1.013-.455-.876-.99a4.002 4.002 0 0 1 7.753 0c.136.535-.324.99-.877.99H5Z"
					/>
				</svg>
			</div>
			<div class=" self-center">{$i18n.t('Groups')}</div>
		</a>
		
		<a
			id="projects"
			href="/admin/users/projects"
			draggable="false"
			class="px-0.5 py-1 min-w-fit rounded-lg lg:flex-none flex text-right transition select-none {selectedTab ===
			'projects'
				? ''
				: ' text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'}"
		>
			<div class=" self-center mr-2">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 16 16"
					fill="currentColor"
					class="size-4"
				>
					<path
						d="M2 2a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V2zm2 1a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm3 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm3 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2zM3 7a1 1 0 0 0 0 2h10a1 1 0 0 0 0-2H3z"
					/>
				</svg>
			</div>
			<div class=" self-center">{$i18n.t('Projects')}</div>
		</a>
	</div>

		<div class="flex-1 px-3.5 lg:pr-[1rem] lg:pl-0 overflow-y-scroll">
			{#if selectedTab === 'overview'}
				<UserList />
			{:else if selectedTab === 'groups'}
				<Groups />
			{:else if selectedTab === 'projects'}
			<Projects />
		{/if}
		</div>
	</div>
{/if}
