<script>
	import { onMount } from 'svelte';
	import { getModels } from '$lib/apis';

	export let value = ''; 
	export let inputClass = '';
	export let i18n;

	let models = [];
	let searchInput = '';
	let isOpen = false;

	// Holt die Modelle einmalig beim Laden
	onMount(async () => {
		try {
			const res = await getModels(localStorage.token);
			models = res || [];
			syncSearchInput();
		} catch (err) {
			console.error('Fehler beim Laden der Modelle:', err);
		}
	});

	// Synchronisiert das Eingabefeld, sobald sich 'value' oder 'models' von AUSSEN ändern
	$: if (models.length > 0 && value !== undefined) {
		syncSearchInput();
	}

	function syncSearchInput() {
		// Verhindert Überschreiben, während der User aktiv in das Suchfeld tippt
		if (isOpen) return;

		const activeModel = models.find((m) => m.id === value);
		if (activeModel) {
			searchInput = activeModel.name || activeModel.id;
		} else if (value) {
			searchInput = value;
		} else {
			searchInput = '';
		}
	}

	// Filtert Modelle: Wenn das Feld fokussiert wird und dem gewählten Modell entspricht, 
	// zeige alle Modelle an. Ansonsten filtere nach der Freitext-Eingabe.
	$: filteredModels = models.filter((m) => {
		if (!searchInput) return true;
		
		const currentModel = models.find((m) => m.id === value);
		const currentName = currentModel ? (currentModel.name || currentModel.id) : value;

		// Wenn das Suchfeld genau dem aktuell ausgewählten Namen entspricht, alle anzeigen
		if (searchInput === currentName) {
			return true;
		}

		return (m.name || m.id).toLowerCase().includes(searchInput.toLowerCase());
	});

	function selectModel(model) {
		value = model.id;
		searchInput = model.name || model.id;
		isOpen = false;
	}

	function handleBlur() {
		setTimeout(() => {
			isOpen = false;

			const validModel = models.find(
				(m) =>
					m.id === value ||
					(m.name && m.name.toLowerCase() === searchInput.toLowerCase())
			);

			if (validModel) {
				value = validModel.id;
				searchInput = validModel.name || validModel.id;
			} else {
				// Wenn kein valides Modell getippt wurde, behalte manuell eingegebenen Text als Wert
				value = searchInput;
			}
		}, 200);
	}
</script>

<div class="relative w-full">
	<input
		type="text"
		class={inputClass}
		bind:value={searchInput}
		on:focus={() => (isOpen = true)}
		on:blur={handleBlur}
		placeholder={$i18n.t('Select a model')}
	/>

	{#if isOpen && filteredModels.length > 0}
		<ul
			class="absolute z-50 left-0 right-0 mt-1 max-h-60 overflow-y-auto bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg"
		>
			{#each filteredModels as model}
				<li
					class="px-3 py-2 text-sm cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 dark:text-white"
					on:mousedown={() => selectModel(model)}
				>
					{model.name || model.id}
				</li>
			{/each}
		</ul>
	{/if}
</div>