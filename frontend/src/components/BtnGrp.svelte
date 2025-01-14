<script lang="ts">
	import type { Component } from "svelte";

	interface Btn {
		name: string;
		action: () => void;
		icon?: Component;
	}

	export type { Btn };
  export let btns: Btn[];

</script>

<div class="flex gap-6">
  {#each btns as btn}
    <button
      class="inline-flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-transform transform duration-300 bg-gray-900 text-white shadow-md shadow-blue-500/20 hover:shadow-blue-500/80 hover:scale-110 hover:bg-black"
      on:click={btn.action}
    >
      {#if btn.icon}
        <btn.icon class="w-4 h-4 me-2" />
      {/if}
      {btn.name}
    </button>
  {/each}
</div>
