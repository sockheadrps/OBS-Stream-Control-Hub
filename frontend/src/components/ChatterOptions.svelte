<script lang="ts">
  

  import { chatterOptionsContext, getChatterOptions, chatterOptionsStore, requestUserSettings, userSettings, sendTwitchBotSettings } from '../stores/ws_twitch_bot';
  import { onMount } from 'svelte';

  let isMuted: boolean = false; 
  let messageReplace: string = ''; 
  let ttsLength: number = 255; // Default value

  export let currentOpenChatter: string = '';
  export let chatterOptions: any = undefined;
  let responseUserSettings: any = undefined;

  $: chatterOptions = getChatterOptions(currentOpenChatter);
  $: responseUserSettings = userSettings;

  // Update initial values when userSettings changes
  $: if (responseUserSettings) {
    isMuted = responseUserSettings.is_muted;
    messageReplace = responseUserSettings.message_replace;
    ttsLength = responseUserSettings.tts_length;
  }

  function updateOptionsStore() {
    if (!currentOpenChatter) {
      return;
    }
    console.log(`updating options store for ${currentOpenChatter}, isMuted: ${isMuted}, messageReplace: ${messageReplace}, ttsLength: ${ttsLength}`);
    let settings = {
      name: currentOpenChatter,
      is_muted: isMuted,
      message_replace: messageReplace,
      tts_length: ttsLength
    };
    sendTwitchBotSettings(settings);
    chatterOptionsStore.update(store => ({
      ...store,
      name: currentOpenChatter,
      is_muted: isMuted,
      message_replace: messageReplace,
      tts_length: ttsLength
    }));
  }

  const handleTTSLengthChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    ttsLength = parseInt(target.value);
    updateOptionsStore();
  };

  const handleMessageReplaceChange = (event: Event) => {
    const target = event.target as HTMLInputElement; 
    messageReplace = target.value;
    updateOptionsStore();
  };

  const toggleMute = () => {
    isMuted = !isMuted;
    updateOptionsStore();
  };

  let ready = false;
  onMount(() => {
    requestUserSettings(currentOpenChatter);
    ready = true;
  });

</script>
{#if ready}
<div class="p-4 bg-gray-800 rounded-lg shadow">
  <div class="mb-6">
    <label for="tts-length" class="block mb-2 text-sm font-medium text-gray-300">
      TTS Maximum Length
    </label>
    <input
      type="range"
      id="tts-length"
      min="0"
      max="500"
      value={ttsLength}
      on:change={handleTTSLengthChange}
      class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
    />
    <span class="text-sm text-gray-400 mt-1">{ttsLength} characters</span>
  </div>

  <div class="mb-6">
    <label for="message-replace" class="block mb-2 text-sm font-medium text-gray-300">
      Message Replace
    </label>
    <input
      type="text"
      id="message-replace"
      value={messageReplace}
      on:input={handleMessageReplaceChange}
      class="bg-gray-700 border border-gray-600 text-gray-100 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
      placeholder="Replace message with..."
    />
  </div>

  <div class="flex items-center mb-6">
    <button
      type="button"
      on:click={toggleMute}
      class={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        isMuted ? 'bg-red-600' : 'bg-blue-600'
      }`}
      role="switch"
      aria-checked={isMuted}
      aria-label={isMuted ? 'Unmute TTS' : 'Mute TTS'}
    >
      <span
        class={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
          isMuted ? 'translate-x-5' : 'translate-x-0'
        }`}
      ></span>
    </button>
    <span class="ml-3 text-sm font-medium text-gray-300">
      {isMuted ? 'Unmute TTS' : 'Mute TTS'}
    </span>
  </div>

  <div class="flex justify-center">
    <button
      type="button"
      on:click={() => chatterOptionsContext.store.update(store => ({ ...store, killTTS: true }))}
      class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors duration-200"
    >
      Kill Current TTS
    </button>
  </div>
</div>
{/if}
