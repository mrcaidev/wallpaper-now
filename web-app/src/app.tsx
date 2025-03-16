import "@fontsource-variable/inter/index.css";
import "@fontsource/rochester/index.css";
import { Header } from "./components/header.tsx";
import { NowTrending } from "./components/now-trending.tsx";
import { QueryProvider } from "./components/query-provider.tsx";
import { Recommendation } from "./components/recommendation.tsx";
import { Toaster } from "./components/ui/sonner.tsx";
import "./globals.css";

export function App() {
  return (
    <QueryProvider>
      <Header />
      <main className="max-w-7xl mt-20 mx-auto">
        <NowTrending />
        <Recommendation />
      </main>
      <Toaster richColors />
    </QueryProvider>
  );
}
