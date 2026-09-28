import { crossfade } from 'svelte/transition';
import { cubicInOut } from 'svelte/easing';
import { writable } from 'svelte/store';

export const LOGO_LOADER_KEY = 'logo-loader';
export const responseLoaderVisible = writable(false);

export const [send, receive] = crossfade({
	duration: 380,
	easing: cubicInOut,
	fallback(node, params, intro) {
		return {
			duration: 200,
			css: (t) => {
				// intro ist true beim Einblenden (Ziel), false beim Ausblenden (Start)
				// Beim Ausblendenfaden wir extrem schnell aus (t^3), damit keine "Doppelung" zu sehen ist
				const easeOpacity = intro ? Math.pow(t, 0.5) : Math.pow(t, 3);
				return `opacity: ${easeOpacity}`;
			}
		};
	}
});