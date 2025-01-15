<script lang="ts">
	import { onMount } from 'svelte';
	import {
		twitch_bot_websocketState,
		sendTwitchBotSettings,
		twitch_bot_lastMessage,
		chatterOptionsContext,
		getChatterOptions,
		requestUserSettings
	} from '../stores/ws_twitch_bot';
	import ChatterOptions from './ChatterOptions.svelte';

	let currentOpenChatter: string = '';
	let ttsAllowed: boolean = true;
	let messageReplace: string = '';
	let ttsLength: number = 255;
	let ready: boolean = false;
	let chatters: string[] = [];
	let currentChatter = { chatterName: '' };

	$: console.log(currentOpenChatter, ttsAllowed, messageReplace, ttsLength);

	const handleChatterClick = (chatterName: string) => {
		currentOpenChatter = chatterName;
	};

	const handleChatterMouseover = (chatterName: string) => {
		requestUserSettings(chatterName);
	};

	onMount(() => {
		ready = true;
	});

	$: twitch_bot_lastMessage.subscribe((msg) => {
		if (msg?.event === 'UPDATE') {
			chatters = msg.data.chatter_list || [];
			currentChatter = { chatterName: msg.data.current_chatter || '' };
		}
	});
</script>

{#if ready && chatters.length > 0}
	<div class="flex justify-center items-center h-1/6 bg-inherit m-12">
		<div class="flex flex-wrap gap-4 justify-center items-center p-4">
			{#each chatters as chatter}
				<button
					on:click={() => handleChatterClick(chatter)}
					on:mouseover={() => handleChatterMouseover(chatter)}
					on:focus={() => handleChatterMouseover(chatter)}
					class={`inline-flex items-center justify-center rounded-md w-32 h-14 text-sm font-medium transition-all transform duration-300 ${
						currentChatter.chatterName === chatter ? '' : 'cursor-pointer hover:scale-105'
					}`}
				>
					<span
						class={`font-mono inline-flex items-center justify-center rounded-md bg-black bg-opacity-50 w-full h-full shadow-lg transition-all transform duration-300 ${
							currentChatter.chatterName === chatter
								? 'text-blue-500 shadow-blue-500/50 shadow-2xl scale-110'
								: 'text-gray-500 text-opacity-70 hover:bg-opacity-70 shadow-gray-500/50 hover:text-gray-300 hover:text-opacity-90'
						}`}
					>
						{chatter}
					</span>
				</button>
			{/each}
			{#if currentOpenChatter}
				<ChatterOptions {currentOpenChatter} chatterOptions={getChatterOptions(currentOpenChatter)} />
			{/if}
		</div>
	</div>
{/if}
