<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isLoading, isAuthenticated, login, initAuth0 } from '$lib/auth.js';
  
  let loginError = null;
  
  onMount(async () => {
    await initAuth0();
    
    // Check if already authenticated and redirect
    isAuthenticated.subscribe(authenticated => {
      if (authenticated) {
        goto('/dashboard');
      }
    });
  });
  
  async function handleLogin() {
    try {
      loginError = null;
      await login();
    } catch (error) {
      loginError = 'Failed to sign in. Please try again.';
      console.error('Login error:', error);
    }
  }
</script>

<svelte:head>
  <title>Sign In - GemPrice</title>
  <meta name="description" content="Sign in to access AI-powered pricing recommendations" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <!-- Header -->
    <div class="text-center">
      <div class="mx-auto h-20 w-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center">
        <span class="text-white text-3xl font-bold">💎</span>
      </div>
      <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
        Welcome to GemPrice
      </h2>
      <p class="mt-2 text-sm text-gray-600">
        AI-Powered Dynamic Pricing System
      </p>
    </div>

    <!-- Login Card -->
    <div class="bg-white rounded-lg shadow-xl p-8">
      {#if $isLoading}
        <!-- Loading State -->
        <div class="text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-2 text-gray-600">Loading...</p>
        </div>
      {:else}
        <!-- Login Form -->
        <div class="space-y-6">
          <div class="text-center">
            <h3 class="text-lg font-semibold text-gray-900">Sign in to your account</h3>
            <p class="mt-1 text-sm text-gray-600">
              Get started with intelligent pricing recommendations
            </p>
          </div>

          {#if loginError}
            <div class="bg-red-50 border border-red-200 rounded-md p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-red-800">{loginError}</p>
                </div>
              </div>
            </div>
          {/if}

          <!-- Features -->
          <div class="space-y-4">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"></path>
                  </svg>
                </div>
              </div>
              <p class="text-sm text-gray-700">AI-powered pricing recommendations</p>
            </div>
            
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"></path>
                  </svg>
                </div>
              </div>
              <p class="text-sm text-gray-700">Bulk CSV processing</p>
            </div>
            
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"></path>
                  </svg>
                </div>
              </div>
              <p class="text-sm text-gray-700">Pricing history & analytics</p>
            </div>
          </div>

          <!-- Sign In Button -->
          <button
            on:click={handleLogin}
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 transform hover:scale-105"
          >
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="h-5 w-5 text-blue-200 group-hover:text-blue-100" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
            </span>
            Sign in with Auth0
          </button>

          <div class="text-center">
            <p class="text-xs text-gray-500">
              Secure authentication powered by Auth0
            </p>
          </div>
        </div>
      {/if}
    </div>

    <!-- Footer -->
    <div class="text-center text-sm text-gray-500">
      <p>&copy; 2025 GemPrice. All rights reserved.</p>
    </div>
  </div>
</div>
