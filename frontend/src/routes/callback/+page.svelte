<script>
  import { onMount } from 'svelte';
  import { handleCallback, initAuth0 } from '$lib/auth.js';
  import { goto } from '$app/navigation';
  
  let loading = true;
  let error = null;
  
  onMount(async () => {
    try {
      // Initialize Auth0 client first
      await initAuth0();
      
      // Then handle the callback
      await handleCallback();
      
      // Redirect to dashboard after successful authentication
      await goto('/dashboard');
    } catch (err) {
      error = err.message;
      console.error('Auth callback error:', err);
      
      // Redirect to login on error after a delay
      setTimeout(() => {
        goto('/login');
      }, 3000);
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>Authenticating - GemPrice</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-50">
  <div class="max-w-md w-full space-y-8">
    <div class="text-center">
      {#if loading}
        <div class="flex flex-col items-center space-y-4">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <h2 class="text-2xl font-bold text-gray-900">Authenticating...</h2>
          <p class="text-gray-600">Please wait while we sign you in.</p>
        </div>
      {:else if error}
        <div class="flex flex-col items-center space-y-4">
          <div class="rounded-full bg-red-100 p-3">
            <svg class="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.314 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900">Authentication Error</h2>
          <p class="text-gray-600">{error}</p>
          <a 
            href="/"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Return Home
          </a>
        </div>
      {:else}
        <div class="flex flex-col items-center space-y-4">
          <div class="rounded-full bg-green-100 p-3">
            <svg class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900">Success!</h2>
          <p class="text-gray-600">You have been successfully authenticated.</p>
        </div>
      {/if}
    </div>
  </div>
</div>
