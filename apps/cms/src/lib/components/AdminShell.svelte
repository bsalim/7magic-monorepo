<script lang="ts">
  import { page } from '$app/state';
  import LayoutDashboardIcon from '@lucide/svelte/icons/layout-dashboard';
  import MapPinIcon from '@lucide/svelte/icons/map-pin';
  import MegaphoneIcon from '@lucide/svelte/icons/megaphone';
  import ImagesIcon from '@lucide/svelte/icons/images';
  import NewspaperIcon from '@lucide/svelte/icons/newspaper';
  import LogOutIcon from '@lucide/svelte/icons/log-out';
  import MenuIcon from '@lucide/svelte/icons/menu';
  import UserCogIcon from '@lucide/svelte/icons/user-cog';
  import type { Component } from 'svelte';
  import type { Snippet } from 'svelte';

  import type { AuthUser } from '$lib/api';
  import * as Avatar from '$lib/components/ui/avatar';
  import { Button } from '$lib/components/ui/button';
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Sheet from '$lib/components/ui/sheet';
  import { Separator } from '$lib/components/ui/separator';

  let { user, children }: { user: AuthUser; children: Snippet } = $props();

  type NavItem = { label: string; href: string; icon: Component };

  const nav: NavItem[] = [
    { label: 'Dashboard', href: '/', icon: LayoutDashboardIcon },
    { label: 'Venues', href: '/venues', icon: MapPinIcon },
    { label: 'Articles', href: '/articles', icon: NewspaperIcon },
    { label: 'Wedding Showcases', href: '/showcases', icon: ImagesIcon },
    { label: 'Promotion Pop up', href: '/promotions', icon: MegaphoneIcon }
  ];

  const pathname = $derived(page.url.pathname);

  const isActive = (href: string) =>
    href === '/' ? pathname === '/' : pathname === href || pathname.startsWith(`${href}/`);

  const activeItem = $derived(nav.find((item) => isActive(item.href)) ?? nav[0]);

  const displayName = $derived(
    [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username || user.email
  );

  const initials = $derived(
    displayName
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join('') ||
      user.email[0]?.toUpperCase() ||
      '7'
  );

  let mobileOpen = $state(false);

  // Close the mobile drawer whenever the route changes.
  $effect(() => {
    pathname;
    mobileOpen = false;
  });
</script>

{#snippet brand()}
  <div class="flex items-center gap-3">
    <img
      src="/img/7magic-logo.png"
      alt="7Magic"
      class="size-10 rounded-md bg-white object-contain p-1.5"
    />
    <div class="min-w-0">
      <p class="text-xs font-medium text-white/55">7Magic Wedding</p>
      <h1 class="truncate text-base font-semibold text-white">CMS Console</h1>
    </div>
  </div>
{/snippet}

{#snippet navLinks()}
  <nav class="space-y-1">
    {#each nav as item (item.href)}
      {@const Icon = item.icon}
      {@const active = isActive(item.href)}
      <a
        href={item.href}
        aria-current={active ? 'page' : undefined}
        class={`flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition ${
          active
            ? 'bg-white text-zinc-900'
            : 'text-white/70 hover:bg-white/10 hover:text-white'
        }`}
      >
        <Icon class="size-[18px]" />
        {item.label}
      </a>
    {/each}
  </nav>
{/snippet}

<div class="min-h-screen bg-muted/40 text-foreground">
  <!-- Desktop sidebar -->
  <aside
    class="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col bg-sidebar lg:flex"
  >
    <div class="flex h-16 items-center border-b border-white/10 px-5">
      {@render brand()}
    </div>
    <div class="flex-1 overflow-y-auto px-3 py-4">
      {@render navLinks()}
    </div>
    <div class="border-t border-white/10 p-3">
      <div class="flex items-center gap-3 rounded-md bg-white/5 p-3">
        <Avatar.Root class="size-9 rounded-md">
          <Avatar.Fallback class="rounded-md bg-white text-sm font-bold text-zinc-900">
            {initials}
          </Avatar.Fallback>
        </Avatar.Root>
        <div class="min-w-0">
          <p class="truncate text-sm font-semibold text-white">{displayName}</p>
          <p class="truncate text-xs text-white/55">{user.email}</p>
        </div>
      </div>
    </div>
  </aside>

  <div class="lg:pl-64">
    <!-- Top bar -->
    <header
      class="sticky top-0 z-20 border-b bg-background/90 backdrop-blur supports-backdrop-filter:bg-background/70"
    >
      <div class="flex h-16 items-center justify-between gap-4 px-4 md:px-6">
        <div class="flex min-w-0 items-center gap-3">
          <!-- Mobile menu trigger -->
          <Sheet.Root bind:open={mobileOpen}>
            <Sheet.Trigger
              class="lg:hidden inline-flex size-9 items-center justify-center rounded-md border bg-background text-muted-foreground hover:bg-accent hover:text-foreground"
              aria-label="Open navigation"
            >
              <MenuIcon class="size-5" />
            </Sheet.Trigger>
            <Sheet.Content side="left" class="w-72 border-r-0 bg-sidebar p-0">
              <div class="flex h-16 items-center border-b border-white/10 px-5">
                {@render brand()}
              </div>
              <div class="px-3 py-4">
                {@render navLinks()}
              </div>
            </Sheet.Content>
          </Sheet.Root>

          <div class="min-w-0">
            <p class="text-xs font-medium text-muted-foreground">Workspace</p>
            <p class="truncate text-sm font-semibold">{activeItem.label}</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <Button href="/venues/new" size="sm" class="hidden sm:inline-flex">New venue</Button>

          <DropdownMenu.Root>
            <DropdownMenu.Trigger
              class="inline-flex items-center gap-2 rounded-full p-0.5 outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-label="Account menu"
            >
              <Avatar.Root class="size-9">
                <Avatar.Fallback class="bg-zinc-900 text-sm font-semibold text-white">
                  {initials}
                </Avatar.Fallback>
              </Avatar.Root>
            </DropdownMenu.Trigger>
            <DropdownMenu.Content align="end" class="w-60">
              <DropdownMenu.Label>
                <div class="flex flex-col">
                  <span class="truncate font-semibold">{displayName}</span>
                  <span class="truncate text-xs font-normal text-muted-foreground">{user.email}</span>
                </div>
              </DropdownMenu.Label>
              <Separator class="my-1" />
              <DropdownMenu.Item>
                {#snippet child({ props })}
                  <a {...props} href="/settings/profile" class="w-full cursor-pointer">
                    <UserCogIcon class="size-4" />
                    Profile settings
                  </a>
                {/snippet}
              </DropdownMenu.Item>
              <form method="POST" action="/logout">
                <DropdownMenu.Item closeOnSelect={false}>
                  {#snippet child({ props })}
                    <button {...props} type="submit" class="w-full cursor-pointer">
                      <LogOutIcon class="size-4" />
                      Sign out
                    </button>
                  {/snippet}
                </DropdownMenu.Item>
              </form>
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        </div>
      </div>
    </header>

    <main class="mx-auto w-full max-w-[1440px] px-4 py-6 md:px-6 md:py-8">
      {@render children()}
    </main>
  </div>
</div>
