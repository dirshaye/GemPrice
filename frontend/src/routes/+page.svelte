<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isLoading, isAuthenticated, initAuth0 } from '$lib/auth.js';
  
  onMount(async () => {
    await initAuth0();
    
    // Redirect based on authentication status
    isAuthenticated.subscribe(authenticated => {
      if (authenticated) {
        goto('/dashboard');
      } else {
        goto('/login');
      }
    });
  });
</script>

<svelte:head>
  <title>GemPrice - AI-Powered Pricing System</title>
  <meta name="description" content="Get AI-powered price recommendations for your products" />
</svelte:head>

<!-- Loading while checking authentication -->
<div class="min-h-screen bg-gray-50 flex items-center justify-center">
  <div class="text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading GemPrice...</p>
  </div>
</div>
