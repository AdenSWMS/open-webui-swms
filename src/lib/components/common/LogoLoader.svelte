<script lang="ts">
	import { onMount } from 'svelte';

	// State als Prop: 'idle' | 'thinking' | 'writing' | 'done'
	export let state: 'idle' | 'thinking' | 'writing' | 'done' = 'idle';
	export let size: 'small' | 'big' = 'small';

	const LONG =
		'm94.67434,158.15779c-4.46524,5.92437 -5.50802,15.22097 -1.20003,22.41047c4.30799,7.1895 30.86038,36.38897 35.19651,41.59065c46.06485,-73.32024 75.44803,-107.53623 84.51568,-129.5877c9.06764,-22.05146 -2.11075,-29.11213 -6.09571,-32.0368c-3.98496,-2.92466 -22.5769,-6.93675 -33.81339,7.10871l-78.60306,90.51467z';
	const SHORT =
		'm128.56881,221.67816c0,0 44.86486,54.32432 50,58.64865c5.13514,4.32432 16.75676,12.97297 29.72973,1.89189c12.97297,-11.08108 6.48649,-22.97297 6.48649,-22.97297c0,0 -52.10811,-86.7027 -52.81081,-87.13513c-0.7027,-0.43243 -33.40541,49.56757 -33.40541,49.56757z';

	let markEl: HTMLDivElement;
	let prevState = state;
	const running: Animation[] = [];

	const angleOf = (el: Element) => {
		const t = getComputedStyle(el).transform;
		if (!t || t === 'none') return 0;
		const m = new DOMMatrixReadOnly(t);
		return ((Math.atan2(m.b, m.a) * 180) / Math.PI + 360) % 360;
	};

	// Reagiert auf Änderungen von `state` (Svelte Reactive Statement)
	$: if (markEl && state !== prevState) {
		handleStateChange(state);
		prevState = state;
	}

	function handleStateChange(nextState: string) {
		const logos = [...markEl.querySelectorAll<HTMLElement>('.logo')];
		const halves = [...markEl.querySelectorAll<HTMLElement>('.half')];
		const arms = [...markEl.querySelectorAll<HTMLElement>('.arm')];

		const RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		const EASE_OUT = 'cubic-bezier(.2,.8,.2,1)';
		const EASE_BACK = 'cubic-bezier(.34,1.45,.5,1)';

		// 1. Lage einfrieren
		const snap = {
			logos: logos.map(angleOf),
			halves: halves.map((h) => {
				const t = getComputedStyle(h).transform;
				return t === 'none' ? 'translate(0px,0px)' : t;
			}),
			arms: arms.map((a) => getComputedStyle(a).opacity)
		};

		running.splice(0).forEach((a) => a.cancel());

		// 2. Weicher Übergang
		const done = nextState === 'done';

		logos.forEach((el, i) => {
			const from = snap.logos[i];
			const rest = from % 180;
			let to: number;

			if (done) to = Math.ceil((from + 30) / 180) * 180;
			else if (rest > 0.5 && rest < 179.5) to = Math.ceil(from / 180) * 180;
			else return;

			running.push(
				el.animate([{ transform: `rotate(${from}deg)` }, { transform: `rotate(${to}deg)` }], {
					duration: RM ? 0 : done ? 900 : 500,
					easing: done ? EASE_BACK : EASE_OUT
				})
			);
		});

		halves.forEach((el, i) => {
			running.push(
				el.animate([{ transform: snap.halves[i] }, { transform: 'translate(0px,0px)' }], {
					duration: RM ? 0 : done ? 700 : 500,
					easing: done ? EASE_BACK : EASE_OUT
				})
			);
		});

		arms.forEach((el, i) => {
			running.push(
				el.animate([{ opacity: snap.arms[i] }, { opacity: '1' }], {
					duration: RM ? 0 : 400,
					easing: EASE_OUT
				})
			);
		});
	}
</script>

<div class="mark" class:big={size === 'big'} data-state={state} bind:this={markEl}>
	<svg viewBox="0 0 360 360" aria-hidden="true">
		<g transform="translate(180 180)">
			<circle class="ripple" r="150" />
			<g class="logo">
				<g class="half a">
					<g transform="translate(-216.35 -229.16)">
						<path class="arm long" d={LONG} />
						<path class="arm short" d={SHORT} />
					</g>
				</g>
				<g class="half b">
					<g transform="rotate(180)">
						<g transform="translate(-216.35 -229.16)">
							<path class="arm long" d={LONG} />
							<path class="arm short" d={SHORT} />
						</g>
					</g>
				</g>
			</g>
		</g>
	</svg>
</div>

<style>
	:root {
		--c1: #2bb7ec;
		--c2: #07abea;
	}

	.mark {
		width: 30px;
		height: 30px;
		flex: none;
	}
	.mark.big {
		width: 45px;
		height: 45px;
	}
	.mark svg {
		width: 100%;
		height: 100%;
		display: block;
		overflow: visible;
	}

	.long {
		fill: var(--c1);
		stroke: var(--c1);
	}
	.short {
		fill: var(--c2);
		stroke: var(--c2);
	}

	/* Denkt */
	:global([data-state='thinking']) .logo {
		animation: turn 1.6s cubic-bezier(0.65, 0, 0.35, 1) 0.5s infinite;
	}
	:global([data-state='thinking']) .half.a {
		animation: splitA 1.6s ease-in-out 0.5s infinite;
	}
	:global([data-state='thinking']) .half.b {
		animation: splitB 1.6s ease-in-out 0.5s infinite;
	}
	:global([data-state='thinking']) .short {
		animation: dim 1.6s ease-in-out 0.5s infinite;
	}

	@keyframes turn {
		to {
			transform: rotate(180deg);
		}
	}
	@keyframes splitA {
		50% {
			transform: translate(-14px, -11px);
		}
	}
	@keyframes splitB {
		50% {
			transform: translate(14px, 11px);
		}
	}
	@keyframes dim {
		50% {
			opacity: 0.45;
		}
	}

	/* Schreibt */
	:global([data-state='writing']) .half.a {
		animation: slideA 1s ease-in-out 0.5s infinite;
	}
	:global([data-state='writing']) .half.b {
		animation: slideB 1s ease-in-out 0.5s infinite;
	}
	:global([data-state='writing']) .half.a .short {
		animation: dim 1s ease-in-out 0.5s infinite;
	}
	:global([data-state='writing']) .half.b .short {
		animation: dim 1s ease-in-out 1s infinite;
	}

	@keyframes slideA {
		50% {
			transform: translate(6px, -7px);
		}
	}
	@keyframes slideB {
		50% {
			transform: translate(-6px, 7px);
		}
	}

	/* Fertig */
	.ripple {
		fill: none;
		stroke: var(--c1);
		stroke-width: 8;
		opacity: 0;
		transform-box: fill-box;
		transform-origin: center;
	}
	:global([data-state='done']) .ripple {
		animation: ripple 1s 0.55s ease-out;
	}
	:global([data-state='done']) .mark {
		animation: pop 0.5s 0.6s ease-out;
	}

	@keyframes ripple {
		0% {
			opacity: 0.5;
			transform: scale(0.7);
		}
		100% {
			opacity: 0;
			transform: scale(1.35);
		}
	}
	@keyframes pop {
		50% {
			transform: scale(1.1);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.logo,
		.half,
		.arm,
		.ripple,
		.mark {
			animation: none !important;
		}
		:global([data-state='thinking']) .mark,
		:global([data-state='writing']) .mark {
			animation: fade 1.4s ease-in-out infinite !important;
		}
		@keyframes fade {
			50% {
				opacity: 0.45;
			}
		}
	}
</style>
