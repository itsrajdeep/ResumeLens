"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

const BACKEND = "http://localhost:8000";

interface Resume {
  id: number;
  post_id: number;
  category: string | null;
  summary: string | null;
  ocr_text: string | null;
  parsed_data: Record<string, unknown> | null;
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
  skills: { name: string; category: string | null }[];
  projects: { id: number; name: string; description: string; tech_tags: string[] }[];
}

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-white/5 ${className}`} />;
}

export default function ResumeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imgExpanded, setImgExpanded] = useState(false);
  const [imgLoaded, setImgLoaded] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetch(`${BACKEND}/api/resumes/${id}`)
      .then((r) => {
        if (!r.ok) throw new Error(`API error ${r.status}`);
        return r.json();
      })
      .then((data) => { setResume(data); setLoading(false); })
      .catch((e) => { setError(e.message); setLoading(false); });
  }, [id]);

  const yoeMatch = resume?.title?.match(/\[(\d+)\+?\s*YoE\]/i);
  const isStudent = /\[Student\]/i.test(resume?.title || "");
  const yoeLabel = isStudent ? "Student" : yoeMatch ? `${yoeMatch[1]} YoE` : null;
  const postedDate = resume?.created_at
    ? new Date(resume.created_at).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })
    : null;

  if (loading) {
    return (
      <div className="flex pt-16 min-h-screen">
        <main className="flex-1 px-6 md:px-10 pb-20 max-w-5xl mx-auto w-full pt-8">
          <Skeleton className="h-4 w-48 mb-8" />
          <Skeleton className="h-10 w-3/4 mb-4" />
          <Skeleton className="h-4 w-1/3 mb-8" />
          <Skeleton className="w-full aspect-[8/11] rounded-xl mb-6" />
        </main>
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="flex pt-16 min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="material-symbols-outlined text-7xl text-red-400/50">error_outline</span>
          <h2 className="text-xl font-semibold text-[var(--color-on-surface)]">Resume not found</h2>
          <p className="text-sm text-red-400">{error}</p>
          <Link href="/search" className="btn-primary px-6 py-2 rounded-lg text-sm mt-2">Back to Search</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex pt-16 min-h-screen">
      {imgExpanded && resume.file_url && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.93)", backdropFilter: "blur(8px)" }}
          onClick={() => setImgExpanded(false)}
        >
          <button
            className="absolute top-5 right-5 w-10 h-10 rounded-full flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 transition-all z-10"
            onClick={() => setImgExpanded(false)}
          >
            <span className="material-symbols-outlined text-2xl">close</span>
          </button>
          <div className="relative max-w-5xl w-full max-h-[90vh]" onClick={(e) => e.stopPropagation()}>
            <img
              src={resume.file_url}
              alt={resume.title || "Resume"}
              className="w-full h-auto max-h-[90vh] object-contain rounded-xl shadow-2xl"
              style={{ border: "1px solid rgba(255,255,255,0.1)" }}
            />
          </div>
        </div>
      )}

      <main className="flex-1 px-6 md:px-10 pb-20 max-w-5xl mx-auto w-full pt-8">
        <div className="flex items-center gap-2 text-xs text-[var(--color-on-surface-variant)] mb-6">
          <Link href="/search" className="hover:text-[var(--color-primary)] transition-colors flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">arrow_back</span>
            Search
          </Link>
          <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          <span className="text-[var(--color-on-surface)] truncate max-w-xs">{resume.title || `Resume #${resume.id}`}</span>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
          <div className="flex flex-col gap-2">
            <div className="flex flex-wrap items-center gap-2">
              {yoeLabel && (
                <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full"
                  style={{ background: "rgba(192,193,255,0.15)", color: "var(--color-primary)", border: "1px solid rgba(192,193,255,0.3)" }}>
                  {yoeLabel}
                </span>
              )}
              {resume.category && (
                <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full"
                  style={{ background: "rgba(76,215,246,0.12)", color: "var(--color-secondary)", border: "1px solid rgba(76,215,246,0.25)" }}>
                  {resume.category}
                </span>
              )}
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-[var(--color-on-surface)] leading-tight" style={{ letterSpacing: "-0.02em" }}>
              {resume.title || `Resume #${resume.id}`}
            </h1>
            <div className="flex flex-wrap items-center gap-4 text-xs text-[var(--color-on-surface-variant)]">
              {resume.author && (
                <span className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[15px]">person</span>
                  u/{resume.author}
                </span>
              )}
              {resume.subreddit && (
                <span className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[15px]">forum</span>
                  r/{resume.subreddit}
                </span>
              )}
              {resume.score !== null && (
                <span className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[15px] text-[var(--color-secondary)]">arrow_upward</span>
                  {resume.score} upvotes
                </span>
              )}
              {postedDate && (
                <span className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[15px]">calendar_today</span>
                  {postedDate}
                </span>
              )}
            </div>
          </div>
          {resume.permalink && (
            <a
              href={`https://reddit.com${resume.permalink}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold uppercase tracking-wider shrink-0 transition-all hover:bg-white/5"
              style={{ border: "1px solid var(--color-outline-variant)", color: "var(--color-on-surface-variant)" }}
            >
              <span className="material-symbols-outlined text-[16px]">open_in_new</span>
              View on Reddit
            </a>
          )}
        </div>

        {resume.file_url && (
          <section className="mb-8">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-on-surface-variant)] flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px]">description</span>
                Resume Document
              </h2>
              <button
                onClick={() => setImgExpanded(true)}
                className="flex items-center gap-1.5 text-xs text-[var(--color-primary)] hover:underline"
              >
                <span className="material-symbols-outlined text-[15px]">zoom_in</span>
                Full screen
              </button>
            </div>
            <div
              className="relative w-full rounded-2xl overflow-hidden cursor-zoom-in group"
              style={{ border: "1px solid rgba(255,255,255,0.1)", background: "rgba(30,41,59,0.5)" }}
              onClick={() => setImgExpanded(true)}
            >
              {!imgLoaded && (
                <div className="absolute inset-0 animate-pulse bg-white/5 flex items-center justify-center" style={{ minHeight: "400px" }}>
                  <span className="material-symbols-outlined text-4xl text-white/10">description</span>
                </div>
              )}
              <img
                src={resume.file_url}
                alt={resume.title || "Resume"}
                className={`w-full h-auto object-cover object-top transition-all duration-500 group-hover:brightness-110 ${imgLoaded ? "opacity-100" : "opacity-0"}`}
                onLoad={() => setImgLoaded(true)}
              />
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                <div className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold text-white"
                  style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(8px)", border: "1px solid rgba(255,255,255,0.15)" }}>
                  <span className="material-symbols-outlined text-[18px]">zoom_in</span>
                  Click to expand
                </div>
              </div>
            </div>
          </section>
        )}

        {resume.summary && (
          <section className="rounded-xl p-6 mb-6"
            style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)" }}>
            <h3 className="text-base font-semibold text-[var(--color-primary)] mb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
              AI Summary
            </h3>
            <p className="text-sm text-[var(--color-on-surface-variant)] leading-relaxed">{resume.summary}</p>
          </section>
        )}

        {resume.skills && resume.skills.length > 0 && (
          <section className="rounded-xl p-6 mb-6"
            style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)" }}>
            <h3 className="text-base font-semibold text-[var(--color-primary)] mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">terminal</span>
              Skills
            </h3>
            <div className="flex flex-wrap gap-2">
              {resume.skills.map((s) => (
                <span key={s.name} className="skill-badge">{s.name}</span>
              ))}
            </div>
          </section>
        )}

        {resume.projects && resume.projects.length > 0 && (
          <section className="rounded-xl p-6 mb-6"
            style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)" }}>
            <h3 className="text-base font-semibold text-[var(--color-primary)] mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">rocket_launch</span>
              Projects
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {resume.projects.map((p) => (
                <div key={p.id} className="p-4 rounded-lg" style={{ background: "rgba(27,31,44,0.5)", border: "1px solid rgba(255,255,255,0.05)" }}>
                  <h4 className="text-sm font-semibold text-[var(--color-on-surface)] mb-1">{p.name}</h4>
                  {p.description && <p className="text-xs text-[var(--color-on-surface-variant)] mb-3 leading-relaxed">{p.description}</p>}
                  {p.tech_tags?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {p.tech_tags.map((t) => (
                        <span key={t} className="text-[10px] px-2 py-0.5 rounded"
                          style={{ background: "rgba(192,193,255,0.1)", color: "var(--color-primary)" }}>{t}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {resume.ocr_text && (
          <details className="rounded-xl mb-6 overflow-hidden"
            style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)" }}>
            <summary className="p-6 cursor-pointer text-base font-semibold text-[var(--color-primary)] flex items-center gap-2 select-none list-none">
              <span className="material-symbols-outlined text-[18px]">text_snippet</span>
              Extracted Text (OCR)
              <span className="ml-auto material-symbols-outlined text-[18px] text-[var(--color-outline)]">expand_more</span>
            </summary>
            <div className="px-6 pb-6">
              <pre className="text-xs text-[var(--color-on-surface-variant)] whitespace-pre-wrap leading-relaxed font-mono"
                style={{ background: "rgba(15,19,31,0.5)", padding: "1rem", borderRadius: "0.5rem", maxHeight: "400px", overflowY: "auto" }}>
                {resume.ocr_text}
              </pre>
            </div>
          </details>
        )}

        {!resume.summary && (!resume.skills || resume.skills.length === 0) && !resume.ocr_text && (
          <div className="rounded-xl p-8 text-center"
            style={{ background: "rgba(30,41,59,0.5)", border: "1px dashed rgba(255,255,255,0.1)" }}>
            <span className="material-symbols-outlined text-4xl text-[var(--color-outline)] mb-3 block">hourglass_empty</span>
            <p className="text-sm text-[var(--color-on-surface-variant)]">
              This resume has not been processed yet. The AI pipeline will extract skills, generate a summary, and anonymize it shortly.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}