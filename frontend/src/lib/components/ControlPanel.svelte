<script lang="ts">
	import { sendSettings } from '../../stores/controlPanelStore';

	interface ControlPanelSettings {
		particleCount: number;
		particleSpeed: number;
		baseSize: number;
		baseHue: number;
		numberOfStars: number;
		blackParticles: boolean;
		blackStars: boolean;
		trailLength: number;
		rotationSpeed: number;
		starSpeed: number;
		starSize: number;
		starOffset: number;
		wanderStrength: number;
		collisionForce: number;
		trailColor: number;
	}

	const defaultSettings: ControlPanelSettings = {
		particleCount: 50,
		particleSpeed: 0.8,
		baseSize: 15,
		baseHue: 180,
		numberOfStars: 3,
		blackParticles: false,
		blackStars: false,
		trailLength: 5,
		rotationSpeed: 0.03,
		starSpeed: 0.02,
		starSize: 0.2,
		starOffset: 1.02,
		wanderStrength: 0.1,
		collisionForce: 0.5,
		trailColor: 180
	};

	export let onClear: () => void = () => {};

	let compSettings: ControlPanelSettings = defaultSettings;
	console.log(compSettings);

	function updateStore<T extends keyof ControlPanelSettings>(key: T, value: ControlPanelSettings[T]) {
		compSettings[key] = value;
		sendSettings(compSettings);
	}
	$: console.log(compSettings);
</script>

<div class="control-panel">
	<!-- particle count -->
	<div class="control-group">
		<label>
			Particle Count:
			<input
				type="range"
				value={compSettings.particleCount}
				min="1"
				max="100"
				step="1"
				on:change={(e) => updateStore('particleCount', parseInt(e.currentTarget.value))}
			/>
			<span>{compSettings.particleCount}</span>
		</label>
	</div>

	<!-- particle speed -->
	<div class="control-group">
		<label>
			Particle Speed:
			<input
				type="range"
				value={compSettings.particleSpeed}
				min="0.1"
				max="3.0"
				step="0.1"
				on:change={(e) => updateStore('particleSpeed', parseFloat(e.currentTarget.value))}
			/>
			<span>{compSettings.particleSpeed}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			Base Size:
			<input
				type="range"
				value={compSettings.baseSize}
				min="5"
				max="30"
				step="1"
				on:change={(e) => {
					updateStore('baseSize', parseInt(e.currentTarget.value));
					onClear();
				}}
			/>
			<span>{compSettings.baseSize}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			Base Hue:
			<input
				type="range"
				value={compSettings.baseHue}
				min="0"
				max="360"
				step="1"
				on:change={(e) => {
					updateStore('baseHue', parseInt(e.currentTarget.value));
					onClear();
				}}
			/>
			<span>{compSettings.baseHue}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			Number of Stars:
			<input
				type="range"
				value={compSettings.numberOfStars}
				min="0"
				max="5"
				step="1"
				on:change={(e) => {
					updateStore('numberOfStars', parseInt(e.currentTarget.value));
					onClear();
				}}
			/>
			<span>{compSettings.numberOfStars}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			<input
				type="checkbox"
				checked={compSettings.blackParticles}
				on:change={(e) => {
					updateStore('blackParticles', e.currentTarget.checked);
					onClear();
				}}
			/>
			Black Particles
		</label>
	</div>

	<div class="control-group">
		<label>
			<input
				type="checkbox"
				checked={compSettings.blackStars}
				on:change={(e) => {
					updateStore('blackStars', e.currentTarget.checked);
					onClear();
				}}
			/>
			Black Stars
		</label>
	</div>

	<div class="control-group">
		<label>
			Trail Length:
			<input
				type="range"
				value={compSettings.trailLength}
				min="1"
				max="20"
				step="1"
				on:change={(e) => updateStore('trailLength', parseInt(e.currentTarget.value))}
			/>
			<span>{compSettings.trailLength}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			Trail Color:
			<input
				type="range"
				value={compSettings.trailColor}
				min="0"
				max="360"
				step="1"
				on:change={(e) => updateStore('trailColor', parseInt(e.currentTarget.value))}
			/>
			<span>{compSettings.trailColor}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			Rotation Speed:
			<input
				type="range"
				value={compSettings.rotationSpeed}
				min="0.01"
				max="0.1"
				step="0.01"
				on:change={(e) => updateStore('rotationSpeed', parseFloat(e.currentTarget.value))}
			/>
			<span>{compSettings.rotationSpeed}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			Star Speed:
			<input
				type="range"
				value={compSettings.starSpeed}
				min="0.01"
				max="0.1"
				step="0.01"
				on:change={(e) => updateStore('starSpeed', parseFloat(e.currentTarget.value))}
			/>
			<span>{compSettings.starSpeed}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			Star Size:
			<input
				type="range"
				value={compSettings.starSize}
				min="0.1"
				max="0.5"
				step="0.05"
				on:change={(e) => updateStore('starSize', parseFloat(e.currentTarget.value))}
			/>
			<span>{compSettings.starSize}</span>
		</label>
	</div>

	<div class="control-group">
		<label>
			Star Offset:
			<input
				type="range"
				value={compSettings.starOffset}
				min="1"
				max="2"
				step="0.1"
				on:change={(e) => updateStore('starOffset', parseFloat(e.currentTarget.value))}
			/>
			<span>{compSettings.starOffset}</span>
		</label>
	</div>

	<div class="control-group">
		<button class="clear-button" on:click={onClear}> Clear Particles </button>
	</div>
</div>

<style>
	.control-panel {
		position: fixed;
		top: 20px;
		right: 20px;
		background: rgba(0, 0, 0, 0.8);
		padding: 20px;
		border-radius: 10px;
		color: white;
		z-index: 1000;
	}

	.control-group {
		margin-bottom: 15px;
	}

	label {
		display: flex;
		align-items: center;
		gap: 10px;
		font-size: 14px;
	}

	input[type='range'] {
		width: 150px;
	}

	span {
		min-width: 30px;
		text-align: right;
	}

	.clear-button {
		background: #ff3e3e;
		color: white;
		border: none;
		padding: 8px 16px;
		border-radius: 5px;
		cursor: pointer;
		transition: background 0.2s;
	}

	.clear-button:hover {
		background: #ff1f1f;
	}
</style>
