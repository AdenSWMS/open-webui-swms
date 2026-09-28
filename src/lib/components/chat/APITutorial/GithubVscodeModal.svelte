<script lang="ts">
	import Modal from '$lib/components/common/Modal.svelte';

	export let show = false;

	// Hier kannst du deine Erklärungs-Abschnitte definieren
	const steps = [
		{
			title: '1. Einstellungen in VS Code öffnen',
			description:
				'Öffne VS Code und drücke `Ctrl + ,` (Windows/Linux) oder `Cmd + ,` (macOS), um die Einstellungen zu öffnen. Alternativ kannst du unten links auf das Zahnrad-Symbol klicken.'
		},
		{
			title: '2. Nach OpenCode / API-Key suchen',
			description:
				'Gib oben in der Suchleiste der Einstellungen `OpenCode API Key` oder `opencode.apiKey` ein, um das passende Eingabefeld direkt zu finden.'
		},
		{
			title: '3. API-Key einfügen & speichern',
			description:
				'Füge deinen kopierten API-Key in das entsprechende Textfeld ein. Die Einstellung wird automatisch gespeichert und ist sofort einsatzbereit.'
		}
	];
</script>

<Modal bind:show size="2xl">
	<div class="px-5 py-4">
		<!-- Header / Schließen-Button -->
		<div class="flex justify-between items-center pb-3">
			<div class="text-lg font-medium text-gray-900 dark:text-gray-100">
				API-Key in VS Code einrichten
			</div>
			<button
				class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition"
				on:click={() => (show = false)}
				aria-label="Schließen"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<path
						d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"
					/>
				</svg>
			</button>
		</div>

		<!-- Video Einbindung -->
		<div
			class="mb-6 overflow-hidden rounded-xl bg-black aspect-video flex items-center justify-center shadow-inner"
		>
			<video src="./../../assets/opencode.mp4" autoplay loop muted playsinline class="w-full h-full object-cover">
				<track kind="captions" />
				Dein Browser unterstützt dieses Video-Format leider nicht.
			</video>
		</div>

		<!-- Erklärungs-Textfelder -->
		<div class="space-y-4">
			{#each steps as step}
				<div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-800">
					<h3 class="font-medium text-sm text-gray-900 dark:text-gray-100 mb-1">
						{step.title}
					</h3>
					<p class="text-xs leading-relaxed text-gray-600 dark:text-gray-400">
						{step.description}
					</p>
				</div>
			{/each}
		</div>
	</div>
</Modal>