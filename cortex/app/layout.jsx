export const metadata = {
  title: "Cortex UI",
  description: "Longin EGO Cortex UI"
};

export default function RootLayout({ children }) {
  return (
    <html lang="cs">
      <body>{children}</body>
    </html>
  );
}
