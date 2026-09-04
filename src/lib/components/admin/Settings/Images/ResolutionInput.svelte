<script>
	import { createEventDispatcher } from 'svelte';

	export let value = []; // jetzt ein Array statt String
	export let inputClass = '';
	export let i18n;

	const dispatch = createEventDispatcher();

	let currentInput = '';
	let errorMessage = '';

	// Hilfsfunktion: Wandelt jeden Input (String oder Array) sauber in ein Array aus Strings um
	function toArray(val) {
		if (Array.isArray(val)) return val;
		if (typeof val === 'string' && val.trim() !== '') {
			return val
				.split(',')
				.map((s) => s.trim())
				.filter(Boolean);
		}
		return [];
	}

	// Reaktives Array für das Rendering
	$: sizes = toArray(value);

	const sizeRegex = /^\d+x\d+$/;

	function addSize() {
		const formattedInput = currentInput.trim().toLowerCase();
		if (!formattedInput) return;

		if (!sizeRegex.test(formattedInput)) {
			errorMessage = $i18n ? $i18n.t('Invalid format! Use e.g. 512x512') : 'Invalid format!';
			return;
		}

		if (!sizes.includes(formattedInput)) {
			value = [...sizes, formattedInput]; // bleibt ein Array
			dispatch('change', value);
		}

		currentInput = '';
		errorMessage = '';
	}

	function removeSize(index) {
		value = sizes.filter((_, i) => i !== index); // bleibt ein Array
		dispatch('change', value);
	}

	function handleKeyDown(event) {
		if (event.key === 'Enter') {
			event.preventDefault();
			event.stopPropagation();
			addSize();
		} else if (event.key === 'Backspace' && currentInput === '' && sizes.length > 0) {
			removeSize(sizes.length - 1);
		}
	}
</script>

<div class="flex flex-col gap-1 w-full">
	<div
		class={`${inputClass} flex flex-wrap items-center gap-1.5 p-1.5 cursor-text h-auto min-h-[38px]`}
		on:click={() => document.getElementById('image-size-input')?.focus()}
		on:keydown={() => {}}
	>
		{#each sizes as size, index (size + index)}
			<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-primary-500/20 text-primary-600 dark:bg-gray-800 dark:text-gray-200">
				<button
					type="button"
					class="hover:text-red-500 focus:outline-none cursor-pointer"
					on:click|preventDefault|stopPropagation={() => removeSize(index)}
				>
					&times;
				</button>
				{size}
			</span>
		{/each}
		<input
			id="image-size-input"
			type="text"
			class="flex-1 bg-transparent border-none outline-none focus:ring-0 p-0 text-xs min-w-[120px]"
			placeholder={sizes.length === 0 ? ($i18n ? $i18n.t('Enter Image Size (e.g. 512x512)') : 'Enter Image Size (e.g. 512x512)') : ''}
			bind:value={currentInput}
			on:keydown={handleKeyDown}
		/>
	</div>
	{#if errorMessage}
		<span class="text-xs text-red-500 mt-0.5">{errorMessage}</span>
	{/if}
</div>