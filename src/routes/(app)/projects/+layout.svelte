<script lang="ts">
	import { showSidebar } from '$lib/stores';
</script>

<div
	class="flex flex-col flex-1 min-w-0 w-full h-screen max-h-[100dvh] transition-[max-width] duration-200 ease-in-out {$showSidebar
		? 'md:max-w-[calc(100%-var(--sidebar-width))]'
		: 'md:max-w-[calc(100%-42px)]'} max-w-full"
>
	<div class="flex-1 min-w-0 max-h-full overflow-y-auto">
		<slot />
	</div>
</div>
