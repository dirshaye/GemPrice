<script>
  import { onMount } from 'svelte';
  import { isLoading, isAuthenticated, user, logout, initAuth0, requireAuth } from '$lib/auth.js';
  import AuthenticatedPriceForm from '$lib/components/AuthenticatedPriceForm.svelte';
  import CSVUpload from '$lib/components/CSVUpload.svelte';
  import HealthStatus from '$lib/components/HealthStatus.svelte';
  
  let activeTab = 'single';
  
  onMount(async () => {
    await initAuth0();
    requireAuth();
  });
  
  function setActiveTab(tab) {
    activeTab = tab;
  }
  
  async function handleLogout() {
    await logout();
  }
</script>

<svelte:head>
  <title>Dashboard - GemPrice</title>
  <meta name="description" content="AI-powered pricing dashboard" />
</svelte:head>

{#if $isLoading}
  <!-- Loading Screen -->
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading dashboard...</p>
    </div>
  </div>
{:else if $isAuthenticated}
  <!-- Authenticated Dashboard -->
  <div class="min-h-screen bg-gray-50">
    <!-- Top Navigation -->
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Logo and Title -->
          <div class="flex items-center">
            <div class="flex-shrink-0 flex items-center">
              <span class="text-2xl">💎</span>
              <h1 class="ml-2 text-xl font-bold text-gray-900">GemPrice</h1>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <a href="/dashboard" class="border-blue-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Dashboard
              </a>
              <a href="/history" class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Pricing History
              </a>
            </div>
          </div>
          
          <!-- User Menu -->
          <div class="flex items-center space-x-4">
            <HealthStatus />
            
            {#if $user}
              <div class="flex items-center space-x-3">
                {#if $user.picture}
                  <img src={$user.picture} alt={$user.name} class="h-8 w-8 rounded-full" />
                {/if}
                <div class="hidden sm:block">
                  <p class="text-sm font-medium text-gray-900">{$user.name || 'User'}</p>
                  <p class="text-xs text-gray-500">{$user.email}</p>
                </div>
                <button
                  on:click={handleLogout}
                  class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Sign out
                </button>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Welcome Message -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900">
          Welcome back{#if $user?.name}, {$user.name.split(' ')[0]}{/if}! 👋
        </h2>
        <p class="mt-1 text-gray-600">
          Get AI-powered pricing recommendations for your products
        </p>
      </div>

      <!-- Navigation Tabs -->
      <div class="mb-8">
        <div class="sm:hidden">
          <select
            bind:value={activeTab}
            class="block w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="single">Single Product</option>
            <option value="bulk">Bulk Upload</option>
          </select>
        </div>
        <div class="hidden sm:block">
          <nav class="flex space-x-8" aria-label="Tabs">
            <button
              on:click={() => setActiveTab('single')}
              class="px-3 py-2 font-medium text-sm rounded-md transition-colors duration-200 {activeTab === 'single' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}"
            >
              📝 Single Product Pricing
            </button>
            <button
              on:click={() => setActiveTab('bulk')}
              class="px-3 py-2 font-medium text-sm rounded-md transition-colors duration-200 {activeTab === 'bulk' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}"
            >
              📊 Bulk CSV Upload
            </button>
          </nav>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="bg-white rounded-lg shadow">
        {#if activeTab === 'single'}
          <div class="p-6">
            <AuthenticatedPriceForm />
          </div>
        {:else if activeTab === 'bulk'}
          <div class="p-6">
            <CSVUpload />
          </div>
        {/if}
      </div>
    </main>
  </div>
{:else}
  <!-- Not Authenticated - Redirect happens in onMount -->
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <p class="text-gray-600">Redirecting to login...</p>
    </div>
  </div>
{/if}
