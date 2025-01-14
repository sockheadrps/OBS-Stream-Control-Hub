<svelte:options runes={false} />

<script lang="ts">
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import ObsTab from '../components/ObsTab.svelte';
	import { websocketState, connectWebSocket, sendMessage } from '../stores/wsstore';
	import { Card, TabItem, Tabs } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { PUBLIC_OBS_URL } from '$env/static/public';

	let ready = false;

	let tabs = [
		{
			name: 'Obs',
			action: () => console.log('Obs button clicked!')
		}
	];

	onMount(() => {
		ready = true;
		connectWebSocket(PUBLIC_OBS_URL);
	});
</script>

{#if ready}
	<main
		class="p-0 m-0 bg-gray-900 w-screen h-[calc(100vh-80px)] flex justify-center items-center"
		in:fade={{ duration: 300 }}
	>
		<div
			class="w-4/5 card-container h-4/5 px-4 py-0 m-auto flex justify-center items-center border-2 border-gray-700 bg-gray-800 rounded-lg shadow-xl"
		>
			<div class="w-full h-full space-y-6 flex flex-col justify-center items-center">

			</div>
		</div>
	</main>
{/if}

<style>
	.card-container {
		border-radius: 16px;
		box-shadow:
			0 10px 20px rgba(0, 0, 0, 0.25),
			0 6px 6px rgba(0, 0, 0, 0.22);
		color: #ffffff;
		transition: all 0.3s ease-in-out;
	}
</style>
