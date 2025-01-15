<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { writable, get } from 'svelte/store';
	import { browser } from '$app/environment';
	import bg2 from '$lib/assets/bg2.png';
	import { overlaySettings } from '../../../stores/wsOverlay';

	// Constants
	const TWO_PI = Math.PI * 2;
	const COLLISION_THRESHOLD = 30;
	const MAX_COLLISIONS = 3;
	const EXPLOSION_FORCE = 5;
	const PARTICLE_LOAD_INTERVAL = 100; // ms between loading each particle

	// Store to track whether the canvas is ready
	const ready = writable(false);

	// Variables and constants
	let canvas: HTMLCanvasElement;
	let ctx: CanvasRenderingContext2D;
	let particlesArray: Particle[] = [];
	let myImage: HTMLImageElement;
	let imageData: ImageData;
	let pixels: Uint8ClampedArray;
	let particleLoadInterval: number;
	let currentParticleCount = 0;

	// function to convert 0-360 to some colors
	function colorFromHue(hue: number) {
		if (hue === 0) {
			return 'hsl(0, 0%, 0%)';
		}
		return `hsl(${hue}, 100%, 50%)`;
	}

	// Reactive declarations for settings
	$: particleCount = $overlaySettings?.particleCount;
	$: particleSpeed = $overlaySettings?.particleSpeed;
	$: rotationSpeed = $overlaySettings?.rotationSpeed;
	$: starSpeed = $overlaySettings?.starSpeed;
	$: starSize = $overlaySettings?.starSize;
	$: starOffset = $overlaySettings?.starOffset;
	$: trailLength = $overlaySettings?.trailLength;
	$: wanderStrength = $overlaySettings?.wanderStrength;
	$: collisionForce = $overlaySettings?.collisionForce;
	$: baseSize = $overlaySettings?.baseSize;
	$: baseHue = $overlaySettings?.baseHue;
	$: numberOfStars = $overlaySettings?.numberOfStars;
	$: blackParticles = $overlaySettings?.blackParticles;
	$: blackStars = $overlaySettings?.blackStars;
	$: trailColor = $overlaySettings?.trailColor;

	// Create image only in browser
	if (browser) {
		myImage = new Image();
		myImage.src = bg2;
	}
	let numberOfParticles = 0;

	interface ExplosionParticle {
		x: number;
		y: number;
		z: number;
		speed: number;
		angle: number;
		size: number;
		alpha: number;
		color: string;
		update(): boolean;
		draw(ctx: CanvasRenderingContext2D): void;
	}

	class Particle {
		x!: number;
		y!: number;
		z!: number;
		speed!: number;
		velocity!: number;
		maxSize!: number;
		size!: number;
		position1!: number;
		position2!: number;
		angle!: number;
		rotationSpeed!: number;
		starAngles!: number[];
		starSpeeds!: number[];
		sizeMultiplier!: number;
		growthPhase!: boolean;
		trails!: Array<{ x: number; y: number; z: number; alpha: number; color: string }[]>;
		zSpeed!: number;
		riseSpeed!: number;
		horizontalSpeed!: number;
		hasEscaped!: boolean;
		isExploding!: boolean;
		explosionParticles!: ExplosionParticle[];
		color!: string;
		starColor!: string;
		passedThreshold!: boolean;
		baseHue!: number;
		hueOffset!: number;
		wanderAngle!: number;
		collisionCount!: number;
		isFlashing!: boolean;
		flashDuration!: number;
		directionX!: number;
		directionY!: number;
		trailColor!: string;

		constructor() {
			// Defer initialization until canvas is ready
			if (canvas) {
				this.initializePosition();
				this.initializeMovement();
				this.initializeVisuals();
				this.initializeState();
			}
		}

		private initializePosition() {
			// Only initialize if canvas exists
			if (canvas) {
				this.x = Math.random() * canvas.width;
				this.y = Math.random() * canvas.height;
				this.z = 0;
			} else {
				// Default values if canvas not ready
				this.x = 0;
				this.y = 0;
				this.z = 0;
			}
		}

		private initializeMovement() {
			this.velocity = Math.random() * particleSpeed;
			this.riseSpeed = Math.random() * 1 + 0.2;
			this.horizontalSpeed = (Math.random() - 0.5) * 0.2;
			this.directionX = Math.random() * 2 - 1;
			this.directionY = Math.random() * 2 - 1;
		}

		private initializeVisuals() {
			this.maxSize = Math.random() * 20 + baseSize;
			this.size = this.maxSize;
			this.angle = Math.random() * TWO_PI;
			this.rotationSpeed = Math.random() * rotationSpeed * 2 - rotationSpeed;
			this.starAngles = Array(numberOfStars)
				.fill(0)
				.map(() => Math.random() * TWO_PI);
			this.starSpeeds = Array(numberOfStars)
				.fill(0)
				.map(() => Math.random() * starSpeed * 2 - starSpeed);
			this.baseHue = Math.random() * 60 + baseHue;
			this.color =`hsl(${this.baseHue}, 100%, 50%)`;
			this.starColor =`hsl(${this.baseHue}, 100%, 50%)`;
			this.trailColor = colorFromHue(trailColor);
		}

		private initializeState() {
			this.sizeMultiplier = 1;
			this.growthPhase = true;
			this.trails = Array(numberOfStars)
				.fill(this.trailColor)
				.map(() => []);
			this.hasEscaped = false;
			this.isExploding = false;
			this.explosionParticles = [];
			this.passedThreshold = false;
			this.wanderAngle = Math.random() * TWO_PI;
			this.collisionCount = 0;
			this.isFlashing = false;
			this.flashDuration = 0;
		}

		checkCollisions() {
			for (let i = 0; i < particlesArray.length; i++) {
				const other = particlesArray[i];
				if (other === this) continue;

				const dx = this.x - other.x;
				const dy = this.y - other.y;
				const distance = Math.hypot(dx, dy);

				if (distance < COLLISION_THRESHOLD) {
					this.handleCollision(other, dx, dy, distance);
				}
			}
		}

		private handleCollision(other: Particle, dx: number, dy: number, distance: number) {
			const angle = Math.atan2(dy, dx);
			const newDirX = Math.cos(angle) * collisionForce;
			const newDirY = Math.sin(angle) * collisionForce;

			// Check if the other particle is within the shield created by the trails
			if (this.trails.length > 0) {
				const shieldDistance = this.size * starOffset; // Define the shield distance
				if (distance < shieldDistance) {
					// Bounce off the shield instead of colliding
					this.directionX = -newDirX;
					this.directionY = -newDirY;
					other.directionX = newDirX;
					other.directionY = newDirY;
					return; // Exit to prevent further collision handling
				}
			}

			// Handle normal collision if past the shield
			this.isFlashing = other.isFlashing = true;
			this.flashDuration = other.flashDuration = 10;

			this.collisionCount++;
			other.collisionCount++;

			// Move particles away from each other if they are not destroyed
			if (this.collisionCount < MAX_COLLISIONS && other.collisionCount < MAX_COLLISIONS) {
				const separationDistance = COLLISION_THRESHOLD;
				const overlap = separationDistance - distance;

				// Move particles away from each other
				this.x += (dx / distance) * overlap * 0.5; // Move this particle away
				this.y += (dy / distance) * overlap * 0.5; // Move this particle away
				other.x -= (dx / distance) * overlap * 0.5; // Move the other particle away
				other.y -= (dy / distance) * overlap * 0.5; // Move the other particle away
			}

			if (this.collisionCount >= MAX_COLLISIONS) this.explode();
			if (other.collisionCount >= MAX_COLLISIONS) other.explode();
		}

		wander() {
			this.wanderAngle += (Math.random() - 0.5) * 0.5;
			const wanderX = Math.cos(this.wanderAngle) * 0.1;
			const wanderY = Math.sin(this.wanderAngle) * 0.1;

			this.directionX += wanderX;
			this.directionY += wanderY;

			const magnitude = Math.hypot(this.directionX, this.directionY);
			if (magnitude > 0) {
				this.directionX /= magnitude;
				this.directionY /= magnitude;
			}
		}

		update() {
			if (!canvas) return;

			if (this.isExploding) {
				this.updateExplosion();
				return;
			}

			if (this.isFlashing && --this.flashDuration <= 0) {
				this.isFlashing = false;
			}

			this.wander();
			this.checkCollisions();

			// Update position
			const velocityFactor = this.velocity * 2;
			this.x += this.directionX * velocityFactor;
			this.y += this.directionY * velocityFactor;

			// Update visual effects
			this.angle += this.rotationSpeed;
			if (numberOfStars > 0) {
				this.updateTrails();
			}

			// Check if particle is out of view
			const margin = this.size * 2;
			if (
				this.x < -margin ||
				this.x > canvas.width + margin ||
				this.y < -margin ||
				this.y > canvas.height + margin
			) {
				this.reset();
			}
		}

		private updateExplosion() {
			this.explosionParticles = this.explosionParticles.filter((p) => p.update());
			if (this.explosionParticles.length === 0) {
				this.reset();
			}
		}

		private updateTrails() {
			for (let i = 0; i < numberOfStars; i++) {
				this.trailColor = colorFromHue(trailColor);
				if (!this.trails[i]) {
					this.trails[i] = [];
				}

				this.starAngles[i] += this.starSpeeds[i];

				const angle = this.starAngles[i];
				const offsetX = Math.cos(angle) * (this.size * starOffset);
				const offsetY = Math.sin(angle) * (this.size * starOffset);
				const cos = Math.cos(this.angle);
				const sin = Math.sin(this.angle);

				const trailX = this.x + (offsetX * cos - offsetY * sin);
				const trailY = this.y + (offsetX * sin + offsetY * cos);

				this.trails[i].unshift({
					x: trailX,
					y: trailY,
					z: this.z,
					alpha: 0.5,
					color: trailColor
				});

				if (this.trails[i].length > trailLength) {
					this.trails[i].pop();
				}
			}
		}

		draw() {
			if (!ctx) return;

			if (this.isExploding) {
				this.explosionParticles.forEach((p) => p.draw(ctx));
				return;
			}

			ctx.shadowBlur = this.isFlashing ? 30 : 20;
			ctx.shadowColor = this.isFlashing ? 'white' : this.color;

			// Draw trails
			if (numberOfStars > 0) {
				for (const trail of this.trails) {
					if (trail && trail.length > 1) {
						ctx.beginPath();
						ctx.moveTo(trail[0].x, trail[0].y);

						for (let j = 1; j < trail.length; j++) {
							ctx.lineTo(trail[j].x, trail[j].y);
						}
						const trailStrokeColor = this.isFlashing
							? 'rgba(255, 255, 255, 0.5)'
							: this.trailColor

						ctx.strokeStyle = trailStrokeColor;
						ctx.lineWidth = this.size * starSize;
						ctx.stroke();
					}
				}
			}

			// Draw main particle
			ctx.save();
			ctx.translate(this.x, this.y);
			ctx.rotate(this.angle);

			const fillStyle = this.isFlashing ? 'white' : this.color;
			ctx.fillStyle = fillStyle;

			ctx.beginPath();
			ctx.arc(0, 0, this.size, 0, TWO_PI);
			ctx.fill();

			// Draw orbiting particles
			if (numberOfStars > 0) {
				ctx.fillStyle = this.isFlashing ? 'white' : this.starColor;
				for (let i = 0; i < numberOfStars; i++) {
					const offsetX = Math.cos(this.starAngles[i]) * (this.size * starOffset);
					const offsetY = Math.sin(this.starAngles[i]) * (this.size * starOffset);

					ctx.beginPath();
					ctx.arc(offsetX, offsetY, this.size * starSize, 0, TWO_PI);
					ctx.fill();
				}
			}

			ctx.restore();
		}

		explode() {
			this.isExploding = true;
			const numExplosions = 20;
			const angleStep = TWO_PI / numExplosions;

			for (let i = 0; i < numExplosions; i++) {
				const angle = angleStep * i;
				const speed = Math.random() * EXPLOSION_FORCE + 2;

				this.explosionParticles.push({
					x: this.x,
					y: this.y,
					z: this.z,
					speed,
					angle,
					size: Math.random() * 5 + 2,
					alpha: 1,
					color: this.isFlashing ? 'white' : this.color,
					update() {
						this.x += Math.cos(this.angle) * this.speed;
						this.y += Math.sin(this.angle) * this.speed;
						this.alpha *= 0.95;
						this.size *= 0.97;
						return this.alpha > 0.1;
					},
					draw(ctx: CanvasRenderingContext2D) {
						ctx.save();
						ctx.globalAlpha = this.alpha;
						ctx.fillStyle = this.color;
						ctx.shadowBlur = 20;
						ctx.shadowColor = this.color;
						ctx.beginPath();
						ctx.arc(this.x, this.y, this.size, 0, TWO_PI);
						ctx.fill();
						ctx.restore();
					}
				});
			}
		}

		reset() {
			if (canvas) {
				this.initializePosition();
				this.initializeMovement();
				this.size = this.maxSize;
				this.initializeState();
			}
		}
	}

	function init() {
		particlesArray = [];
		currentParticleCount = 0;
		
		// Clear any existing interval
		if (particleLoadInterval) {
			clearInterval(particleLoadInterval);
		}

		// Start loading particles gradually
		particleLoadInterval = setInterval(() => {
			if (currentParticleCount < particleCount) {
				particlesArray.push(new Particle());
				currentParticleCount++;
			} else {
				clearInterval(particleLoadInterval);
			}
		}, PARTICLE_LOAD_INTERVAL);
	}

	function animate() {
		if (!ctx || !canvas || !particlesArray) return;

		ctx.clearRect(0, 0, canvas.width, canvas.height);
		ctx.drawImage(myImage, 0, 0, canvas.width, canvas.height);

		imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
		pixels = imageData.data;

		for (const particle of particlesArray) {
			if (particle) {
				particle.update();
				particle.draw();
			}
		}

		requestAnimationFrame(animate);
	}

	function updateParticles() {
		if (canvas && ctx) {
			numberOfParticles = particleCount;
			init();
		}
	}

	$: {
		if (particlesArray && particlesArray.length > 0) {
			particlesArray.forEach((particle) => {
				if (particle) {
					particle.velocity = Math.random() * particleSpeed;
					particle.rotationSpeed = Math.random() * rotationSpeed * 2 - rotationSpeed;
					particle.starSpeeds = Array(numberOfStars)
						.fill(0)
						.map(() => Math.random() * starSpeed * 2 - starSpeed);
					particle.maxSize = Math.random() * 20 + baseSize;
					particle.size = particle.maxSize;
					particle.baseHue = Math.random() * 60 + baseHue;
					particle.color = blackParticles ? 'black' : `hsl(${particle.baseHue}, 100%, 50%)`;
					particle.starColor = blackStars ? 'black' : `hsl(${particle.baseHue}, 100%, 50%)`;
				}
			});
		}
	}

	$: if (particleCount !== numberOfParticles) {
		updateParticles();
	}

	function clearParticles() {
		if (particleLoadInterval) {
			clearInterval(particleLoadInterval);
		}
		particlesArray = [];
		currentParticleCount = 0;
		init();
	}

	let load_ready = false;
	onMount(() => {
		const loadImage = () =>
			new Promise((resolve) => {
				if (myImage) {
					myImage.onload = resolve;
				}
			});

		loadImage().then(() => {
			if (!canvas) return;
			const context = canvas.getContext('2d', { willReadFrequently: true });
			if (!context) return;

			ctx = context;
			canvas.width = myImage.width;
			canvas.height = myImage.height;

			ctx.drawImage(myImage, 0, 0, canvas.width, canvas.height);
			imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
			pixels = imageData.data;

			init();
			ready.set(true);
			animate();
		});
		load_ready = true;

		return () => {
			if (particleLoadInterval) {
				clearInterval(particleLoadInterval);
			}
			particlesArray = [];
		};
	});
</script>

{#if load_ready}
	<div class="container">
		<canvas bind:this={canvas}></canvas>
	</div>
{/if}

<style>
	.container {
		position: relative;
		width: 100vw;
		height: 100vh;
	}

	canvas {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 1920px;
		height: 1080px;
	}
</style>
