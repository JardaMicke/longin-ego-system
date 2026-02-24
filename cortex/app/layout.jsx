import "./globals.css";
import { Orbitron, Share_Tech_Mono } from "next/font/google";

const orbitron = Orbitron({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-orbitron"
});
const shareTechMono = Share_Tech_Mono({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-mono"
});

export const metadata = {
  title: "L.O.N.G.I.N. EGO System",
  description: "Logical Orchestrated Networked Generative Intelligent Nexus"
};

export default function RootLayout({ children }) {
  return (
    <html lang="cs" className={`${orbitron.variable} ${shareTechMono.variable}`}>
      <body className="app-root">{children}</body>
    </html>
  );
}
