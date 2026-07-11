import Link from "next/link";

const stats = [
  { value: "10K+", label: "Resumes", color: "var(--color-primary)" },
  { value: "800+", label: "Skills", color: "var(--color-primary)" },
  { value: "AI", label: "Powered Analysis", color: "var(--color-secondary)" },
  { value: "15+", label: "Categories", color: "var(--color-primary)" },
];

const features = [
  {
    icon: "dataset",
    title: "Search Thousands",
    description: "Access a vast, searchable index of anonymized resumes verified by real developers.",
    accent: "primary",
    glow: false,
  },
  {
    icon: "memory",
    title: "AI-Powered Analysis",
    description: "Extract skills, identify seniority levels, and benchmark against industry standards automatically.",
    accent: "secondary",
    glow: true,
  },
  {
    icon: "bookmarks",
    title: "Save for Later",
    description: "Curate collections of ideal candidate profiles or benchmark stacks for your next project.",
    accent: "tertiary",
    glow: false,
  },
];

export default function HomePage() {
  return (
    <main className="flex flex-col min-h-screen pt-16 relative overflow-x-hidden">
      {/* Background gradient blobs */}
      <div className="pointer-events-none fixed inset-0 z-0" aria-hidden>
        <div
          className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] rounded-full opacity-20"
          style={{ background: "radial-gradient(circle, rgba(192,193,255,0.3) 0%, transparent 70%)" }}
        />
        <div
          className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full opacity-15"
          style={{ background: "radial-gradient(circle, rgba(76,215,246,0.25) 0%, transparent 70%)" }}
        />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 flex-grow flex items-center px-6 max-w-7xl mx-auto w-full py-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center w-full">

          {/* Left Column */}
          <div className="lg:col-span-7 flex flex-col gap-8">
            <div className="flex flex-col gap-5">
              <h1
                className="text-[clamp(44px,7vw,80px)] font-bold leading-[1.1] text-[var(--color-on-surface)]"
                style={{ letterSpacing: "-0.04em" }}
              >
                Find Real <br />
                <span className="gradient-text">Developer Resumes</span>
              </h1>
              <p className="text-lg text-[var(--color-on-surface-variant)] max-w-xl leading-relaxed">
                Search thousands of anonymized developer resumes collected from Reddit and analyze them using AI.
                Gain insights into real-world tech stacks and career progressions.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center gap-4">
              <Link
                href="/search"
                id="hero-search-cta"
                className="btn-primary flex items-center gap-2 px-8 py-3 rounded-lg text-sm font-semibold tracking-wider uppercase shadow-lg"
              >
                <span className="material-symbols-outlined text-[18px]">search</span>
                Search Resumes
              </Link>
              <Link
                href="/saved"
                className="btn-ghost flex items-center gap-2 px-8 py-3 rounded-lg text-sm font-semibold tracking-wider uppercase"
              >
                <span className="material-symbols-outlined text-[18px]">bookmark</span>
                View Saved
              </Link>
            </div>

            {/* Search Preview */}
            <div className="max-w-2xl">
              <div
                className="glass-panel-static rounded-xl flex items-center h-[52px] px-4 relative overflow-hidden group focus-within:border-[var(--color-primary)]"
                style={{ transition: "box-shadow 0.2s" }}
              >
                <div
                  className="absolute inset-0 opacity-0 group-focus-within:opacity-100 transition-opacity"
                  style={{ background: "linear-gradient(to right, rgba(192,193,255,0.05), transparent)" }}
                />
                <span className="material-symbols-outlined text-[var(--color-outline)] mr-3 z-10">search</span>
                <input
                  id="hero-search-input"
                  className="search-input bg-transparent border-none w-full focus:ring-0 text-[var(--color-on-surface)] placeholder:text-[var(--color-outline)] z-10 h-full text-[15px]"
                  placeholder="Search React, Spring Boot, Docker..."
                  type="text"
                />
                <div className="hidden sm:flex items-center gap-1 ml-auto text-xs text-[var(--color-outline)] font-mono z-10 bg-[var(--color-surface-container-high)] px-2 py-1 rounded">
                  <span>⌘</span><span>K</span>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="flex flex-wrap items-center gap-8 pt-5 border-t border-white/5">
              {stats.map((s) => (
                <div key={s.label} className="flex flex-col">
                  <span className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</span>
                  <span className="text-xs font-semibold uppercase tracking-wider text-[var(--color-on-surface-variant)]">{s.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column — Hero Graphic */}
          <div className="lg:col-span-5 hidden lg:flex justify-center items-center h-full">
            <div className="relative w-full max-w-[500px] aspect-square">
              {/* Main Resume Card Mockup */}
              <div
                className="absolute top-[10%] left-[10%] w-[80%] h-[70%] glass-panel-static rounded-xl overflow-hidden flex flex-col p-6 animate-float z-20"
                style={{ border: "1px solid rgba(255,255,255,0.12)" }}
              >
                <div className="flex items-center gap-4 mb-5">
                  <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ background: "var(--color-surface-container)" }}>
                    <span className="material-symbols-outlined text-[var(--color-primary)]">person</span>
                  </div>
                  <div>
                    <div className="h-4 w-32 rounded mb-2" style={{ background: "rgba(255,255,255,0.2)" }} />
                    <div className="h-3 w-24 rounded" style={{ background: "rgba(255,255,255,0.1)" }} />
                  </div>
                </div>
                <div className="space-y-3 flex-1">
                  <div className="h-3 w-full rounded" style={{ background: "rgba(255,255,255,0.1)" }} />
                  <div className="h-3 w-5/6 rounded" style={{ background: "rgba(255,255,255,0.1)" }} />
                  <div className="h-3 w-4/6 rounded" style={{ background: "rgba(255,255,255,0.1)" }} />
                </div>
                <div className="mt-auto flex gap-2 flex-wrap pt-3">
                  <span className="px-2 py-1 rounded text-[10px] font-mono" style={{ background: "rgba(192,193,255,0.2)", color: "var(--color-primary)" }}>React</span>
                  <span className="px-2 py-1 rounded text-[10px] font-mono" style={{ background: "rgba(76,215,246,0.2)", color: "var(--color-secondary)" }}>TypeScript</span>
                  <span className="px-2 py-1 rounded text-[10px] font-mono" style={{ background: "rgba(255,255,255,0.1)", color: "rgba(255,255,255,0.7)" }}>Node.js</span>
                </div>
                {/* AI scan line */}
                <div
                  className="absolute left-0 w-full h-[2px] animate-scan"
                  style={{ background: "var(--color-secondary)", boxShadow: "0 0 10px #4cd7f6" }}
                />
              </div>

              {/* AI Insights Card */}
              <div
                className="absolute bottom-[10%] right-[-5%] w-[60%] h-[40%] glass-panel-static rounded-xl p-4 animate-float-reverse z-10"
                style={{ border: "1px solid rgba(255,255,255,0.1)" }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className="material-symbols-outlined text-[var(--color-secondary)] text-sm">auto_awesome</span>
                  <span className="text-xs font-semibold text-[var(--color-secondary)]">AI Insights</span>
                </div>
                <div className="h-2 w-full rounded mb-2" style={{ background: "rgba(76,215,246,0.2)" }}>
                  <div className="h-full w-[85%] rounded" style={{ background: "var(--color-secondary)" }} />
                </div>
                <div className="text-[10px] text-white/50 mb-4">Strong match for Frontend roles</div>
                <div className="flex gap-2">
                  {["terminal", "database"].map((icon) => (
                    <div key={icon} className="h-8 w-8 rounded flex items-center justify-center" style={{ background: "var(--color-surface-container)" }}>
                      <span className="material-symbols-outlined text-white/60 text-sm">{icon}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Decorative nodes */}
              <div className="absolute top-[5%] right-[20%] w-3 h-3 rounded-full animate-pulse" style={{ background: "var(--color-primary)", boxShadow: "0 0 15px #c0c1ff" }} />
              <div className="absolute bottom-[20%] left-[5%] w-2 h-2 rounded-full animate-pulse" style={{ background: "var(--color-secondary)", boxShadow: "0 0 10px #4cd7f6", animationDelay: "1s" }} />
              <div className="absolute top-[40%] left-[-10%] w-4 h-4 rounded-full animate-pulse" style={{ background: "var(--color-tertiary-fixed)", boxShadow: "0 0 20px #d8e3fb", animationDelay: "2s" }} />
            </div>
          </div>
        </div>
      </section>

      {/* Features / Bento Grid */}
      <section className="relative z-10 px-6 pb-20 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="glass-panel rounded-xl p-6 flex flex-col gap-4 relative overflow-hidden cursor-default"
            >
              {f.glow && (
                <div
                  className="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl pointer-events-none"
                  style={{ background: "rgba(76,215,246,0.1)", marginRight: "-2.5rem", marginTop: "-2.5rem" }}
                />
              )}
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center z-10"
                style={{
                  background: `linear-gradient(135deg, rgba(${f.accent === "secondary" ? "76,215,246" : f.accent === "tertiary" ? "216,227,251" : "192,193,255"},0.2), transparent)`,
                  border: `1px solid rgba(${f.accent === "secondary" ? "76,215,246" : f.accent === "tertiary" ? "216,227,251" : "192,193,255"},0.2)`,
                }}
              >
                <span
                  className="material-symbols-outlined text-[28px] z-10"
                  style={{
                    color: f.accent === "secondary" ? "var(--color-secondary)" : f.accent === "tertiary" ? "var(--color-tertiary-fixed)" : "var(--color-primary)",
                    fontVariationSettings: "'FILL' 1",
                  }}
                >
                  {f.icon}
                </span>
              </div>
              <div className="z-10">
                <h3 className="text-lg font-semibold text-[var(--color-on-surface)] mb-1">{f.title}</h3>
                <p className="text-sm text-[var(--color-on-surface-variant)] leading-relaxed">{f.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
