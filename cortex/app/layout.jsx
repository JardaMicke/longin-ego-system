import "./globals.css";

export const metadata = {
  title: "L.O.N.G.I.N. EGO System",
  description: "Logical Orchestrated Networked Generative Intelligent Nexus"
};

export default function RootLayout({ children }) {
  return (
    <html lang="cs">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=Share+Tech+Mono&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="app-root">{children}</body>
    </html>
  );
}
