<script lang="ts">
	import { decode } from 'html-entities';
	import { v4 as uuidv4 } from 'uuid';

	import { getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	const i18n = getContext<Writable<i18nType>>('i18n');

	import { slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	import ChevronRight from '../icons/ChevronRight.svelte';
	import ChevronDown from '../icons/ChevronDown.svelte';
	import Spinner from './Spinner.svelte';
	import WrenchSolid from '../icons/WrenchSolid.svelte';
	import CheckCircle from '../icons/CheckCircle.svelte';
	import XMark from '../icons/XMark.svelte';
	import Image from './Image.svelte';
	import FullHeightIframe from './FullHeightIframe.svelte';
	import { settings } from '$lib/stores';

	export let id: string = '';
	export let attributes: {
		type?: string;
		id?: string;
		name?: string;
		arguments?: string;
		result?: string;
		files?: string;
		embeds?: string;
		done?: string;
		status?: string;
	} = {};

	export let open = false;
	export let grouped = false;
	export let allowEmbeds = false;
	export let className = '';
	export let resolvable = false;
	export let resolving = false;
	export let onResolve: (approved: boolean) => void = () => {};

	const RESULT_PREVIEW_LIMIT = 10000;
	let expandedResult = false;

	$: if (!open) expandedResult = false;
	export let buttonClassName =
		'py-1 text-[0.9375rem] text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition';

	const componentId = id || uuidv4();
interface ToolStateLabel {
		active: string;    // Während der Vorbereitung
		executing: string; // Während der Ausführung
		done: string;      // Nach Abschluss
	}

	// Vollständiges Mapping aller 37 Tools
	const TOOL_CONFIG: Record<string, ToolStateLabel> = {
		// Zeit & Datum
		get_current_timestamp: { active: 'Hole Uhrzeit...', executing: 'Hole Uhrzeit...', done: 'Uhrzeit abgerufen' },
		calculate_timestamp: { active: 'Berechne Zeitstempel...', executing: 'Berechne Zeitstempel...', done: 'Zeitstempel berechnet' },

		// Interaktion
		ask_user: { active: 'Bereite Frage vor...', executing: 'Warte auf Benutzereingabe...', done: 'Benutzereingabe erhalten' },

		// Wissensdatenbanken (Knowledge Bases)
		list_knowledge_bases: { active: 'Lade Wissensdatenbanken...', executing: 'Lade Wissensdatenbanken...', done: 'Wissensdatenbanken geladen' },
		search_knowledge_bases: { active: 'Durchsuche Wissensdatenbanken...', executing: 'Durchsuche Wissensdatenbanken...', done: 'Wissensdatenbanken durchsucht' },
		query_knowledge_bases: { active: 'Frage Wissensdatenbank ab...', executing: 'Frage Wissensdatenbank ab...', done: 'Wissensdatenbank abgefragt' },

		// Dateien in Knowledge Bases
		grep_knowledge_files: { active: 'Durchsuche Dateien (Grep)...', executing: 'Durchsuche Dateien (Grep)...', done: 'Dateien durchsucht' },
		search_knowledge_files: { active: 'Suche in Wissensdateien...', executing: 'Suche in Wissensdateien...', done: 'Wissensdateien durchsucht' },
		query_knowledge_files: { active: 'Frage Wissensdateien ab...', executing: 'Frage Wissensdateien ab...', done: 'Wissensdateien abgefragt' },
		view_knowledge_file: { active: 'Öffne Wissensdatei...', executing: 'Lade Wissensdatei...', done: 'Wissensdatei geöffnet' },

		// Chats
		search_chats: { active: 'Suche in Chats...', executing: 'Suche in Chats...', done: 'Chats durchsucht' },
		view_chat: { active: 'Lade Chat...', executing: 'Lade Chat...', done: 'Chat geladen' },

		// Speicher & Erinnerungen (Memories)
		search_memories: { active: 'Durchsuche Erinnerungen...', executing: 'Durchsuche Erinnerungen...', done: 'Erinnerungen durchsucht' },
		list_memory_paths: { active: 'Lade Speicherpfade...', executing: 'Lade Speicherpfade...', done: 'Speicherpfade geladen' },
		read_memory_path: { active: 'Lese Speicherpfad...', executing: 'Lese Speicherpfad...', done: 'Speicherpfad gelesen' },
		list_memories: { active: 'Lade Erinnerungen...', executing: 'Lade Erinnerungen...', done: 'Erinnerungen geladen' },
		update_memory: { active: 'Aktualisiere Erinnerung...', executing: 'Aktualisiere Erinnerung...', done: 'Erinnerung aktualisiert' },
		add_memory: { active: 'Speichere Erinnerung...', executing: 'Speichere Erinnerung...', done: 'Erinnerung gespeichert' },
		replace_memory_content: { active: 'Ersetze Erinnerungsinhalt...', executing: 'Ersetze Erinnerungsinhalt...', done: 'Erinnerungsinhalt ersetzt' },
		delete_memory: { active: 'Lösche Erinnerung...', executing: 'Lösche Erinnerung...', done: 'Erinnerung gelöscht' },

		// Bilder
		generate_image: { active: 'Bereite Bildgenerierung vor...', executing: 'Generiere Bild...', done: 'Bild generiert' },
		edit_image: { active: 'Bereite Bildbearbeitung vor...', executing: 'Bearbeite Bild...', done: 'Bild bearbeitet' },

		// Notizen
		search_notes: { active: 'Durchsuche Notizen...', executing: 'Durchsuche Notizen...', done: 'Notizen durchsucht' },
		view_note: { active: 'Öffne Notiz...', executing: 'Lade Notiz...', done: 'Notiz geöffnet' },
		write_note: { active: 'Erstelle Notiz...', executing: 'Schreibe Notiz...', done: 'Notiz erstellt' },
		replace_note_content: { active: 'Überarbeite Notiz...', executing: 'Ersetze Notizinhalt...', done: 'Notiz überarbeitet' },

		// Aufgaben & Automationen
		create_tasks: { active: 'Erstelle Aufgabe...', executing: 'Erstelle Aufgabe...', done: 'Aufgabe erstellt' },
		update_task: { active: 'Aktualisiere Aufgabe...', executing: 'Aktualisiere Aufgabe...', done: 'Aufgabe aktualisiert' },
		create_automation: { active: 'Richte Automation ein...', executing: 'Erstelle Automation...', done: 'Automation eingerichtet' },
		update_automation: { active: 'Aktualisiere Automation...', executing: 'Aktualisiere Automation...', done: 'Automation aktualisiert' },
		list_automations: { active: 'Lade Automationen...', executing: 'Lade Automationen...', done: 'Automationen geladen' },
		toggle_automation: { active: 'Schalte Automation um...', executing: 'Schalte Automation um...', done: 'Automation umgeschaltet' },
		delete_automation: { active: 'Lösche Automation...', executing: 'Lösche Automation...', done: 'Automation gelöscht' },

		// Kalender
		search_calendar_events: { active: 'Durchsuche Kalender...', executing: 'Durchsuche Kalender...', done: 'Kalender durchsucht' },
		create_calendar_event: { active: 'Erstelle Kalendereintrag...', executing: 'Trage Termin ein...', done: 'Termin eingetragen' },
		update_calendar_event: { active: 'Aktualisiere Kalendereintrag...', executing: 'Aktualisiere Termin...', done: 'Termin aktualisiert' },
		delete_calendar_event: { active: 'Lösche Kalendereintrag...', executing: 'Lösche Termin...', done: 'Termin gelöscht' },

		// Websuche
		search_web: { active: 'Durchsuche Web...', executing: 'Durchsuche Web...', done: 'Web durchsucht' },
		fetch_url: { active: 'Hole URL...', executing: 'Hole URL...', done: 'URL abgerufen' },
	};

	function formatFallbackName(name: string): string {
		if (!name) return '';
		return name
			.replace(/_/g, ' ')
			.replace(/([a-z])([A-Z])/g, '$1 $2')
			.replace(/\b\w/g, (char) => char.toUpperCase());
	}

	function getStatusLabel(
		name: string,
		isDoneState: boolean,
		isExecutingState: boolean,
		isPreparingState: boolean
	): string {
		const config = TOOL_CONFIG[name];

		if (config) {
			if (isDoneState) return config.done;
			if (isExecutingState) return config.executing;
			if (isPreparingState) return config.active;
		}

		const prettyName = formatFallbackName(name);

		if (isDoneState) return `${prettyName} abgeschlossen`;
		if (isExecutingState) return `${prettyName} wird ausgeführt...`;
		if (isPreparingState) return `${prettyName} wird vorbereitet...`;

		return prettyName;
	}

	$: statusLabel = getStatusLabel(attributes?.name ?? '', isDone, isExecuting, isPreparing);

	function parseJSONString(str: string) {
		// Iteratively unwrap nested JSON-encoded strings. Same result as the previous
		// recursive form, but without the stack-overflow-and-recover path it hit on
		// scalar values (e.g. JSON.parse('5') -> 5 -> infinite self-recursion).
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		let value: any = str;
		while (typeof value === 'string') {
			try {
				value = JSON.parse(value);
			} catch {
				break;
			}
		}
		return value;
	}

	function formatJSONString(str: string) {
		try {
			const parsed = parseJSONString(str);
			if (typeof parsed === 'object') {
				return JSON.stringify(parsed, null, 2);
			} else {
				return String(parsed);
			}
		} catch (e) {
			return str;
		}
	}

	function parseArguments(str: string): Record<string, unknown> | null {
		try {
			const parsed = parseJSONString(str);
			if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
				return parsed as Record<string, unknown>;
			}
			return null;
		} catch {
			return null;
		}
	}

	function isToolResultError(value: unknown): boolean {
		if (typeof value === 'string') {
			const text = value.trim().toLowerCase();
			if (
				text.startsWith('error:') ||
				text.startsWith('exception:') ||
				text.startsWith('traceback') ||
				text.startsWith('http error!')
			) {
				return true;
			}
		}

		let parsed = value;
		while (typeof parsed === 'string') {
			try {
				parsed = JSON.parse(parsed);
			} catch {
				break;
			}
		}
		if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) return false;

		const result = parsed as Record<string, unknown>;
		const error = result.error;
		if (
			(typeof error === 'string' && error.trim().length > 0) ||
			(typeof error === 'object' && error !== null)
		) {
			return true;
		}

		const status = typeof result.status === 'string' ? result.status.trim().toLowerCase() : '';
		if (status === 'error' || status === 'failed') return true;

		const message = result.message;
		return (
			(result.success === false || result.ok === false) &&
			((typeof message === 'string' && message.trim().length > 0) ||
				(typeof message === 'object' && message !== null))
		);
	}

	export let resultContent: string = '';

	$: result = resultContent || decode(attributes?.result ?? '');
	$: files = parseJSONString(decode(attributes?.files ?? ''));
	$: embeds = parseJSONString(decode(attributes?.embeds ?? ''));
	$: isAskUser = attributes?.name === 'ask_user';
	$: needsInput = isAskUser && attributes?.status === 'pending';
	$: needsApproval = !isAskUser && attributes?.status === 'pending' && resolvable;
	$: args =
		open || needsApproval || needsInput || (Array.isArray(embeds) && embeds.length > 0)
			? decode(attributes?.arguments ?? '')
			: '';
	$: isRejected = attributes?.status === 'rejected';
	$: isDone =
		attributes?.done === 'true' ||
		attributes?.status === 'failed' ||
		attributes?.status === 'incomplete';
	$: isExecuting = !isDone && !isRejected && attributes?.status === 'completed';
	$: isPreparing = !isDone && !isRejected && !needsApproval && !needsInput && !isExecuting;
	$: isActive = isPreparing || isExecuting;
	$: isError = attributes?.status === 'failed' || (isDone && isToolResultError(result));

	$: parsedArgs = parseArguments(args);
	$: parsedResult = parseJSONString(result);

	const toggleOpen = () => {
		open = !open;
	};

	const toggleOpenOnKeydown = (event: KeyboardEvent) => {
		if (event.key !== 'Enter' && event.key !== ' ') {
			return;
		}

		event.preventDefault();
		toggleOpen();
	};
</script>

<div {id} class={className}>
	{#if allowEmbeds && !grouped && embeds && Array.isArray(embeds) && embeds.length > 0}
		<!-- Embed Mode: Show iframes without collapsible behavior -->
		<div class="py-1 w-full cursor-pointer">
			<div class="w-full text-xs text-gray-500">
				{attributes.name}
			</div>
			{#each embeds as embed, idx}
				<div class="my-2" id={`${componentId}-tool-call-embed-${idx}`}>
					<FullHeightIframe
						src={embed}
						{args}
						allowScripts={true}
						allowForms={$settings?.iframeSandboxAllowForms ?? false}
						allowSameOrigin={$settings?.iframeSandboxAllowSameOrigin ?? false}
						allowPopups={true}
					/>
				</div>
			{/each}
		</div>
	{:else}
		<!-- Tool call display -->
		<!-- Tool call display -->
		<div
			class="{buttonClassName} w-full min-w-0 cursor-pointer"
			role="button"
			tabindex="0"
			on:click={toggleOpen}
			on:keydown={toggleOpenOnKeydown}
		>
			<!-- inline-flex sorgt dafür, dass sich das Element eng um Inhalt & Chevron schmiegt -->
			<div
				class="inline-flex max-w-full font-normal items-center gap-1.5 {isActive
					? 'shimmer'
					: ''}"
			>
				<!-- Status icon -->
				{#if isActive}
					<div>
						<Spinner className="size-4" />
					</div>
				{:else if isRejected}
					<div class="text-red-400 dark:text-red-500">
						<XMark className="size-4" strokeWidth="2.5" />
					</div>
				{:else if isError}
					<div class="text-red-500 dark:text-red-400">
						<XMark className="size-4" strokeWidth="2.5" />
					</div>
				{:else if isDone}
					<div class="text-emerald-500 dark:text-emerald-400">
						<CheckCircle className="size-4" strokeWidth="2" />
					</div>
				{:else}
					<div class="text-gray-400 dark:text-gray-500">
						<WrenchSolid className="size-3.5" />
					</div>
				{/if}

				<!-- Label (ohne flex-1, damit es keine freie Fläche auffüllt) -->
				<div class="min-w-0 truncate">
					<span class="font-normal text-black dark:text-gray-500">
						{#if isRejected}
							{$i18n.t('Denied {{NAME}}', { NAME: statusLabel })}
						{:else if needsInput}
							{$i18n.t('Input needed')}
						{:else if needsApproval}
							{$i18n.t('Allow {{NAME}}?', { NAME: statusLabel })}
						{:else}
							{statusLabel}
						{/if}
					</span>
				</div>

				{#if needsApproval && !isAskUser}
					<span class="flex gap-1 shrink-0 ml-1">
						<button
							type="button"
							class="tool-call-allow-button text-[0.6875rem] px-2.5 py-0.5 rounded-md text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-white/8 hover:bg-gray-200 dark:hover:bg-white/12 transition-colors duration-100 disabled:opacity-50"
							disabled={resolving}
							on:click|stopPropagation={() => onResolve(true)}
						>
							{$i18n.t('Allow')}
						</button>
						<button
							type="button"
							class="tool-call-deny-button text-[0.6875rem] px-2 py-0.5 rounded-md text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-100 disabled:opacity-50"
							disabled={resolving}
							on:click|stopPropagation={() => onResolve(false)}
						>
							{$i18n.t('Deny')}
						</button>
					</span>
				{:else}
					<!-- Chevron (sitzt jetzt direkt neben dem Text dank gap-1.5) -->
					<div class="flex shrink-0 self-center translate-y-[1px]">
						{#if open}
							<ChevronDown strokeWidth="3.5" className="size-3" />
						{:else}
							<ChevronRight strokeWidth="3.5" className="size-3" />
						{/if}
					</div>
				{/if}
			</div>
		</div>

		{#if open}
			<div transition:slide={{ duration: 300, easing: quintOut, axis: 'y' }}>
				<div
					class="border border-gray-50 dark:border-gray-850/30 rounded-2xl my-1.5 p-2.5 space-y-2"
				>
					{#if args}
						<!-- Input -->
						<div>
							<div
								class="text-[0.625rem] uppercase tracking-wider font-normal text-gray-400 dark:text-gray-500 mb-1.5 px-1"
							>
								{$i18n.t('Input')}
							</div>

							{#if parsedArgs}
								<div class="px-1 space-y-0.5">
									{#each Object.entries(parsedArgs) as [key, value]}
										<div class="flex gap-2 text-xs py-0.5">
											<span class="font-normal text-gray-600 dark:text-gray-400 shrink-0"
												>{key}</span
											>
											<span class="text-gray-800 dark:text-gray-200 break-all"
												>{typeof value === 'object' ? JSON.stringify(value) : value}</span
											>
										</div>
									{/each}
								</div>
							{:else}
								<div class="tool-call-body w-full max-w-none!">
									<pre
										class="text-xs text-gray-600 dark:text-gray-300 whitespace-pre font-mono bg-gray-50 dark:bg-gray-900 rounded-lg p-2 overflow-x-auto">{formatJSONString(
											args
										)}</pre>
								</div>
							{/if}
						</div>
					{/if}

					<!-- Output -->
					{#if isDone && result}
						<div>
							<div
								class="text-[0.625rem] uppercase tracking-wider font-normal text-gray-400 dark:text-gray-500 mb-1.5 px-1"
							>
								{$i18n.t('Output')}
							</div>
							<div class="w-full max-w-none!">
								{#if typeof parsedResult === 'object' && parsedResult !== null}
									<pre
										class="text-xs text-gray-600 dark:text-gray-300 whitespace-pre font-mono bg-gray-50 dark:bg-gray-900 rounded-lg p-2 overflow-x-auto">{JSON.stringify(
											parsedResult,
											null,
											2
										)}</pre>
								{:else}
									{@const resultStr = String(parsedResult)}
									{@const isTruncated = resultStr.length > RESULT_PREVIEW_LIMIT && !expandedResult}
									<pre
										class="text-xs text-gray-600 dark:text-gray-300 whitespace-pre-wrap break-words font-mono">{isTruncated
											? resultStr.slice(0, RESULT_PREVIEW_LIMIT)
											: resultStr}</pre>
									{#if isTruncated}
										<button
											class="mt-1 text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition"
											on:click|stopPropagation={() => {
												expandedResult = true;
											}}
										>
											{$i18n.t('Show all ({{COUNT}} characters)', {
												COUNT: resultStr.length.toLocaleString()
											})}
										</button>
									{/if}
								{/if}
							</div>
						</div>
					{/if}
				</div>
			</div>
		{/if}
	{/if}

	<!-- Files display (images etc.) when done -->
	{#if isDone}
		{#if typeof files === 'object'}
			{#each files ?? [] as file, idx}
				{#if typeof file === 'string'}
					{#if file.startsWith('data:image/')}
						<Image id={`${componentId}-tool-call-result-${idx}`} src={file} alt="Image" />
					{/if}
				{:else if typeof file === 'object'}
					{#if (file.type === 'image' || (file?.content_type ?? '').startsWith('image/')) && file.url}
						<Image id={`${componentId}-tool-call-result-${idx}`} src={file.url} alt="Image" />
					{/if}
				{/if}
			{/each}
		{/if}
	{/if}
</div>
