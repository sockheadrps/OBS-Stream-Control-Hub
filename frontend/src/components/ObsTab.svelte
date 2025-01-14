<script lang="ts">
	import { onMount } from 'svelte';
	import { websocketState, sendMessage, lastMessage } from '../stores/wsstore';

	let ready: boolean = false;

	let scenes: {
		sceneName: string;
		sceneId: string;
	}[] = [];

	let currentScene: {
		currentScene: string;
		transitioning: boolean;
	} = {
		currentScene: '',
		transitioning: false
	};

	const handleSceneChange = (sceneName: string, sceneId: string) => {
		currentScene = {
			currentScene: sceneName,
			transitioning: true
		};
		sendMessage({
			op: 6,
			d: {
				requestType: 'SetCurrentProgramScene',
				requestId: '1',
				requestData: {
					sceneName: sceneName,
					sceneUuid: sceneId
				}
			}
		});
	};

	const getScenes = () => {
		const req = {
			op: 6,
			d: {
				requestType: 'GetSceneList',
				requestId: '1'
			}
		};
		sendMessage(req);
	};

	const getCurrentScene = () => {
		const req = {
			op: 6,
			d: {
				requestType: 'GetCurrentProgramScene',
				requestId: '1'
			}
		};
		sendMessage(req);
	};

	onMount(() => {
		getScenes();
		getCurrentScene();
		ready = true;
	});

	$: lastMessage.subscribe((msg) => {
		if (msg.d.requestType === 'GetSceneList') {
			scenes = msg.d.responseData.scenes.map((scene: any) => ({
				sceneName: scene.sceneName,
				sceneId: scene.sceneUuid
			}));
		}
		if (msg.d.requestType === 'GetCurrentProgramScene') {
			currentScene = {
				currentScene: msg.d.responseData.currentProgramSceneName,
				transitioning: false
			};
		}
		if (msg.d.eventType === 'CurrentProgramSceneChanged') {
			currentScene = {
				currentScene: msg.d.eventData.sceneName,
				transitioning: false
			};
		}
	});
</script>
{#if ready && currentScene.currentScene}
	<div class="flex justify-center items-center h-1/6 bg-inherit m-12">
		<div class="flex flex-wrap gap-4 justify-center items-center p-4">
			{#each scenes as scene}
				<button
					on:click={() => handleSceneChange(scene.sceneName, scene.sceneId)}
					class={`inline-flex items-center justify-center rounded-md w-32 h-14 text-sm font-medium transition-all transform duration-300 ${
						currentScene.transitioning ? 'cursor-not-allowed' : 'cursor-pointer hover:scale-105'
					}`}
				>
					<span
						class={`font-mono inline-flex items-center justify-center rounded-md bg-black bg-opacity-50 w-full h-full shadow-lg transition-all transform duration-300 ${
							currentScene.transitioning
								? scene.sceneName === currentScene.currentScene
									? 'text-orange-500 shadow-orange-500/50 shadow-2xl scale-110'
									: 'text-gray-500 text-opacity-70'
								: scene.sceneName === currentScene.currentScene
								? 'text-blue-500 shadow-blue-500/50 shadow-xl bg-opacity-75 text-opacity-100 hover:shadow-blue-500/50 hover:bg-opacity-100 hover:text-blue-400'
								: 'text-gray-500 text-opacity-70 hover:bg-opacity-70 shadow-gray-500/50 hover:text-gray-300 hover:text-opacity-90'
						}`}
					>
						{scene.sceneName}
					</span>
				</button>
			{/each}
		</div>
	</div>
{/if}
