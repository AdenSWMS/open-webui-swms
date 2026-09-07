<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-pulse">
	{#each [1, 2] as _}
		<div class="border border-gray-200 dark:border-gray-800 rounded-xl p-4">
			<div class="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
			<div class="space-y-3">
				{#each [1, 2, 3] as __}
					<div class="flex justify-between items-center py-2">
						<div class="h-3 w-20 bg-gray-200 dark:bg-gray-800 rounded"></div>
						<div class="h-3 w-16 bg-gray-200 dark:bg-gray-800 rounded"></div>
						<div class="h-3 w-12 bg-gray-200 dark:bg-gray-800 rounded"></div>
					</div>
				{/each}
			</div>
		</div>
	{/each}
</div>