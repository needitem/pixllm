import { writable } from 'svelte/store';

export const desktopSettings = writable<DesktopSettings | null>(null);
