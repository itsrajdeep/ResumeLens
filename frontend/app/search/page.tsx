"use client";
import { useState } from "react";
import Link from "next/link";

const categories = [
  { icon: "code", label: "Frontend" },
  { icon: "database", label: "Backend" },
  { icon: "layers", label: "Fullstack" },
  { icon: "terminal", label: "DevOps" },
  { icon: "psychology", label: "ML / AI" },
  { icon: "cloud", label: "Cloud" },
];

const mockResumes = [
  {
    id: "1",
    code: "ID-FEND-892",
    role: "Backend Engineer",

    skills: ["Java", "Spring Boot", "AWS", "PostgreSQL"],
    project: ["> Architected microservices", "> 40% reduction in latency", "> 1M+ daily active users"],
  },
  {
    id: "2",
    code: "ID-DATA-401",
    role: "Data Scientist",

    skills: ["Python", "TensorFlow", "SQL", "Spark"],
    project: ["> Built predictive NLP models", "> 15% increase in retention", "> Deployed via Docker/K8s"],
  },
  {
    id: "3",
    code: "ID-UIUX-112",
    role: "Frontend Engineer",

    skills: ["React", "TypeScript", "Tailwind", "Next.js"],
    project: ["> Migrated legacy SPA to Next", "> 90+ Lighthouse score", "> Implemented Design System"],
  },
  {
    id: "4",
    code: "ID-DEVOPS-228",
    role: "DevOps Engineer",

    skills: ["Kubernetes", "Terraform", "AWS", "CI/CD"],
    project: ["> Zero-downtime deployments", "> Reduced infra cost 35%", "> Multi-region k8s clusters"],
  },
  {
    id: "5",
    code: "ID-MLAI-055",
    role: "ML Engineer",

    skills: ["Python", "PyTorch", "MLflow", "CUDA"],
    project: ["> LLM fine-tuning pipeline", "> Reduced inference latency", "> Open-source NLP toolkit"],
  },
  {
    id: "6",
    code: "ID-FULL-334",
    role: "Fullstack Developer",

    skills: ["Go", "React", "PostgreSQL", "Docker"],
    project: ["> Greenfield SaaS platform", "> Built API from scratch", "> 5k+ daily active users"],
  },
];

export default function SearchPage() {
  const [activeCategory, setActiveCategory] = useState("Backend");
  const [query, setQuery] = useState("");

  const filtered = mockResumes.filter((r) => {
    const q = query.toLowerCase();
    return (
      r.role.toLowerCase().includes(q) ||
      r.skills.some((s) => s.toLowerCase().includes(q))
    );
  });

  return (
    <div className="flex pt-16 min-h-screen">
      {/* Sidebar */}
      <aside
        className="hidden md:flex fixed left-0 top-16 h-[calc(100vh-64px)] w-[240px] flex-col p-4 z-40"
        style={{
          background: "rgba(27,31,44,0.75)",
          backdropFilter: "blur(16px)",
          borderRight: "1px solid rgba(255,255,255,0.07)",
        }}
      >
        <div className="mb-4">
          <h2 className="text-lg font-bold text-[var(--color-primary)]">Filters</h2>
          <p className="text-xs text-[var(--color-on-surface-variant)] mt-0.5">Refine search</p>
        </div>

        <nav className="flex-1 flex flex-col gap-1 overflow-y-auto">
          {categories.map((cat) => {
            const isActive = cat.label === activeCategory;
            return (
              <button
                key={cat.label}
                id={`filter-${cat.label.toLowerCase()}`}
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

        <div className="mt-auto flex flex-col gap-3">
          <button className="btn-primary w-full py-2 rounded text-xs font-semibold uppercase tracking-wider">
            Save Search
          </button>
          <div className="border-t border-white/5 pt-3 flex flex-col gap-1">
            {[{ icon: "menu_book", label: "Documentation" }, { icon: "contact_support", label: "Support" }].map((item) => (
              <a key={item.label} href="#" className="flex items-center gap-3 px-3 py-2 rounded text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)] hover:bg-white/5 transition-all">
                <span className="material-symbols-outlined text-[18px]">{item.icon}</span>
                <span className="text-xs font-semibold uppercase tracking-wider">{item.label}</span>
              </a>
            ))}
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 md:ml-[240px] px-6 pb-16 max-w-7xl mx-auto w-full">
        {/* Sticky Search */}
        <div className="sticky top-20 z-30 py-4" style={{ background: "rgba(15,19,31,0.8)", backdropFilter: "blur(8px)" }}>
          <div className="relative w-full max-w-3xl mx-auto">
            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-on-surface-variant)]">search</span>
            <input
              id="search-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="search-input w-full h-[52px] pl-12 pr-4 rounded-xl text-[var(--color-on-surface)] placeholder:text-[var(--color-on-surface-variant)]/50 text-[15px]"
              placeholder="Search resumes by skill, role... [Ctrl + K]"
            />
          </div>
        </div>

        {/* Results Count */}
        <div className="flex items-center justify-between mb-6 mt-2">
          <p className="text-sm text-[var(--color-on-surface-variant)]">
            Showing <span className="text-[var(--color-primary)] font-semibold">{filtered.length}</span> resumes
          </p>
          <span className="text-xs text-[var(--color-outline)] uppercase tracking-wider font-semibold">{activeCategory}</span>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filtered.map((resume) => (
            <article key={resume.id} className="glass-panel rounded-xl p-6 flex flex-col gap-4">
              {/* Header */}
              <header className="flex justify-between items-start border-b border-white/5 pb-4">
                <div>
                  <h3 className="font-mono text-[13px] text-[var(--color-on-surface-variant)]">{resume.code}</h3>
                  <div className="mt-2 inline-block px-3 py-1 rounded-full" style={{ background: "var(--color-surface-container-high)", border: "1px solid rgba(70,69,84,0.4)" }}>
                    <span className="text-xs font-semibold uppercase tracking-wider text-[var(--color-secondary)]">{resume.role}</span>
                  </div>
                </div>

              </header>

              {/* Skills */}
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-wider text-[var(--color-on-surface-variant)] mb-2">Core Skills</p>
                <div className="flex flex-wrap gap-2">
                  {resume.skills.map((s) => (
                    <span key={s} className="px-2 py-1 rounded text-xs font-medium text-[var(--color-on-surface)]" style={{ background: "var(--color-surface-container)" }}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Project Snippet */}
              <div className="flex-1">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-[var(--color-on-surface-variant)] mb-2">Recent Project</p>
                <div className="code-block text-[var(--color-on-surface-variant)]">
                  {resume.project.map((line, i) => (
                    <div key={i}>{line}</div>
                  ))}
                </div>
              </div>

              {/* Footer */}
              <footer className="pt-4 border-t border-white/5">
                <Link
                  href={`/resume/${resume.id}`}
                  id={`view-resume-${resume.id}`}
                  className="btn-ghost w-full py-2 rounded-lg text-xs font-semibold uppercase tracking-wider flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">visibility</span>
                  Open Resume
                </Link>
              </footer>
            </article>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <span className="material-symbols-outlined text-7xl text-[var(--color-surface-variant)]">search_off</span>
            <h3 className="text-lg font-semibold text-[var(--color-on-surface)]">No results found</h3>
            <p className="text-sm text-[var(--color-on-surface-variant)]">Try a different skill or keyword</p>
          </div>
        )}
      </main>
    </div>
  );
}
