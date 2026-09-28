<script lang="ts">
	import Modal from '$lib/components/common/Modal.svelte';

	export let show = false;

	const downloads = [
		{
			label: 'Windows Version',
			os: 'Windows',
			url: 'https://opencode.ai/de/download/stable/windows-x64-nsis'
		},
		{
			label: 'macOS Silicon Version',
			os: 'macOS',
			url: 'https://opencode.ai/de/download/stable/darwin-aarch64-dmg'
		},
		{
			label: 'macOS Intel Version',
			os: 'macOS',
			url: 'https://opencode.ai/de/download/stable/darwin-x64-dmg'
		},
		{
			label: 'Linux DEB Version',
			os: 'Linux',
			url: 'https://opencode.ai/de/download/stable/linux-x64-deb'
		},
		{
			label: 'Linux RPM Version',
			os: 'Linux',
			url: 'https://opencode.ai/de/download/stable/linux-x64-rpm'
		}
	];

	// Manueller API-Key State
	let apiKey = '';

	// Trackt kopierte Code-Blöcke für Feedback ("Kopiert!")
	let copiedIndex: string | null = null;

	// State für den Anleitungs-Switch ('windows' oder 'unix')
	let activeTab: 'windows' | 'unix' = 'windows';

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

	async function copyToClipboard(text: string, id: string) {
		await navigator.clipboard.writeText(text);
		copiedIndex = id;
		setTimeout(() => {
			if (copiedIndex === id) copiedIndex = null;
		}, 2000);
	}

	$: if (!show) {
		apiKey = '';
		activeTab = 'windows';
		copiedIndex = null;
	}

	// Hilfsvariable für den formatierten API-Key in den Befehlen
	$: formattedKey = apiKey.trim() ? `${apiKey.trim()}` : '"API Key hier"';

	// Definitionen der Commands für einfaches Kopieren & Wiederverwenden
	$: winPrepCmd = `winget install OpenJS.NodeJS.LTS\n\nwinget install jqlang.jq\n\nwinget install git.git`;
	$: winConfigCmd = `[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)\n$OutputEncoding = [System.Text.UTF8Encoding]::new($false)\n\nSet-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser\n\nmkdir "$HOME\\.config\\opencode" -Force | Out-Null\niwr https://opencode.office.swms.de/opencode.json -OutFile "$HOME\\.config\\opencode\\opencode.json"\n\n$content = jq --arg key ${formattedKey} '.provider.swms.options.apiKey = $key' "$HOME\\.config\\opencode\\opencode.json"\n[System.IO.File]::WriteAllText("$HOME\\.config\\opencode\\opencode.json", $content, [System.Text.UTF8Encoding]::new($false))`;
	$: winPluginsCmd = `# ponytail plugin\n$content = jq --arg p "@dietrichgebert/ponytail" '.plugin = (.plugin // []) + [$p]' "$HOME\\.config\\opencode\\opencode.json"\n[System.IO.File]::WriteAllText("$HOME\\.config\\opencode\\opencode.json", $content, [System.Text.UTF8Encoding]::new($false))\n\n# i-have-adhd plugin\ngit clone https://github.com/ayghri/i-have-adhd "$HOME\\.config\\opencode\\vendor\\i-have-adhd"\n$adhdPluginPath = "$HOME\\.config\\opencode\\vendor\\i-have-adhd\\.opencode\\plugins\\i-have-adhd.mjs" -replace '\\\\', '/'\n$content = jq --arg p $adhdPluginPath '.plugin = (.plugin // []) + [$p]' "$HOME\\.config\\opencode\\opencode.json"\n[System.IO.File]::WriteAllText("$HOME\\.config\\opencode\\opencode.json", $content, [System.Text.UTF8Encoding]::new($false))\nNew-Item -ItemType File -Path "$HOME\\.config\\opencode\\.i-have-adhd-always" -Force | Out-Null`;
	$: winToolsCmd = `npm install -g ui-ux-pro-max-cli\nuipro init --ai opencode --global\n\n# mattpocock skills (Interaktiv - Prompts manuell beantworten und OpenCode als Ziel wählen)\nnpx skills@latest add mattpocock/skills`;
	$: winUpdateCmd = `[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)\n$OutputEncoding = [System.Text.UTF8Encoding]::new($false)\n\niwr https://opencode.office.swms.de/opencode.json -OutFile "$env:TEMP\\opencode.remote.json"\n\n$local = Get-Content "$HOME\\.config\\opencode\\opencode.json" -Raw | ConvertFrom-Json\n$remote = Get-Content "$env:TEMP\\opencode.remote.json" -Raw | ConvertFrom-Json\n\n$local.provider.swms.models = $remote.provider.swms.models\n$local | ConvertTo-Json -Depth 100 | Set-Content "$HOME\\.config\\opencode\\opencode.json" -Encoding utf8\nRemove-Item "$env:TEMP\\opencode.remote.json" -Force\n\n# Skills & Plugins aktualisieren\ngit -C "$HOME\\.config\\opencode\\vendor\\i-have-adhd" pull\nnpm update -g ui-ux-pro-max-cli\nuipro update --global\nnpx skills@latest update`;

	$: unixDownloadCmd = `mkdir -p ~/.config/opencode\ncurl -fsSL https://opencode.office.swms.de/opencode.json -o ~/.config/opencode/opencode.json`;
	$: unixConfigCmd = `jq --arg key ${formattedKey} '.provider.swms.options.apiKey = $key' ~/.config/opencode/opencode.json > ~/.config/opencode/opencode.json.tmp && mv ~/.config/opencode/opencode.json.tmp ~/.config/opencode/opencode.json`;
	$: unixUpdateCmd = `curl -fsSL https://opencode.office.swms.de/opencode.json -o /tmp/opencode.remote.json\njq -s '.[1] * .[0]' ~/.config/opencode/opencode.json /tmp/opencode.remote.json > ~/.config/opencode/opencode.json.tmp && mv ~/.config/opencode/opencode.json.tmp ~/.config/opencode/opencode.json`;
</script>

<Modal bind:show size="2xl">
	<div class="px-5 py-4">
		<div class="flex justify-between items-center pb-3">
			<div class="text-lg font-medium dark:text-gray-100">Download OpenCode & Konfiguration</div>
			<button class="self-center" on:click={() => (show = false)} aria-label="Schließen">
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
		<div
			class="mb-4 overflow-hidden rounded-xl bg-black aspect-video flex items-center justify-center"
		>
			<video src="./../../assets/tutorial/opencode.mp4" autoplay loop muted playsinline>
				<track kind="captions" />
				Dein Browser unterstützt dieses Video-Format leider nicht.
			</video>
		</div>
		<button
			class="mb-4 px-3.5 py-2 text-sm rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-gray-100 transition"
			on:click={() => window.open('https://opencode.ai/docs/de', '_blank')}
		>
			OpenCode Dokumentation öffnen
		</button>
		<div class="text-md font-medium dark:text-gray-100 ml-2 mb-4">
			OpenCode ist ein Open-Source-Agent, der dir hilft, Code in deinem Terminal, deiner IDE oder
			auf dem Desktop zu schreiben.
		</div>
		<div>
			<h2 class="font-semibold text-gray-900 dark:text-white ml-2 mb-2">Downloads</h2>
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

		<!-- API-Key Input Feld -->
		<h2 class="font-semibold mb-1 dark:text-gray-100">API-Key eintragen</h2>
		<div class="text-gray-500 text-xs mt-1 mb-2 text-left">
			Füge deinen API-Key hier ein, um ihn direkt in die unteren Einrichtungsbefehle zu übernehmen:
		</div>

		<div class="mt-2">
			<input
				type="text"
				placeholder="Füge deinen API-Key hier ein..."
				bind:value={apiKey}
				class="w-full px-3.5 py-2 text-sm rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-amber-500/50 transition font-mono"
			/>
		</div>

		<hr class="my-4 border-gray-100 dark:border-gray-850" />

		<div class="text-sm text-gray-600 dark:text-gray-400 mt-5 mb-10">
			<!-- Tab Switcher -->
			<div class="flex flex-col items-start gap-2 mb-6">
				<div class="flex bg-gray-100 dark:bg-gray-850 p-1 rounded-xl">
					<button
						class="px-3 py-1.5 text-sm font-medium rounded-lg transition {activeTab === 'windows'
							? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
							: 'text-gray-500 hover:text-gray-900 dark:hover:text-white'}"
						on:click={() => (activeTab = 'windows')}
					>
						Windows
					</button>
					<button
						class="px-3 py-1.5 text-sm font-medium rounded-lg transition {activeTab === 'unix'
							? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
							: 'text-gray-500 hover:text-gray-900 dark:hover:text-white'}"
						on:click={() => (activeTab = 'unix')}
					>
						macOS / Linux
					</button>
				</div>
			</div>

			{#if activeTab === 'windows'}
				<!-- Installation Windows -->
				<h3 class="font-semibold text-gray-900 dark:text-gray-100 text-base mb-3">
					Anleitung zur Einrichtung (PowerShell)
				</h3>

				<ol class="list-decimal list-inside space-y-5 mb-8 text-gray-700 dark:text-gray-300">
					<li>Installieren Sie zuerst OpenCode.</li>
					<li>
						Wenn OpenCode schon installiert ist und eine Config-Datei für OpenCode auf Ihrem Rechner
						vorhanden ist, nutzen Sie die Anleitung zum Updaten.
					</li>
					<li>
						<span
							><strong>Paketmanager vorbereiten:</strong>
							<code
								class="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 font-mono text-xs"
								>NodeJS</code
							>,
							<code
								class="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 font-mono text-xs"
								>jq</code
							>
							und
							<code
								class="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 font-mono text-xs"
								>git</code
							> installieren:</span
						>

						<div class="relative mt-2 mb-2 group">
							<button
								class="absolute top-2 right-2 px-2.5 py-1 text-xs rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 transition z-10"
								on:click={() => copyToClipboard(winPrepCmd, 'winPrep')}
							>
								{copiedIndex === 'winPrep' ? '✓ Kopiert' : 'Kopieren'}
							</button>
							<code
								class="block whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-3 pr-20 rounded-xl font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto leading-relaxed border border-gray-200 dark:border-gray-700/50"
								>{winPrepCmd}</code
							>
						</div>
						<span class="text-sm text-gray-500 dark:text-gray-400 font-semibold"
							>Starte deine <strong>PowerShell</strong> am besten einmal neu</span
						>
					</li>
					<li>
						<span
							><strong
								>UTF-8 Standard setzen, Execution Policy anpassen, Konfiguration herunterladen &
								API-Key eintragen:</strong
							></span
						>
						<div class="relative mt-2 group">
							<button
								class="absolute top-2 right-2 px-2.5 py-1 text-xs rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 transition z-10"
								on:click={() => copyToClipboard(winConfigCmd, 'winConfig')}
							>
								{copiedIndex === 'winConfig' ? '✓ Kopiert' : 'Kopieren'}
							</button>
							<code
								class="block whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-3 pr-20 rounded-xl font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto leading-relaxed border border-gray-200 dark:border-gray-700/50"
								>{winConfigCmd}</code
							>
						</div>
					</li>
					<li>
						<span
							><strong>Plugins installieren (ponytail & i-have-adhd):</strong> Fügt die Erweiterungen
							zur Konfigurationsdatei hinzu:</span
						>
						<div class="relative mt-2 group">
							<button
								class="absolute top-2 right-2 px-2.5 py-1 text-xs rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 transition z-10"
								on:click={() => copyToClipboard(winPluginsCmd, 'winPlugins')}
							>
								{copiedIndex === 'winPlugins' ? '✓ Kopiert' : 'Kopieren'}
							</button>
							<code
								class="block whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-3 pr-20 rounded-xl font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto leading-relaxed border border-gray-200 dark:border-gray-700/50"
								>{winPluginsCmd}</code
							>
						</div>
					</li>
					<li>
						<span><strong>Globales UI/UX Tooling & Skills installieren:</strong></span>
						<div class="relative mt-2 group">
							<button
								class="absolute top-2 right-2 px-2.5 py-1 text-xs rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 transition z-10"
								on:click={() => copyToClipboard(winToolsCmd, 'winTools')}
							>
								{copiedIndex === 'winTools' ? '✓ Kopiert' : 'Kopieren'}
							</button>
							<code
								class="block whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-3 pr-20 rounded-xl font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto leading-relaxed border border-gray-200 dark:border-gray-700/50"
								>{winToolsCmd}</code
							>
						</div>
					</li>
					<li>Starten Sie OpenCode neu und Sie sind fertig!</li>
				</ol>

				<hr class="my-6 border-gray-100 dark:border-gray-850" />

				<!-- Update Windows -->
				<h3 class="font-semibold text-gray-900 dark:text-gray-100 text-base mb-3">
					Anleitung zum Updaten
				</h3>
				<ol class="list-decimal list-inside space-y-4 text-gray-700 dark:text-gray-300">
					<li>
						Der API-Key sowie benutzerdefinierte Einstellungen bleiben in der Config erhalten.
					</li>
					<li>
						<span
							>Führen Sie folgende Befehle in der <strong>PowerShell</strong> aus, um die SWMS-Modelle
							und installierten Skills zu aktualisieren:</span
						>
						<div class="relative mt-2 group">
							<button
								class="absolute top-2 right-2 px-2.5 py-1 text-xs rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 transition z-10"
								on:click={() => copyToClipboard(winUpdateCmd, 'winUpdate')}
							>
								{copiedIndex === 'winUpdate' ? '✓ Kopiert' : 'Kopieren'}
							</button>
							<code
								class="block whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-3 pr-20 rounded-xl font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto leading-relaxed border border-gray-200 dark:border-gray-700/50"
								>{winUpdateCmd}</code
							>
						</div>
					</li>
					<li>Starten Sie OpenCode neu und Sie sind fertig!</li>
				</ol>
			{:else if activeTab === 'unix'}
				<!-- Installation Unix -->
				<h3 class="font-semibold text-gray-900 dark:text-gray-100 text-base mb-3">
					Anleitung zur Installation
				</h3>
				<ol class="list-decimal list-inside space-y-4 mb-8 text-gray-700 dark:text-gray-300">
					<li>Installieren Sie zuerst OpenCode.</li>
					<li>
						Wenn schon eine Config-Datei für OpenCode auf Ihrem Rechner vorhanden ist, nutzen Sie
						die Anleitung zum Updaten.
					</li>
					<li>
						<span>Kopieren Sie diesen Befehl und geben Sie ihn in Ihr Terminal ein:</span>
						<div class="relative mt-2 group">
							<button
								class="absolute top-2 right-2 px-2.5 py-1 text-xs rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 transition z-10"
								on:click={() => copyToClipboard(unixDownloadCmd, 'unixDownload')}
							>
								{copiedIndex === 'unixDownload' ? '✓ Kopiert' : 'Kopieren'}
							</button>
							<code
								class="block whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-3 pr-20 rounded-xl font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto leading-relaxed border border-gray-200 dark:border-gray-700/50"
								>{unixDownloadCmd}</code
							>
						</div>
					</li>
					<li>
						<span>API-Schlüssel in die Konfiguration eintragen:</span>
						<div class="relative mt-2 group">
							<button
								class="absolute top-2 right-2 px-2.5 py-1 text-xs rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 transition z-10"
								on:click={() => copyToClipboard(unixConfigCmd, 'unixConfig')}
							>
								{copiedIndex === 'unixConfig' ? '✓ Kopiert' : 'Kopieren'}
							</button>
							<code
								class="block whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-3 pr-20 rounded-xl font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto leading-relaxed border border-gray-200 dark:border-gray-700/50"
								>{unixConfigCmd}</code
							>
						</div>
					</li>
					<li>Starten Sie OpenCode neu und Sie sind fertig!</li>
				</ol>

				<hr class="my-6 border-gray-100 dark:border-gray-850" />

				<!-- Update Unix -->
				<h3 class="font-semibold text-gray-900 dark:text-gray-100 text-base mb-3">
					Anleitung zum Updaten
				</h3>
				<ol class="list-decimal list-inside space-y-4 text-gray-700 dark:text-gray-300">
					<li>Der API-Key bleibt in der Config erhalten.</li>
					<li>
						<span>Um die Config zu aktualisieren, geben Sie diesen Befehl in das Terminal ein:</span
						>
						<div class="relative mt-2 group">
							<button
								class="absolute top-2 right-2 px-2.5 py-1 text-xs rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 transition z-10"
								on:click={() => copyToClipboard(unixUpdateCmd, 'unixUpdate')}
							>
								{copiedIndex === 'unixUpdate' ? '✓ Kopiert' : 'Kopieren'}
							</button>
							<code
								class="block whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-3 pr-20 rounded-xl font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto leading-relaxed border border-gray-200 dark:border-gray-700/50"
								>{unixUpdateCmd}</code
							>
						</div>
					</li>
					<li>Starten Sie OpenCode neu und Sie sind fertig!</li>
				</ol>
			{/if}
		</div>
	</div>
</Modal>
