<script lang="ts">
	import Modal from '$lib/components/common/Modal.svelte';
	import { generateLiteLLMApiKey, deleteLiteLLMApiKey } from '$lib/apis/litellm';

	export let show = false;

	const downloads = [
		{ label: 'Windows Version', os: 'Windows', url: 'https://opencode.ai/de/download/stable/windows-x64-nsis' },
		{ label: 'macOS Silicon Version', os: 'macOS', url: 'https://opencode.ai/de/download/stable/darwin-aarch64-dmg' },
		{ label: 'macOS Intel Version', os: 'macOS', url: 'https://opencode.ai/de/download/stable/darwin-x64-dmg' },
		{ label: 'Linux DEB Version', os: 'Linux', url: 'https://opencode.ai/de/download/stable/linux-x64-deb' },
		{ label: 'Linux RPM Version', os: 'Linux', url: 'https://opencode.ai/de/download/stable/linux-x64-rpm' }
	];

	let apiKey: string | null = null;
	let response: any = null;
	let isLoading = false;
	let keyError: string | null = null;
	let copied = false;
	let showConfirmModal = false; // Steuert das Modal für die Neu-Generierung

	async function handleGenerateKey() {
		isLoading = true;
		response = null;
		keyError = null;
		generateLiteLLMApiKey(localStorage.token)
		.then((key) => {
			response = key;
			apiKey = response.key;
		})
		.catch((err) => {
			keyError = `Fehler beim Generieren des API-Keys: ${err}`;
		})
		.finally(() => {
			isLoading = false;
		});
	}

	async function handleReGenerateKey() {
		await deleteLiteLLMApiKey(localStorage.token);
		await handleGenerateKey()
	}

	async function confirmAndReGenerateKey() {
		showConfirmModal = false;
		await handleReGenerateKey();
	}

	async function triggerDownload(item: { label: string; url: string }) {
		try {
			const res = await fetch(item.url);
			if (!res.ok) throw new Error(`HTTP ${res.status}`);
			const blob = await res.blob();
			const blobUrl = URL.createObjectURL(blob);

			const a = document.createElement('a');
			a.href = blobUrl;
			a.download = item.url.split('/').pop() ?? 'download';
			document.body.appendChild(a);
			a.click();
			a.remove();
			URL.revokeObjectURL(blobUrl);
		} catch (err) {
			console.warn('Fetch-Download fehlgeschlagen, Fallback auf direkten Link:', err);
			window.open(item.url, '_blank');
		}
	}

	async function copyKey() {
		if (!apiKey) return;
		await navigator.clipboard.writeText(apiKey);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}

	$: if (!show) {
		apiKey = null;
		keyError = null;
		copied = false;
		showConfirmModal = false;
	}
</script>

<Modal bind:show size="lg">
	<div class="px-5 py-4">
		<div class="flex justify-between items-center pb-3">
			<div class="text-lg font-medium dark:text-gray-100">Download OpenCode & generiere API-Key</div>
			<button
				class="self-center"
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
		<div class="mb-4 overflow-hidden rounded-xl bg-black aspect-video flex items-center justify-center">
			<video 
				src="./../../assets/opencode.mp4" 
				autoplay 
				loop 
				muted 
				playsinline
			>
				<track kind="captions" />
				Dein Browser unterstützt dieses Video-Format leider nicht.
			</video>
		</div>
		<div class="text-md font-medium dark:text-gray-100 mb-4">
			OpenCode ist ein Open-Source-Agent, der dir hilft, Code in deinem Terminal, deiner IDE oder auf dem Desktop zu schreiben.
		</div>
		<div class="space-y-4">
			<div class="flex items-start gap-3">
				<span class="text-white-500 text-lg ml-5">*</span>
				<div>
					<h3 class="font-semibold text-gray-900 dark:text-white">LSP-fähig</h3>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						Lädt automatisch die richtigen LSPs für das LLM.
					</p>
				</div>
			</div>

			<div class="flex items-start gap-3">
				<span class="text-white-500 text-lg ml-5">*</span>
				<div>
					<h3 class="font-semibold text-gray-900 dark:text-white">Multi-Session</h3>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						Starte mehrere Agenten parallel im selben Projekt.
					</p>
				</div>
			</div>

			<div class="flex items-start gap-3">
				<span class="text-white-500 text-lg ml-5">*</span>
				<div>
					<h3 class="font-semibold text-gray-900 dark:text-white">Links teilen</h3>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						Teile einen Link zu jeder Sitzung als Referenz oder zum Debuggen.
					</p>
				</div>
			</div>

			<div class="flex items-start gap-3">
				<span class="text-white-500 text-lg ml-5">*</span>
				<div>
					<h3 class="font-semibold text-gray-900 dark:text-white">GitHub Copilot</h3>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						Melde dich mit GitHub an, um deinen Copilot-Account zu nutzen.
					</p>
				</div>
			</div>

			<div class="flex items-start gap-3">
				<span class="text-white-500 text-lg ml-5">*</span>
				<div>
					<h3 class="font-semibold text-gray-900 dark:text-white">ChatGPT Plus/Pro</h3>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						Melde dich mit OpenAI an, um deinen ChatGPT Plus- oder Pro-Account zu nutzen.
					</p>
				</div>
			</div>

			<div class="flex items-start gap-3">
				<span class="text-white-500 text-lg ml-5">*</span>
				<div>
					<h3 class="font-semibold text-gray-900 dark:text-white">Jedes Modell</h3>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						75+ LLM-Anbieter durch Models.dev, einschließlich lokaler Modelle.
					</p>
				</div>
			</div>

			<div class="flex items-start gap-3">
				<span class="text-white-500 text-lg ml-5">*</span>
				<div>
					<h3 class="font-semibold text-gray-900 dark:text-white">Jeder Editor</h3>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						Verfügbar als Terminal-Interface, Desktop-App und IDE-Extension.
					</p>
				</div>
			</div>
		</div>
		<div class="text-md font-medium dark:text-gray-100 mt-4 mb-4">
			Der Open-Source AI-Coding-Agent
		</div>
		<div class="space-y-4">
			<div class="flex items-start gap-3">
				<span class="text-white-500 text-lg ml-5">*</span>
				<div>
					<p class="text-sm text-gray-600 dark:text-gray-400 mb-10">
						Mit über 160,000 GitHub-Stars, 900 Contributors und über 13,000 Commits wird OpenCode von über 7.5M Entwickler:innen jeden Monat genutzt und geschätzt.
					</p>
				</div>
			</div>
		</div>
		<div>
			<h2 class="font-semibold text-gray-900 dark:text-white mb-2">Downloads:</h2>
		</div>
		<div class="flex flex-col gap-2">
			{#each downloads as item}
				<button
					class="flex items-center gap-2 px-3.5 py-2 text-sm rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-gray-100 transition"
					on:click={() => triggerDownload(item)}
				>
					{item.label}
				</button>
			{/each}
		</div>

		<hr class="my-4 border-gray-100 dark:border-gray-850" />

		<div class="text-sm font-medium mb-2 dark:text-gray-100">API-Key</div>

		<button
			class="w-full px-3.5 py-2 text-sm rounded-xl bg-black text-white hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100 transition disabled:opacity-50"
			on:click={handleGenerateKey}
			disabled={isLoading}
		>
			{isLoading ? 'Generiere…' : 'API-Key generieren'}
		</button>

		<div class="mt-3">
			<button
				class="w-full px-3.5 py-2 text-xs font-medium rounded-xl border border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-300 dark:hover:bg-amber-900/40 transition disabled:opacity-50 flex items-center justify-center gap-1.5"
				on:click={() => (showConfirmModal = true)}
				disabled={isLoading}
			>
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
					<path fill-rule="evenodd" d="M13.836 2.477a.75.75 0 0 1 .75.75v3.182a.75.75 0 0 1-.75.75h-3.182a.75.75 0 0 1 0-1.5h1.37l-.84-.841a4.5 4.5 0 0 0-7.08.932.75.75 0 0 1-1.3-.75 6 6 0 0 1 9.44-1.242l.842.84V3.227a.75.75 0 0 1 .75-.75Zm-8.672 7.84a4.5 4.5 0 0 0 7.08-.931.75.75 0 0 1 1.3.75 6 6 0 0 1-9.44 1.241l-.842-.84v1.242a.75.75 0 0 1-1.5 0V8.396a.75.75 0 0 1 .75-.75h3.182a.75.75 0 0 1 0 1.5h-1.37l.84.841Z" clip-rule="evenodd" />
				</svg>
				API-Key neu generieren
			</button>
		</div>
				{#if keyError}
			<div class="text-red-500 text-xs mt-2">{keyError}</div>
		{/if}

		{#if apiKey}
			<div
				class="flex items-center gap-2 mt-3 px-3 py-2 rounded-xl bg-gray-50 dark:bg-gray-850"
			>
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

		<hr class="my-4 border-gray-100 dark:border-gray-850" />

		<div class="text-xs text-gray-600 dark:text-gray-400">
			<p class="font-medium mb-1 text-gray-800 dark:text-gray-200">
				Anleitung zur Installation:
			</p>
			<ol class="list-decimal list-inside space-y-1 pl-1">
				<li>Kopiere den generierten API-Key oben.</li>
				<li>Öffne deine Einstellungen / Konfigurationsdatei.</li>
				<li>Füge den Key im Feld <code class="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">API_KEY</code> ein.</li>
				<li>Speichere die Änderungen und starte die Anwendung neu.</li>
			</ol>
		</div>

	</div>
</Modal>

<Modal bind:show={showConfirmModal} size="sm">
	<div class="p-6 text-center">
		<div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-amber-100 dark:bg-amber-900/30 mb-4 text-amber-600 dark:text-amber-400">
			<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
				<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
			</svg>
		</div>

		<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
			API-Key wirklich neu generieren?
		</h3>

		<p class="text-sm text-gray-600 dark:text-gray-300 mb-6">
			Der vorherige Key wird dadurch ungültig. Der neue API-Key wird <strong>nur einmal angezeigt</strong> und kann danach nicht mehr abgerufen werden.
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