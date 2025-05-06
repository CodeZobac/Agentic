'use client';

import dynamic from 'next/dynamic';

// Use dynamic import with no SSR for the AgentFlow component
const AgentFlow = dynamic(() => import('./components/AgentFlow'), {
  ssr: false,
});

export default function Home() {
  return (
    <main className="min-h-screen">
      <AgentFlow />
    </main>
  );
}
