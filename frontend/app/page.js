import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>AI Indressing</h1>
      <p>Upload a photo and let AI transform your outfit</p>
      <nav>
        <Link href="/create">Create Character</Link>
        <Link href="/edit">Edit Photo</Link>
        <Link href="/gallery">Gallery</Link>
      </nav>
    </main>
  );
}
