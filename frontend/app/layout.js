import "./globals.css";

export const metadata = {
  title: "AI Indressing",
  description: "Upload a photo and transform outfits with AI",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
