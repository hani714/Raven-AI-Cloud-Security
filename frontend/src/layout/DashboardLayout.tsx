import React from 'react';
import { SidebarProvider, SidebarInset } from '@/ui/sidebar';
import { AppSidebar } from './AppSidebar';
import { Header } from './Header';

const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <SidebarProvider defaultOpen={true}>
      {/* Full-width header at the top */}
      <header className="fixed top-0 left-0 right-0 z-50 flex h-16 shrink-0 items-center gap-4 bg-background px-4">
        <Header />
      </header>
      
      {/* Add top padding to account for fixed header */}
      <div className="flex w-full flex-1 min-w-0 pt-16 h-screen overflow-hidden">
        <AppSidebar />
        <SidebarInset className="w-full min-w-0 overflow-y-auto scrollbar-hide h-full">
          {children}
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
};

export default DashboardLayout;