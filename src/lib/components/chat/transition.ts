import { crossfade } from 'svelte/transition';
import { cubicInOut } from 'svelte/easing';
import { writable } from 'svelte/store';

export const LOGO_LOADER_KEY = 'logo-loader';
export const responseLoaderVisible = writable(false);
export const responseLoaderHandoffReady = writable(true);

export const [send, receive] = crossfade({
    duration: 380,
    easing: cubicInOut,
    fallback(node, params, intro) {
        return {
            duration: 200,
            css: (t) => `opacity: ${t}`
        };
    }
});