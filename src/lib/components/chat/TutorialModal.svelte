<script lang="ts">
	import Modal from '$lib/components/common/Modal.svelte';
	import { generateLiteLLMApiKey, deleteLiteLLMApiKey } from '$lib/apis/litellm';
	import { createEventDispatcher } from 'svelte';
    import OpenCodeModal from './APITutorial/OpenCodeModal.svelte';
    import CopilotVsCodeModal from './APITutorial/GithubVscodeModal.svelte';

	export let show = false;

	const dispatch = createEventDispatcher();

	interface Provider {
		id: string;
		title: string;
		description: string;
		image: string;
		disabled?: boolean;
	}

	const providers: Provider[] = [
		{
			id: 'opencode',
			title: 'OpenCode',
			description: 'Open-Source-Agent für Terminal, IDE und Desktop.',
			image: '/assets/tutorial/opencode_logo.png',
			disabled: false
		},
		{
			id: 'Github Copilot - VSCode',
			title: 'Github Copilot - VSCode',
			description: 'Der Github Copilot in VsCode mit den Modellen von SWMS.',
			image: '/assets/tutorial/github_vscode.png',
			disabled: false
		},
		{
			id: 'Github Copilot - Visual Studio',
			title: 'Github Copilot - Visual Studio',
			description: 'Der Github Copilot in Visual Studio mit den Modellen von SWMS.',
			image: '/assets/tutorial/github_visualstudio.png',
			disabled: true
		}
	];

	// API-Key States
	let apiKey: string | null = null;
	let isLoading = false;
	let keyError: string | null = null;
	let copied = false;
	let showConfirmModal = false;

	async function handleGenerateKey() {
		isLoading = true;
		keyError = null;
		try {
			const res = await generateLiteLLMApiKey(localStorage.token);
			apiKey = res.key;
		} catch (err) {
			keyError = `Fehler beim Generieren des API-Keys: ${err}`;
		} finally {
			isLoading = false;
		}
	}

	async function confirmAndReGenerateKey() {
		showConfirmModal = false;
		await deleteLiteLLMApiKey(localStorage.token);
		await handleGenerateKey();
	}

	async function copyKey() {
		if (!apiKey) return;
		await navigator.clipboard.writeText(apiKey);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}

	let showOpenCode = false;
	let showCopilotVsCode = false;

	function openProviderModal(providerId: string) {
        console.log('Provider ID:', providerId); // Debug-Ausgabe
		if (providerId === 'opencode') {
            showCopilotVsCode = false;
			showOpenCode = true;
		} else if (providerId === 'Github Copilot - VSCode') {
			showOpenCode = false;
            showCopilotVsCode = true;
		}
	}

	// Reset beim Schließen
	$: if (!show) {
		apiKey = null;
		keyError = null;
		copied = false;
		showConfirmModal = false;
	}
</script>

<Modal bind:show size="2xl">
	<div class="px-5 py-4">
		<!-- Header -->
		<div class="flex justify-between items-center pb-4 mb-2">
			<div class="text-lg font-semibold dark:text-gray-100">Tutorials zur Nutzung des API Keys</div>
			<button
				class="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition"
				on:click={() => (show = false)}
				aria-label="Schließen"
			>
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5 text-gray-500">
					<path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
				</svg>
			</button>
		</div>

      <!-- Info-Box: Erklärung & Anleitung zum API-Key -->
        <div class="mb-6 p-4 rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50/60 dark:bg-gray-850/60 text-sm text-gray-600 dark:text-gray-300 space-y-3">
            <!-- Haupt-Erklärung -->
            <div class="flex gap-3 items-start">
                <div class="p-2 rounded-lg bg-gray-200/60 dark:bg-gray-800 text-gray-700 dark:text-gray-200 shrink-0 mt-0.5">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-7-4a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM9 9a.75.75 0 0 0 0 1.5h.25v3h-.25a.75.75 0 0 0 0 1.5h1.5a.75.75 0 0 0 0-1.5H10.5V10A.75.75 0 0 0 9.75 9H9Z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="space-y-1.5 leading-relaxed">
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100 text-sm">
                        Was ist der API-Key und wofür wird er benötigt?
                    </h4>
                    <p>
                                            Der API-Key ist dein "persönlicher digitaler Schlüssel". Er ermöglicht es dir, unsere KI-Modelle auch außerhalb dieser Web-Oberfläche in externen Plattformen, IDEs oder Tools zu nutzen. Da der Schlüssel OpenAI-kompatibel ist, lässt sich der Key in nahezu allen modernen Entwickler-Tools und KI-Erweiterungen einbinden. Beachte jedoch, dass die gesicherte Projektstruktur von dieser Seite in diesen externen Tools nicht gegeben ist und der Nutzer selbst für die korrekte Nutzung verantwortlich ist.
                    </p>
                    <p class="text-gray-500 dark:text-gray-400">
                        <strong>Abrechnung & Budgets:</strong> Alle Anfragen, die du über deinen API-Key in externen Programmen stellst, werden ganz normal deinem Benutzerkonto zugerechnet und über dein gewohntes Budget-Limit erfasst.
                    </p>
                </div>
            </div>

            <hr class="border-gray-200 dark:border-gray-800/80 my-2" />

            <!-- Ablauf & Anleitung -->
            <div class="grid grid-cols-2 md:grid-cols-1 gap-3 pt-1">
                <div class="flex items-start gap-2">
                    <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-800 font-mono text-[10px] font-bold text-gray-700 dark:text-gray-300">1</span>
                    <p class="leading-tight">
                        <strong class="text-gray-800 dark:text-gray-200">Key generieren:</strong> 
                        Erzeuge deinen Key direkt im Bereich darunter. Er wird aus Sicherheitsgründen <strong>nur einmalig angezeigt</strong>.
                    </p>
                </div>
                <div class="flex items-start gap-2">
                    <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-800 font-mono text-[10px] font-bold text-gray-700 dark:text-gray-300">2</span>
                    <p class="leading-tight">
                        <strong class="text-gray-800 dark:text-gray-200">In Anleitungen nutzen:</strong> 
                        Kopiere den Key und wähle dein gewünschtes Tutorial unten aus oder rufe dein externes Tool auf und füge den Key dort ein. Beachte die jeweiligen Anleitungen der Tools, in manchen Tutorials lässt sich der Key auch direkt in Befehle einsätzen.
                    </p>
                </div>
            </div>
        </div> 

        <hr class="my-4 border-gray-100 dark:border-gray-800" />

		<h2 class="font-semibold mb-1 dark:text-gray-100">API-Key generieren</h2>
		<div class="text-gray-500 text-xs mt-1 mb-2 text-left">
			ⓘ Der generierte API-Key ist für ein Jahr gültig, danach muss er neu generiert werden.
		</div>

		<div class="mt-3 mb-3">
			<button
				class="w-full px-3.5 py-2 text-xs font-medium rounded-xl border border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-300 dark:hover:bg-amber-900/40 transition disabled:opacity-50 flex items-center justify-center gap-1.5"
				on:click={() => (showConfirmModal = true)}
				disabled={isLoading}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 16 16"
					fill="currentColor"
					class="w-3.5 h-3.5"
				>
					<path
						fill-rule="evenodd"
						d="M13.836 2.477a.75.75 0 0 1 .75.75v3.182a.75.75 0 0 1-.75.75h-3.182a.75.75 0 0 1 0-1.5h1.37l-.84-.841a4.5 4.5 0 0 0-7.08.932.75.75 0 0 1-1.3-.75 6 6 0 0 1 9.44-1.242l.842.84V3.227a.75.75 0 0 1 .75-.75Zm-8.672 7.84a4.5 4.5 0 0 0 7.08-.931.75.75 0 0 1 1.3.75 6 6 0 0 1-9.44 1.241l-.842-.84v1.242a.75.75 0 0 1-1.5 0V8.396a.75.75 0 0 1 .75-.75h3.182a.75.75 0 0 1 0 1.5h-1.37l.84.841Z"
						clip-rule="evenodd"
					/>
				</svg>
				API-Key generieren
			</button>
		</div>

		{#if keyError}
			<div class="text-red-500 text-xs mt-2">{keyError}</div>
		{/if}

		{#if apiKey}
			<div class="flex items-center gap-2 mt-3 px-3 py-2 rounded-xl bg-gray-50 dark:bg-gray-850">
				<code class="flex-1 text-xs overflow-x-auto whitespace-nowrap dark:text-gray-100">
					{apiKey}
				</code>
				<button
					class="text-xs px-2.5 py-1 rounded-lg bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-100 transition"
					on:click={copyKey}
				>
					{copied ? '✓ Kopiert' : 'Kopieren'}
				</button>
			</div>
		{/if}

        <h2 class="font-semibold mb-1 mt-10 dark:text-gray-100">Tutorials & Anleitungen</h2>

		<!-- 3-Spalten Grid -->
		<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 my-2">
			{#each providers as provider}
				<button
					disabled={provider.disabled}
					class="group relative text-left border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-850 rounded-xl p-2.5 transition-all duration-300 flex flex-col justify-between {provider.disabled ? 'opacity-60 grayscale cursor-not-allowed' : 'hover:scale-[1.03]'}"
					on:click={() => openProviderModal(provider.id)}
				>
					<div>
						<div class="relative aspect-video w-full rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800 mb-2">
							<img src={provider.image} alt={provider.title} class="w-full h-full object-cover" />
                            {#if provider.disabled}
								<!-- Overlay Badge -->
								<div
									class="absolute inset-0 bg-black/40 backdrop-blur-[1px] flex items-center justify-center p-1"
								>
									<span
										class="px-2 py-1 text-[10px] font-medium bg-gray-900/80 text-gray-200 border border-gray-700/60 rounded-md shadow-sm"
									>
										Aktuell nicht verfügbar
									</span>
								</div>
							{/if}
						</div>
						<h3 class="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-1">{provider.title}</h3>
						<p class="text-[11px] text-gray-500 dark:text-gray-400 line-clamp-2">{provider.description}</p>
					</div>
				</button>
			{/each}
		</div>
	</div>
</Modal>


<Modal bind:show={showConfirmModal} size="sm">
	<div class="p-6 text-center">
		<div
			class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-amber-100 dark:bg-amber-900/30 mb-4 text-amber-600 dark:text-amber-400"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
				stroke-width="1.5"
				stroke="currentColor"
				class="w-6 h-6"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
				/>
			</svg>
		</div>

		<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
			API-Key wirklich neu generieren?
		</h3>

		<p class="text-sm text-gray-600 dark:text-gray-300 mb-6">
			Der vorherige Key wird dadurch ungültig. Der neue API-Key wird <strong
				>nur einmal angezeigt</strong
			> und kann danach nicht mehr abgerufen werden.
		</p>

		<div class="flex gap-3 justify-end">
			<button
				class="flex-1 px-4 py-2 text-sm rounded-xl border border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
				on:click={() => (showConfirmModal = false)}
			>
				Abbrechen
			</button>
			<button
				class="flex-1 px-4 py-2 text-sm rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-medium transition"
				on:click={confirmAndReGenerateKey}
			>
				Neu generieren
			</button>
		</div>
	</div>
</Modal>

{#if showOpenCode}
	<OpenCodeModal bind:show={showOpenCode} />
{/if}

{#if showCopilotVsCode}
	<CopilotVsCodeModal bind:show={showCopilotVsCode} />
{/if}