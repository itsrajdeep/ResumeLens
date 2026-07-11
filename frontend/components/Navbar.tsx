"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/search", label: "Search" },
  { href: "/saved", label: "Saved" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed top-0 left-0 w-full z-50 flex items-center justify-between px-6 h-16"
      style={{
        background: "rgba(15, 19, 31, 0.75)",
        backdropFilter: "blur(16px)",
        WebkitBackdropFilter: "blur(16px)",
        borderBottom: "1px solid rgba(255,255,255,0.07)",
        boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
      }}
    >
      {/* Brand */}
      <div className="flex items-center gap-3">
        <span className="material-symbols-outlined text-[var(--color-primary)] text-3xl">explore</span>
        <Link href="/" className="font-bold text-2xl tracking-tight text-[var(--color-on-surface)]" style={{ letterSpacing: "-0.02em" }}>
          ResumeAtlas
        </Link>
      </div>

      {/* Nav Links */}
      <div className="hidden md:flex items-center h-full gap-2">
        {navLinks.map((link) => {
          const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
          return (
            <Link
              key={link.href}
              href={link.href}
              className="relative px-4 py-1.5 text-sm font-medium rounded transition-colors duration-200"
              style={{
                color: isActive ? "var(--color-primary)" : "var(--color-on-surface-variant)",
                borderBottom: isActive ? "2px solid var(--color-primary)" : "2px solid transparent",
              }}
            >
              {link.label}
            </Link>
          );
        })}
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        <Link href="/search" className="flex items-center gap-1.5 btn-ghost text-xs font-semibold px-4 py-2 rounded-lg tracking-wider uppercase">
          <span className="material-symbols-outlined text-[16px]">search</span>
          Search
        </Link>
        <button className="btn-primary text-xs font-semibold px-4 py-2 rounded-lg tracking-wider uppercase">
          Sign In
        </button>
      </div>
    </nav>
  );
}
