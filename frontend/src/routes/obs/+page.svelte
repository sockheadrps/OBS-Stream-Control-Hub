<svelte:options runes={false} />

<script lang="ts">
	import { PUBLIC_BACKEND_URL, PUBLIC_OBS_URL } from '$env/static/public';
	import ObsTab from '../../components/ObsTab.svelte';
	import TwitchBotTab from '../../components/TwitchBotTab.svelte';
	import { websocketState, connectWebSocket, sendMessage } from '../../stores/wsstore';
	import { Card, TabItem, Tabs } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import ControlPanel from '$lib/components/ControlPanel.svelte';



	let serverUrl = PUBLIC_BACKEND_URL;
	let ready = false;

	let tabs = [
		{
			name: 'Obs',
			action: () => console.log('Obs button clicked!')
		},
		{
			name: 'Control Panel',
			action: () => console.log('Control Panel button clicked!')
		},
		{
			name: 'Twitch Bot',
			action: () => console.log('Twitch Bot button clicked!')
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
				<div
					class="w-5/6 h-5/6 rounded-lg bg-gray-900 flex flex-col shadow-lg"
					in:fade={{ duration: 300, delay: 600 }}
				>
					<Tabs
						defaultClass="flex border-b border-gray-700"
						activeClasses="text-white bg-gray-800 border-b-2 border-blue-500"
						inactiveClasses="text-gray-400 hover:text-gray-200 hover:bg-gray-700"
						contentClass="p-6"
					>
						{#each tabs as tab}
							<TabItem title={tab.name} class="w-1/4 text-center py-2">
								<div class="w-full h-full p-4 bg-gray-900 rounded-lg">
									{#if tab.name === 'Obs'}
										<ObsTab />
									{:else if tab.name === 'Control Panel'}
										<ControlPanel />
									{:else if tab.name === 'Twitch Bot'}
										<TwitchBotTab />
									{/if}
								</div>
							</TabItem>
						{/each}
					</Tabs>
				</div>
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
