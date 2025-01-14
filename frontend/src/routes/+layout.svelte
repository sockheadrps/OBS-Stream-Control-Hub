<script lang="ts">
	import '../app.css';
	import { Dropdown, DropdownItem, AccordionItem, Accordion } from 'flowbite-svelte';
	import { ChevronDownOutline, HomeOutline } from 'flowbite-svelte-icons';
	let { children } = $props();
	import { Button, DropdownDivider } from 'flowbite-svelte';
	import { ChevronRightOutline } from 'flowbite-svelte-icons';
	import { onMount, onDestroy } from 'svelte';
	import { fade } from 'svelte/transition';
	import { browser } from '$app/environment';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import { page } from '$app/stores';
	import { navigating } from '$app/stores';
	import { socketStore, initializeSocket, sendMessage } from '../stores/ws_audio_player';

	let APsocket: WebSocket | null = null;
	const months = [
		'January',
		'February',
		'March',
		'April',
		'May',
		'June',
		'July',
		'August',
		'September',
		'October',
		'November',
		'December'
	];

	let downloadOptions = ['CSV', 'Excel', 'ZIP'];

	function showDownloadOptions(month: string) {
		return downloadOptions.map((option) => ({
			label: option
			// onclick: () => generateReport(month, option.toLowerCase())
		}));
	}

	let expTypeIsOpen = $state(false);

	let dropdownRef: HTMLElement | null;

	// Close dropdown when clicked outside
	function handleClickOutside(event: MouseEvent) {
		if (dropdownRef && !dropdownRef.contains(event.target as Node)) {
			expTypeIsOpen = false;
		}
	}

	$effect(() => {
		if (browser) {
			handleClickOutside(new MouseEvent('mousedown'));
		}
	});
	let ready = $state(false);
	// Add event listener when the component is mounted
	onMount(() => {
		if (browser) {
			document.addEventListener('mousedown', handleClickOutside);
			dropdownRef = document.getElementById('export-dropdown');
			ready = true;

			// Only initialize socket if not already connected
			if (!$socketStore.socket) {
				console.log('Initializing WebSocket...');
				APsocket = initializeSocket();
			} else {
				console.log('Using existing WebSocket...');
				APsocket = $socketStore.socket;
			}

			return () => {
				document.removeEventListener('mousedown', handleClickOutside);
				if (APsocket) {
					console.log('Closing WebSocket...');
					APsocket.close();
				}
			};
		}
	});

	// Clean up event listener when the component is destroyed
</script>

{#if $page.url.pathname !== '/browser_sources/interim'}
	<header class="bg-blue-500 p-4 text-white dark:bg-gray-800">
		<nav
			class="container mx-auto flex items-center justify-between"
			out:fade={{ duration: 400, opacity: 0, x: -20 }}
			in:fade={{ delay: 400, duration: 400, opacity: 1, x: 0, easing: quintOut }}
		>
			<a
				href="/"
				class="flex items-center rounded px-4 py-2 text-xl font-semibold transition-colors hover:bg-blue-600"
			>
				<HomeOutline class="mr-2 h-6 w-6" />
				Home
			</a>
			<ul class="flex space-x-6">
				<!-- Create Dropdown -->
				<li class="relative">
					<button
						class="flex items-center rounded px-4 py-2 transition-colors hover:bg-blue-600"
						data-dropdown-toggle="create-dropdown"
					>
						<a href="/obs"> OBS </a>
					</button>
				</li>
				<!-- Audio Player Dropdown -->
				<li class="relative" in:fade={{ duration: 200 }}>
					<button class="flex items-center rounded px-4 py-2 transition-colors hover:bg-blue-600">
						<a href="/audio_player"> Audio Player </a>
					</button>
				</li>

				<!-- Viz -->
				<li class="relative">
					<button
						class="flex items-center rounded px-4 py-2 transition-colors hover:bg-blue-600"
						data-dropdown-toggle="view-dropdown"
					>
						Viz
						<ChevronDownOutline class="ms-2 h-4 w-4" />
					</button>
					<Dropdown>
						<DropdownItem href="/view-t-data">Viz</DropdownItem>
					</Dropdown>
				</li>

				
			</ul>
		</nav>
	</header>
{/if}

<main class="h-full m-0 p-0 overflow-clip">
	{#if $navigating}
		<div class="w-full h-full" in:fade={{ duration: 150 }} out:fade={{ duration: 150 }}>
			<div class="flex justify-center items-center h-full">
				<div
					class="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"
				></div>
			</div>
		</div>
	{:else}
		<div
			class="w-screen h-[calc(100vh-80px)]"
			in:fade={{ duration: 150 }}
			out:fade={{ duration: 150 }}
		>
			{@render children()}
		</div>
	{/if}
</main>
