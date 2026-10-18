import {
  Layers,
  Activity,
  CreditCard,
  ChevronDown,
  Home,
  KeyRound,
  Lock,
  LogOut,
} from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
} from '@/ui/sidebar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/ui/dropdown-menu';
import { authService } from '@/services/authService';

const navigationItems = [
  { title: 'Dashboard', url: '/dashboard', icon: Home },
  { title: 'Environments', url: '/environments', icon: Layers },
  { title: 'BYOK', url: '/byok', icon: KeyRound },
  { title: 'Active Scans', url: '/scans', icon: Activity },
  { title: 'Subscriptions', url: '/subscriptions', icon: CreditCard },
];

export function AppSidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [signingOut, setSigningOut] = useState(false);

  const isRouteActive = (url: string) => {
    if (url === '/dashboard') return location.pathname === '/dashboard';
    return location.pathname === url || location.pathname.startsWith(`${url}/`);
  };

  const handleSignOut = async () => {
    try {
      setSigningOut(true);
      await authService.logout();
    } finally {
      navigate('/');
    }
  };

  return (
    <Sidebar collapsible="none" className="border-r border-sidebar-border">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="font-mono text-[10px] uppercase tracking-[0.25em] text-primary text-[#E5173F]">
            // Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => {
                const active = isRouteActive(item.url);
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      tooltip={item.title}
                      isActive={active}
                      className={`group relative transition-all ${
                        active
                          ? 'bg-primary/10 text-primary data-[active=true]:!text-primary'
                          : 'hover:translate-x-0.5 hover:text-foreground'
                      }`}
                    >
                      <Link to={item.url}>
                        {active && (
                          <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r bg-primary shadow-[0_0_12px_hsl(var(--primary))]" />
                        )}
                        <item.icon className={active ? 'text-primary' : ''} />
                        <span className={`font-medium ${active ? 'text-primary' : ''}`}>
                          {item.title}
                        </span>
                        {!active && (
                          <span className="ml-auto h-1 w-1 rounded-full bg-transparent group-hover:bg-primary transition-colors" />
                        )}
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarSeparator />
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton size="lg" className="hover:bg-sidebar-accent">
                  <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary/15 border border-primary/30">
                    <Lock className="size-4 text-primary" />
                  </div>
                  <div className="flex flex-col gap-0.5 leading-none">
                    <span className="font-semibold font-display tracking-wide">Pentester</span>
                    <span className="font-mono text-[10px] text-muted-foreground">admin@raven.dev</span>
                  </div>
                  <ChevronDown className="ml-auto opacity-60" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-[--radix-popper-anchor-width]"
                align="start"
                side="top"
              >
                <DropdownMenuItem>
                  <span>Account</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <span>Preferences</span>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={handleSignOut}
                  disabled={signingOut}
                  className="text-destructive focus:text-destructive"
                >
                  <LogOut className="mr-2 size-4" />
                  <span>{signingOut ? 'Signing out...' : 'Sign out'}</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
