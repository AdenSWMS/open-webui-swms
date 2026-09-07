<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 my-6 animate-pulse">
	<div class="lg:col-span-2 border border-gray-200 dark:border-gray-800 rounded-xl p-5 bg-white dark:bg-gray-900">
		<div class="h-4 w-48 bg-gray-200 dark:bg-gray-700 rounded mb-6"></div>
		<div class="h-56 flex items-end justify-between gap-4 pt-8">
			{#each [1, 2, 3, 4, 5] as _}
				<div class="w-full bg-gray-100 dark:bg-gray-800 rounded-t h-full flex items-end">
					<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-t" style="height: {Math.floor(Math.random() * 60 + 20)}%;"></div>
				</div>
			{/each}
		</div>
	</div>

	<!-- Donut Chart Skeleton -->	<div class="border border-gray-200 dark:border-gray-800 rounded-xl p-5 bg-white dark:bg-gray-900 flex flex-col items-center justify-between">
		<div class="h-4 w-36 bg-gray-200 dark:bg-gray-700 rounded w-full mb-4"></div>
		<div class="w-36 h-36 rounded-full border-8 border-gray-200 dark:border-gray-800 my-2"></div>
		<div class="w-full space-y-2 mt-4">
			<div class="h-3 bg-gray-200 dark:bg-gray-800 rounded w-full"></div>
			<div class="h-3 bg-gray-200 dark:bg-gray-800 rounded w-3/4"></div>
		</div>
	</div>
</div>