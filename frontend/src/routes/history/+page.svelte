<script>
  import { onMount } from 'svelte';
  import { isLoading, isAuthenticated, user, logout, initAuth0, requireAuth, getAccessToken } from '$lib/auth.js';
  
  let pricingHistory = [];
  let loading = true;
  let error = null;
  let stats = {
    total_suggestions: 0,
    avg_suggested_price: 0,
    avg_confidence: 0,
    latest_suggestion: null
  };
  
  onMount(async () => {
    await initAuth0();
    requireAuth();
    await loadPricingHistory();
    await loadStats();
  });
  
  async function loadPricingHistory() {
    try {
      loading = true;
      const token = await getAccessToken();
      
      if (!token) {
        error = 'Authentication required';
        return;
      }
      
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/user/suggestions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        pricingHistory = data.suggestions || [];
      } else {
        error = 'Failed to load pricing history';
      }
    } catch (err) {
      error = 'Network error loading history';
      console.error('Error loading pricing history:', err);
    } finally {
      loading = false;
    }
  }
  
  async function loadStats() {
    try {
      const token = await getAccessToken();
      
      if (!token) return;
      
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/user/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        stats = await response.json();
      }
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  }
  
  async function handleLogout() {
    await logout();
  }
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  }
</script>

<svelte:head>
  <title>Pricing History - GemPrice</title>
  <meta name="description" content="View your pricing recommendation history" />
</svelte:head>

{#if $isLoading}
  <!-- Loading Screen -->
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading...</p>
    </div>
  </div>
{:else if $isAuthenticated}
  <!-- Authenticated History Page -->
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
              <a href="/dashboard" class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Dashboard
              </a>
              <a href="/history" class="border-blue-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Pricing History
              </a>
            </div>
          </div>
          
          <!-- User Menu -->
          <div class="flex items-center space-x-4">
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
      <!-- Header -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900">Pricing History</h2>
        <p class="mt-1 text-gray-600">
          View and analyze your past pricing recommendations
        </p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <span class="text-white text-sm font-bold">#</span>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Total Recommendations</dt>
                  <dd class="text-lg font-medium text-gray-900">{stats.total_suggestions}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span class="text-white text-sm font-bold">$</span>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Average Price</dt>
                  <dd class="text-lg font-medium text-gray-900">{formatCurrency(stats.avg_suggested_price || 0)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <span class="text-white text-sm font-bold">%</span>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Avg Confidence</dt>
                  <dd class="text-lg font-medium text-gray-900">{Math.round((stats.avg_confidence || 0) * 100)}%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <span class="text-white text-sm font-bold">⏰</span>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Last Activity</dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {#if stats.latest_suggestion}
                      {formatDate(stats.latest_suggestion)}
                    {:else}
                      No data
                    {/if}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- History Table -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Recommendations
          </h3>
          
          {#if loading}
            <div class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p class="mt-2 text-gray-600">Loading history...</p>
            </div>
          {:else if error}
            <div class="text-center py-8">
              <div class="text-red-600 mb-4">
                <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.314 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <p class="text-gray-600">{error}</p>
              <button 
                on:click={loadPricingHistory}
                class="mt-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
              >
                Try Again
              </button>
            </div>
          {:else if pricingHistory.length === 0}
            <div class="text-center py-8">
              <div class="text-gray-400 mb-4">
                <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-4v4m0 0V3m0 0h2.5a1 1 0 011 1v1M9 5H6.5a1 1 0 00-1 1v1" />
                </svg>
              </div>
              <p class="text-gray-600">No pricing history yet</p>
              <a href="/dashboard" class="mt-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                Get Your First Recommendation
              </a>
            </div>
          {:else}
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost Price</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Suggested Price</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reasoning</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  {#each pricingHistory as item}
                    <tr class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-medium text-gray-900">
                          {item.product_data?.name || 'Product'}
                        </div>
                        <div class="text-sm text-gray-500">
                          {item.product_data?.category || ''}
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(item.product_data?.cost_price || 0)}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="text-sm font-medium text-green-600">
                          {formatCurrency(item.suggested_price)}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {
                          (item.confidence_score || 0) > 0.8 ? 'bg-green-100 text-green-800' : 
                          (item.confidence_score || 0) > 0.6 ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-red-100 text-red-800'
                        }">
                          {Math.round((item.confidence_score || 0) * 100)}%
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(item.timestamp)}
                      </td>
                      <td class="px-6 py-4">
                        <div class="text-sm text-gray-900 max-w-xs truncate" title={item.reasoning}>
                          {item.reasoning || 'No reasoning provided'}
                        </div>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {/if}
        </div>
      </div>
    </main>
  </div>
{:else}
  <!-- Not Authenticated -->
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <p class="text-gray-600">Redirecting to login...</p>
    </div>
  </div>
{/if}
