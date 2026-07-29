<script lang="ts">
	
	import Modal from '$lib/components/common/Modal.svelte';
    import { generateLiteLLMApiKey } from '$lib/apis/litellm';

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


    async function handleGenerateKey() {
        isLoading = true;
        response = null;
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
	let showConfirmModal = false; // Neuer Status für das Bestätigungs-Modal


	async function confirmAndGenerateKey() {
		showConfirmModal = false;
		await handleGenerateKey();
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
			on:click={() => (showConfirmModal = true)}
			disabled={isLoading}
		>
			{isLoading ? 'Generiere…' : 'API-Key generieren'}
		</button>

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
        <div class="text-xs text-gray-600 dark:text-gray-400 mt-2">
            <p class="font-medium mb-1 text-gray-800 dark:text-gray-200">
		    Der generierte API-Key wird nur einmal angezeigt und kann danach nicht mehr abgerufen werden. Wenn Sie ihren verloren haben, wenden sie sich an ihren Administrator.</p>
        </div>

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
</Modal
>
<Modal bind:show={showConfirmModal} size="sm">
	<div class="p-6 text-center">
		<div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-amber-100 dark:bg-amber-900/30 mb-4 text-amber-600 dark:text-amber-400">
			<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
				<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
			</svg>
		</div>

		<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
			Wichtiger Hinweis zum API-Key
		</h3>

		<p class="text-sm text-gray-600 dark:text-gray-300 mb-6">
			Der generierte API-Key wird <strong>nur einmal angezeigt</strong> und kann danach nicht mehr abgerufen werden. Wenn Sie ihn verlieren, müssen Sie sich an Ihren Administrator wenden.
		</p>

		<div class="flex gap-3 justify-end">
			<button
				class="flex-1 px-4 py-2 text-sm rounded-xl border border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
				on:click={() => (showConfirmModal = false)}
			>
				Abbrechen
			</button>
			<button
				class="flex-1 px-4 py-2 text-sm rounded-xl bg-black text-white dark:bg-white dark:text-black font-medium hover:opacity-90 transition"
				on:click={confirmAndGenerateKey}
			>
				Verstanden
			</button>
		</div>
	</div>
</Modal>