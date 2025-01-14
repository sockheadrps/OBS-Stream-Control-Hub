<script lang="ts">
	import { onMount } from 'svelte';
	import SensorData from '../../components/SensorData.svelte';

	interface SensorReading {
		id: number;
		temperature: number;
		humidity: number;
		altitude: number;
		pressure: number;
		timestamp: string;
	}

	let ready = false;
	let data: SensorReading[] = [];
	let updateInterval: number;

	// Fetch data from the server
	async function read_data() {
		try {
			const response = await fetch('http://192.168.1.130:8123/data');
			data = await response.json();
			console.log('Fetched Data:', data);
		} catch (error) {
			console.error('Error fetching data:', error);
		} finally {
			ready = true;
		}
	}

	// Lifecycle hook to fetch data on component mount and start interval
	onMount(() => {
		read_data();
		
		// Update data every minute (60000 milliseconds)
		updateInterval = setInterval(read_data, 60000);

		// Cleanup interval on component destruction
		return () => {
			clearInterval(updateInterval);
		};
	});

	$: currentTemp = data.length ? ((data[data.length - 1].temperature * 9/5) + 32).toFixed(1) : '--';
	$: currentHumidity = data.length ? data[data.length - 1].humidity.toFixed(1) : '--';
</script>

{#if ready}
	<div class="grid grid-cols-2 gap-4 p-4 opacity-75">
		<div class="bg-gray-800 rounded-lg shadow-lg p-8">
			<div class="text-3xl font-bold text-gray-100 mb-4 text-center">
				{currentTemp}°F
			</div>
			<SensorData title="Temperature Data" data={data} yAxisTitle="Temperature (°F)" />
		</div>
		<div class="bg-gray-800 rounded-lg shadow-lg p-8">
			<div class="text-3xl font-bold text-gray-100 mb-4 text-center">
				{currentHumidity}%
			</div>
			<SensorData title="Humidity Data" data={data} yAxisTitle="Humidity (%)" />
		</div>
	</div>
{:else}
	<p>Loading data...</p>
{/if}
