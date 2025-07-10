<script>
	import '../app.css';

	let { children } = $props();
</script>

<div class="debug-section">
	<p class="text-2xl bg-red-500 p-4">Debug: This should be big red text</p>
	<p style="font-size: 1.5rem; background: blue; padding: 1rem;">Manual: This should match the size above</p>
</div>

{@render children()}
