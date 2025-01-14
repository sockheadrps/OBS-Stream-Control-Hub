<script lang="ts">
	import { Button, Card, Label, Range, Toggle } from 'flowbite-svelte';
	import { onDestroy, onMount } from 'svelte';
	import { page } from '$app/state';

	import { sendMessage, socketStore } from '../../stores/ws_audio_player';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	let socket: WebSocket | null = null;
	let latestMessage: any = null;

	let fadeIn1Active = false;
	let fadeOut1Active = false;
	let isPlaying1 = false;
	let skipActive1 = false;
	let ready = false;

	let channel1Title = 'No track playing';
	let channel1Artist = 'No artist';
	let channel1Position = '0:00';
	let channel1Queue: Array<string> = [];
	let autoPlayActive1 = false;

	let reloadOnFinish = false;
	let initialLoad = true;

	// Reactive subscription to the store
	$: {
		$socketStore;
		if ($socketStore) {
			socket = $socketStore.socket;
			latestMessage = $socketStore.latestMessage;
		}
	}

	$: {
		handleMessage(latestMessage);
	}

	async function getAudioFiles() {
		try {
			const response = await fetch(`${PUBLIC_BACKEND_URL}/music`);
			const data = await response.json();
			return data;
		} catch (error) {
			console.error('Failed to fetch audio files:', error);
			return { event: '', data: [] };
		}
	}

	onMount(() => {
		console.log('Mounting audio player');

		try {
			getAudioFiles()
				.then((data) => {
					channel1Queue = data.data;
				})
				.catch((error) => {
					console.error('Failed to initialize audio player:', error);
				});
		} catch (error) {
			console.error('Failed to initialize audio player:', error);
		}

		ready = true;
	});

	onDestroy(() => {
		console.log('Destroying audio player');
		if (socket) {
			socket.send(
				JSON.stringify({
					event: 'player_hidden',
					type: 'player_hidden',
					value: true
				})
			);
		}
	});

	function handleVolume(value: number) {
		if (socket) {
			socket.send(
				JSON.stringify({
					event: 'audio_control',
					type: 'volume',
					data: {
						value,
						channel: `channel-1`
					}
				})
			);
		} else {
			console.error('WebSocket is not connected');
		}
	}

	function handleAutoPlay() {
		console.log('Auto play');
		autoPlayActive1 = !autoPlayActive1;
		if (autoPlayActive1) {
			isPlaying1 = true;
		}

		if (socket) {
			console.log('Sending auto play');
			socket.send(
				JSON.stringify({
					event: 'audio_control',
					data: 'auto_play',
					value: autoPlayActive1
				})
			);
		}
	}

	function handlePlayPause() {
		if (socket) {
			socket.send(
				JSON.stringify({
					event: 'audio_control',
					data: isPlaying1 ? 'pause' : 'play'
				})
			);
		}
	}

	function handleSkip() {
		if (autoPlayActive1 && !isPlaying1) {
			isPlaying1 = true;
		}
		if (socket) {
			socket.send(
				JSON.stringify({
					event: 'audio_control',
					data: 'skip'
				})
			);
		}
	}

	function handleFadeEffect(effect: string, state: boolean) {
		if (socket) {
			socket.send(
				JSON.stringify({
					event: 'effects',
					data: {
						effect,
						state
					}
				})
			);
		}
	}

	function handleReloadOnFinish() {
		reloadOnFinish = !reloadOnFinish;
		if (socket) {
			socket.send(
				JSON.stringify({
					event: 'audio_control',
					data: 'reload_on_finish',
					value: reloadOnFinish
				})
			);
		}
	}

	function handleMessage(message: any) {
		// console.log('Processing message:', message);

		// Channel 1 Handling
		if (message?.data) {
			if (message.data.current_audio) {
				const ch1 = message.data.current_audio;
				channel1Title = message.data.current_audio.title;
				channel1Artist = message.data.current_audio.artist;
				channel1Position = message.data.current_audio.position || '0:00';
			}

			if (message.data.queue) {
				channel1Queue = message.data.queue;
			}
		}
		if (message?.data?.event_type === 'info_request') {
			let data = message?.data?.data;
			if (data) {
				channel1Title = data?.current_audio?.title || 'No track playing';
				channel1Artist = data?.current_audio?.artist || 'No artist';
				channel1Position = data?.current_audio?.position || '0:00';
				channel1Queue = data?.queue || [];
				autoPlayActive1 = !!data?.auto_play;
				reloadOnFinish = !!data?.reload_on_finish;
				fadeIn1Active = data?.effects?.includes('FadeIn') || false;
				fadeOut1Active = data?.effects?.includes('FadeOut') || false;
				isPlaying1 = !!data?.is_playing;
				let vol_elem = document.getElementById('volume1') as HTMLInputElement;
				if (vol_elem && data?.volume !== undefined) {
					vol_elem.value = data.volume;
				}
			}
		}
	}

	$: (async () => {
		if (initialLoad) {
			let socket = $socketStore.socket;
			while (!initialLoad && ready && socket?.readyState === WebSocket.OPEN) {
				await new Promise((resolve) => setTimeout(resolve, 100));
			}
			initialLoad = false;
			if (socket) {
				sendMessage(socket, {
					event: 'info_request',
					type: 'info_request'
				});
			}
		}
	})();
</script>

{#if ready}
	<main class="flex justify-evenly items-center h-screen bg-slate-900 overflow-hidden">
		<div class="flex flex-row justify-center h-5/6 mb-12 gap-8 w-full overflow-hidden">
			<div
				class="bg-slate-800 shadow-lg rounded-2xl p-10 min-w-[30%] max-w-[40%] border-2 border-slate-700 shadow-slate-950 overflow-hidden"
			>
				<!-- Volume Slider -->
				<div class="flex flex-col items-center mb-8">
					<Label
						for="volume1"
						class="mb-2 text-sm text-gray-400 font-semibold uppercase tracking-wider">Volume</Label
					>
					<Range
						id="volume1"
						min={0}
						max={1}
						step={0.05}
						value={0.5}
						class="accent-blue-500 rounded-lg w-full"
						on:change={(e) => {
							const target = e.target as HTMLInputElement;
							handleVolume(parseFloat(target.value));
						}}
					/>
				</div>

				<!-- Effects Section -->
				<div class="mb-4">
					<div class="flex justify-center gap-2">
						<button
							id="fadeIn1"
							class={`bg-gray-900 px-4 py-2 rounded-md transform-active:scale-95 truncate
							${
								fadeIn1Active
									? 'shadow-inner shadow-blue-500 text-blue-400 opacity-100 scale-[1.02] border-b-2 border-l-2 quint-in-out duration-200 border-blue-500'
									: 'text-gray-400 opacity-80 border-b-2 border-l-2 border-black'
							} transition-colors duration-300 ease-in-out hover:bg-gray-900/80`}
							on:click={() => {
								fadeIn1Active = !fadeIn1Active;
								handleFadeEffect('fade_in', fadeIn1Active);
							}}
							aria-pressed={fadeIn1Active}
							title="Toggle Fade In Effect"
						>
							Fade In
						</button>
						<button
							id="fadeOut1"
							class={`bg-gray-900 px-4 py-2 rounded-md transform-active:scale-95 truncate
							${
								fadeOut1Active
									? 'shadow-inner shadow-red-500 text-red-400 opacity-100 scale-[1.02] border-b-2 border-l-2 quint-in-out duration-200 border-red-500'
									: 'text-gray-400 opacity-80 border-b-2 border-l-2 border-black'
							} transition-colors duration-300 ease-in-out hover:bg-gray-900/80`}
							on:click={() => {
								fadeOut1Active = !fadeOut1Active;
								handleFadeEffect('fade_out', fadeOut1Active);
							}}
							aria-pressed={fadeOut1Active}
							title="Toggle Fade Out Effect"
						>
							Fade Out
						</button>
					</div>
				</div>

				<!-- Controls Section -->
				<div class="flex justify-center gap-2 mb-4">
					<button
						id="auto-play-1"
						class={`bg-gray-900 px-4 py-2 rounded-md transform-active:scale-95 truncate
						${
							autoPlayActive1
								? 'shadow-inner shadow-purple-500 text-purple-400 opacity-100 scale-[1.02] border-b-2 border-l-2 quint-in-out duration-200 border-purple-500'
								: 'text-gray-400 opacity-80 border-b-2 border-l-2 border-black'
						} transition-colors duration-300 ease-in-out hover:bg-gray-900/80`}
						on:click={() => {
							handleAutoPlay();
						}}
						aria-pressed={autoPlayActive1}
					>
						Auto Play
					</button>
					<button
						id="play-btn-1"
						class={`bg-gray-900 px-4 py-2 rounded-md transform-active:scale-95 truncate
						${
							isPlaying1
								? 'shadow-inner shadow-yellow-500 text-yellow-400 opacity-100 scale-[1.02] border-b-2 border-l-2 quint-in-out duration-200 border-yellow-500'
								: 'text-green-400 opacity-100 scale-[1.02] border-b-2 border-l-2 quint-in-out duration-200 border-green-500'
						} transition-colors duration-300 ease-in-out hover:bg-gray-900/80`}
						on:click={() => {
							handlePlayPause();
							isPlaying1 = !isPlaying1;
						}}
					>
						{isPlaying1 ? 'Pause' : 'Play'}
					</button>
					<button
						id="skip-btn-1"
						class={`bg-gray-900 px-4 py-2 rounded-md transform-active:scale-95 truncate
						${
							skipActive1
								? 'shadow-inner shadow-yellow-500 text-yellow-400 opacity-100 scale-[1.02] border-b-2 border-l-2 quint-in-out duration-200 border-yellow-500'
								: 'text-gray-400 opacity-80 border-b-2 border-l-2 border-black'
						} transition-colors duration-300 ease-in-out hover:bg-gray-900/80`}
						on:click={() => handleSkip()}
					>
						Skip
					</button>
				</div>

				<!-- Audio Info Section -->
				<div class="flex flex-col overflow-hidden">
					<div
						class="bg-gray-900 border-2 border-gray-700 rounded-lg px-6 py-7 shadow-inner shadow-gray-950 mb-4 flex flex-col gap-4 overflow-hidden"
					>
						<!-- Title Row -->
						<div class="flex items-center justify-between">
							<div class="text-gray-500 text-sm uppercase tracking-wide font-semibold opacity-70">
								Title
							</div>
							<div class="text-blue-400 text-lg font-bold tracking-wide truncate">
								{channel1Title}
							</div>
						</div>
						<!-- Artist Row -->
						<div class="flex items-center justify-between">
							<div class="text-gray-500 text-sm uppercase tracking-wide font-semibold opacity-70">
								Artist
							</div>
							<div class="text-green-400 text-lg font-bold tracking-wide truncate">
								{channel1Artist}
							</div>
						</div>
						<!-- Time Row -->
						<div class="flex justify-end">
							<span class="text-sm text-gray-400 font-mono">{channel1Position}</span>
						</div>
					</div>

					<!-- Queue Section -->
					<div class="flex-1 overflow-hidden">
						<div
							class="bg-gray-900 border-2 border-gray-700 rounded-lg min-h-[300px] max-h-[270px] flex flex-col overflow-y-auto shadow-inner shadow-gray-950"
						>
							<!-- Queue Header -->
							<span
								class="block px-6 py-2 text-xs text-slate-500 font-semibold uppercase tracking-wider border-b border-gray-800 sticky top-0 bg-gray-900 z-10"
							>
								Queue
							</span>
							<!-- Queue Items -->
							{#each channel1Queue as item}
								<div
									class="px-6 py-3 hover:bg-gray-800/50 transition duration-200 ease-in-out truncate"
								>
									<span
										class="text-gray-400/80 font-medium text-sm tracking-wide font-mono truncate"
									>
										{item.title ? item.title : item}
									</span>
								</div>
							{/each}
						</div>
					</div>
				</div>
				<div class="flex justify-end items-center mt-4">
					<span class="text-gray-600 text-sm font-mono mr-2 mb-0">Reload on finish</span>
					<Toggle
						color="teal"
						checked={reloadOnFinish}
						on:change={() => {
							handleReloadOnFinish();
						}}
					></Toggle>
				</div>
			</div>
		</div>
	</main>
{/if}
