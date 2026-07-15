"use client";
import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import Image from "next/image";

const BACKEND = "http://localhost:8000";

const CATEGORY_FILTERS = [
  { icon: "apps", label: "All" },
  { icon: "code", label: "Frontend" },
  { icon: "database", label: "Backend" },
  { icon: "layers", label: "Fullstack" },
  { icon: "terminal", label: "DevOps" },
  { icon: "psychology", label: "ML / AI" },
  { icon: "cloud", label: "Cloud" },
  { icon: "engineering", label: "Mechanical" },
  { icon: "science", label: "Chemical" },
  { icon: "flight", label: "Aerospace" },
];

interface Resume {
  id: number;
  post_id: number;
  category: string | null;
  summary: string | null;
  anonymous_file_path: string | null;
  embedding_id: string | null;
  created_at: string;
  updated_at: string;
  title: string | null;
  file_url: string | null;
  file_type: string | null;
  subreddit: string | null;
  score: number | null;
  permalink: string | null;
  author: string | null;
}

function YoEBadge({ title }: { title: string | null }) {
  if (!title) return null;
  const studentMatch = title.match(/\[Student\]/i);
  const yoeMatch = title.match(/\[(\d+)\+?\s*YoE\]/i);
  if (!studentMatch && !yoeMatch) return null;
  const label = studentMatch ? "Student" : `${yoeMatch![1]} YoE`;
  return (
    <span
      className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
      style={{ background: "rgba(192,193,255,0.15)", color: "var(--color-primary)", border: "1px solid rgba(192,193,255,0.25)" }}
    >
      {label}
    </span>
  );
}

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return null;
  return (
    <span className="flex items-center gap-1 text-[11px] text-white/70 bg-black/30 px-2 py-0.5 rounded-full">
      <span className="material-symbols-outlined text-[13px] text-[var(--color-secondary)]">arrow_upward</span>
      {score}
    </span>
  );
}

function SkeletonCard() {
  return (
    <div className="glass-panel rounded-xl overflow-hidden animate-pulse" style={{ border: "1px solid rgba(255,255,255,0.06)" }}>
      <div className="w-full h-48 bg-white/5" />
      <div className="p-5 flex flex-col gap-3">
        <div className="flex gap-2"><div className="h-4 w-16 rounded-full bg-white/10" /><div className="h-4 w-12 rounded-full bg-white/5" /></div>
        <div className="h-3 w-full rounded bg-white/10" />
        <div className="h-3 w-4/5 rounded bg-white/5" />
        <div className="h-3 w-2/3 rounded bg-white/5" />
        <div className="h-8 w-full rounded bg-white/5 mt-2" />
      </div>
    </div>
  );
}

export default function SearchPage() {
  const [activeCategory, setActiveCategory] = useState("All");
  const [query, setQuery] = useState("");
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const PAGE_SIZE = 18;

  const fetchResumes = useCallback(async (pg: number, cat: string, reset: boolean) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(pg), page_size: String(PAGE_SIZE) });
      if (cat !== "All") params.set("category", cat);
      const res = await fetch(`${BACKEND}/api/resumes?${params}`);
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const data: Resume[] = await res.json();
      setResumes((prev) => (reset ? data : [...prev, ...data]));
      setHasMore(data.length === PAGE_SIZE);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setPage(1);
    setResumes([]);
    fetchResumes(1, activeCategory, true);
  }, [activeCategory, fetchResumes]);

  useEffect(() => {
    if (page === 1) return;
    fetchResumes(page, activeCategory, false);
  }, [page, activeCategory, fetchResumes]);

  const filtered = query.trim()
    ? resumes.filter((r) => {
        const q = query.toLowerCase();
        return (
          r.title?.toLowerCase().includes(q) ||
          r.author?.toLowerCase().includes(q) ||
          r.category?.toLowerCase().includes(q)
        );
      })
    : resumes;

  return (
    <div className="flex pt-16 min-h-screen">
      {/* Sidebar */}
      <aside
        className="hidden md:flex fixed left-0 top-16 h-[calc(100vh-64px)] w-[240px] flex-col p-4 z-40"
        style={{ background: "rgba(27,31,44,0.75)", backdropFilter: "blur(16px)", borderRight: "1px solid rgba(255,255,255,0.07)" }}
      >
        <div className="mb-4">
          <h2 className="text-lg font-bold text-[var(--color-primary)]">Filters</h2>
          <p className="text-xs text-[var(--color-on-surface-variant)] mt-0.5">Browse by category</p>
        </div>
        <nav className="flex-1 flex flex-col gap-1 overflow-y-auto">
          {CATEGORY_FILTERS.map((cat) => {
            const isActive = cat.label === activeCategory;
            return (
              <button
                key={cat.label}
                id={`filter-${cat.label.toLowerCase().replace(/\s+/g, "-")}`}
                onClick={() => setActiveCategory(cat.label)}
                className="flex items-center gap-3 px-3 py-2 rounded text-left transition-all duration-200"
                style={{
                  background: isActive ? "rgba(192,193,255,0.1)" : "transparent",
                  color: isActive ? "var(--color-primary)" : "var(--color-on-surface-variant)",
                  borderRight: isActive ? "2px solid var(--color-primary)" : "2px solid transparent",
                  fontWeight: isActive ? 700 : 400,
                }}
              >
                <span className="material-symbols-outlined text-[18px]">{cat.icon}</span>
                <span className="text-xs font-semibold uppercase tracking-wider">{cat.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="mt-auto border-t border-white/5 pt-3 flex flex-col gap-1">
          {[{ icon: "menu_book", label: "Documentation" }, { icon: "contact_support", label: "Support" }].map((item) => (
            <a key={item.label} href="#" className="flex items-center gap-3 px-3 py-2 rounded text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)] hover:bg-white/5 transition-all">
              <span className="material-symbols-outlined text-[18px]">{item.icon}</span>
              <span className="text-xs font-semibold uppercase tracking-wider">{item.label}</span>
            </a>
          ))}
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 md:ml-[240px] px-6 pb-16 max-w-7xl mx-auto w-full">
        {/* Sticky Search Bar */}
        <div className="sticky top-16 z-30 py-4" style={{ background: "rgba(15,19,31,0.88)", backdropFilter: "blur(8px)" }}>
          <div className="relative w-full max-w-3xl mx-auto">
            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-on-surface-variant)]">search</span>
            <input
              id="search-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="search-input w-full h-[52px] pl-12 pr-4 rounded-xl text-[var(--color-on-surface)] placeholder:text-[var(--color-on-surface-variant)]/50 text-[15px]"
              placeholder="Search by title, author, category..."
            />
          </div>
        </div>

        {/* Result count row */}
        <div className="flex items-center justify-between mb-6 mt-2">
          <p className="text-sm text-[var(--color-on-surface-variant)]">
            {loading && resumes.length === 0 ? "Loading resumes..." : error ? (
              <span className="text-red-400">{error}</span>
            ) : (
              <>Showing <span className="text-[var(--color-primary)] font-semibold">{filtered.length}</span> resumes
                {query && <span className="ml-1 text-[var(--color-outline)]">for &ldquo;{query}&rdquo;</span>}
              </>
            )}
          </p>
          <span className="text-xs text-[var(--color-outline)] uppercase tracking-wider font-semibold">{activeCategory}</span>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filtered.map((resume) => (
            <article
              key={resume.id}
              className="glass-panel rounded-xl overflow-hidden flex flex-col group transition-all duration-300"
              style={{ border: "1px solid rgba(255,255,255,0.06)" }}
            >
              {/* Thumbnail */}
              <div className="relative w-full h-48 bg-[var(--color-surface-container)] overflow-hidden">
                {resume.file_url ? (
                  <Image
                    src={resume.file_url}
                    alt={resume.title || "Resume"}
                    fill
                    className="object-cover object-top transition-transform duration-500 group-hover:scale-105"
                    sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 33vw"
                    unoptimized
                  />
                ) : (
                  <div className="flex items-center justify-center h-full w-full">
                    <span className="material-symbols-outlined text-6xl text-white/10">description</span>
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-surface)]/70 via-transparent to-transparent" />
                <div className="absolute top-3 right-3">
                  <ScoreBadge score={resume.score} />
                </div>
              </div>

              {/* Body */}
              <div className="p-5 flex flex-col gap-3 flex-1">
                {/* Badges row */}
                <div className="flex items-center gap-2 flex-wrap">
                  <YoEBadge title={resume.title} />
                  {resume.category && (
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full" style={{ background: "rgba(76,215,246,0.12)", color: "var(--color-secondary)", border: "1px solid rgba(76,215,246,0.2)" }}>
                      {resume.category}
                    </span>
                  )}
                </div>

                {/* Title */}
                <h3 className="text-sm font-semibold text-[var(--color-on-surface)] leading-snug line-clamp-2">
                  {resume.title || "Untitled Resume"}
                </h3>

                {/* Meta */}
                <div className="flex items-center gap-2 text-[11px] text-[var(--color-on-surface-variant)]">
                  <span className="material-symbols-outlined text-[13px]">person</span>
                  <span className="font-mono truncate max-w-[120px]">{resume.author || "anonymous"}</span>
                  {resume.subreddit && (
                    <>
                      <span className="opacity-30">·</span>
                      <span className="opacity-60">r/{resume.subreddit}</span>
                    </>
                  )}
                </div>

                {resume.summary && (
                  <p className="text-[12px] text-[var(--color-on-surface-variant)] leading-relaxed line-clamp-2">{resume.summary}</p>
                )}

                {/* Footer */}
                <footer className="mt-auto pt-3 border-t border-white/5 flex items-center gap-2">
                  <Link
                    href={`/resume/${resume.id}`}
                    id={`view-resume-${resume.id}`}
                    className="btn-ghost flex-1 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider flex items-center justify-center gap-2"
                  >
                    <span className="material-symbols-outlined text-[16px]">visibility</span>
                    View Resume
                  </Link>
                  {resume.permalink && (
                    <a
                      href={`https://reddit.com${resume.permalink}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      title="View on Reddit"
                      className="p-2 rounded-lg text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)] hover:bg-white/5 transition-all"
                    >
                      <span className="material-symbols-outlined text-[18px]">open_in_new</span>
                    </a>
                  )}
                </footer>
              </div>
            </article>
          ))}

          {/* Skeleton loading cards */}
          {loading && Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={`sk-${i}`} />)}
        </div>

        {/* Empty state */}
        {!loading && filtered.length === 0 && !error && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <span className="material-symbols-outlined text-7xl text-[var(--color-surface-variant)]">search_off</span>
            <h3 className="text-lg font-semibold text-[var(--color-on-surface)]">No resumes found</h3>
            <p className="text-sm text-[var(--color-on-surface-variant)]">Try a different keyword or category filter</p>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <span className="material-symbols-outlined text-7xl text-red-400/50">error_outline</span>
            <h3 className="text-lg font-semibold text-[var(--color-on-surface)]">Could not connect to backend</h3>
            <p className="text-sm text-red-400">{error}</p>
            <button onClick={() => fetchResumes(1, activeCategory, true)} className="btn-primary px-6 py-2 rounded-lg text-sm mt-2">
              Retry
            </button>
          </div>
        )}

        {/* Load More */}
        {!loading && hasMore && filtered.length > 0 && !query && (
          <div className="flex justify-center mt-10">
            <button
              id="load-more-btn"
              onClick={() => setPage((p) => p + 1)}
              className="btn-ghost px-8 py-3 rounded-xl text-sm font-semibold uppercase tracking-wider flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">expand_more</span>
              Load More
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
