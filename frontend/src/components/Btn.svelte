<script lang="ts">
	export let label: string; // Button label
	export let doClick: () => void; // Function to call on click
	export let active: boolean = true; // Whether the button is enabled or not
</script>

<div class="w-full h-full bg-none">
	<ul>
    <li>
      <button
        onclick={doClick}
        class={`inline-flex items-center justify-center rounded-md w-24 h-12 text-sm font-medium transition-transform transform duration-300 ${
          active ? 'cursor-not-allowed' : 'cursor-pointer hover:scale-105 opacity-70'
        }`}
      >
        <span
          class={`font-mono inline-flex items-center justify-center rounded-md bg-black bg-opacity-50 w-full h-full shadow-lg transition-transform transform duration-300 ${
            active
              ? 'text-blue-500 hover:shadow-blue-500/50 hover:bg-opacity-70'
              : 'text-gray-500 hover:shadow-gray-500/50 hover:bg-opacity-70'
          }`}
        >
          {label}
        </span>
      </button>
    </li>
  </ul>
</div>
