import Link from "next/link";

// In a real app, this would fetch from the API via the resume ID
const resume = {
  title: "Senior Backend Engineer",
  location: "San Francisco, CA (Remote)",
  experience: "7+ Years Exp",

  summary:
    "Performance-driven Senior Backend Engineer with over 7 years of experience designing and scaling highly available distributed systems. Specializes in Go, gRPC, and Kubernetes. Proven track record of optimizing microservices to handle millions of concurrent requests while reducing infrastructure costs.",
  skills: {
    languages: ["Go (Golang)", "Python", "Rust", "SQL"],
    infrastructure: ["Kubernetes", "Docker", "AWS (EKS, S3, EC2)", "Terraform", "CI/CD (GitHub Actions)"],
    databases: ["PostgreSQL", "Redis", "Kafka", "Elasticsearch"],
  },
  experience_items: [
    {
      title: "Senior Backend Engineer",
      company: "TechNova Solutions",
      period: "2021 - Present",
      bullets: [
        "Architected and migrated legacy monolith to Go-based microservices, improving system throughput by 300% and reducing latency by 40%.",
        "Implemented event-driven architecture using Kafka, enabling real-time data processing for over 5M daily active users.",
        "Led a team of 4 engineers, conducting code reviews and mentoring junior staff on concurrency patterns in Go.",
        "Optimized PostgreSQL queries and implemented Redis caching layer, decreasing database load by 60%.",
      ],
      active: true,
    },
    {
      title: "Backend Developer",
      company: "DataFlow Inc.",
      period: "2018 - 2021",
      bullets: [
        "Developed RESTful APIs in Python (FastAPI) for data aggregation platform used by enterprise clients.",
        "Containerized applications using Docker and deployed via Kubernetes, establishing CI/CD pipelines with GitLab CI.",
        "Integrated third-party payment gateways (Stripe, PayPal) with secure webhook handling.",
      ],
      active: false,
    },
  ],
  projects: [
    {
      name: "Distributed Task Queue",
      description: "Open-source distributed task queue written in Go, inspired by Celery. Uses Redis as a broker.",
      tags: ["Go", "Redis"],
    },
    {
      name: "K8s Log Aggregator",
      description: "Custom operator for Kubernetes that streams logs from specific pods to an external Elasticsearch cluster.",
      tags: ["Kubernetes", "Elasticsearch"],
    },
  ],
  education: {
    degree: "B.S. Computer Science",
    school: "University of California, Berkeley",
    period: "2014 - 2018",
  },

};

export default function ResumeDetailPage({ params }: { params: { id: string } }) {
  return (
    <div className="flex pt-16 min-h-screen">
      {/* Sidebar — Role Categories */}
      <aside
        className="hidden md:flex fixed left-0 top-16 h-[calc(100vh-64px)] w-[280px] flex-col py-10 z-40"
        style={{
          background: "rgba(27,31,44,0.75)",
          backdropFilter: "blur(20px)",
          borderRight: "1px solid rgba(255,255,255,0.07)",
        }}
      >
        <div className="px-6 mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: "rgba(192,193,255,0.1)", border: "1px solid rgba(192,193,255,0.2)" }}>
              <span className="material-symbols-outlined text-[var(--color-primary)] text-[18px]">filter_list</span>
            </div>
            <h2 className="text-lg font-semibold text-[var(--color-primary)]">Role Categories</h2>
          </div>
          <p className="text-xs text-[var(--color-on-surface-variant)]">Refine your search</p>
        </div>

        <nav className="flex flex-col gap-1 flex-grow overflow-y-auto">
          {[
            { icon: "code", label: "Frontend" },
            { icon: "database", label: "Backend", active: true },
            { icon: "layers", label: "Fullstack" },
            { icon: "terminal", label: "DevOps" },
          ].map((item) => (
            <Link
              key={item.label}
              href="/search"
              className="flex items-center gap-4 px-6 py-3 transition-all"
              style={{
                background: item.active ? "rgba(76,215,246,0.08)" : "transparent",
                color: item.active ? "var(--color-secondary)" : "var(--color-on-surface-variant)",
                borderLeft: item.active ? "4px solid var(--color-secondary)" : "4px solid transparent",
              }}
            >
              <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
              <span className="text-xs font-semibold uppercase tracking-wider">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="px-6 mt-auto mb-8">
          <button className="w-full btn-primary py-3 rounded-lg text-xs font-semibold uppercase tracking-wider">
            Apply Filters
          </button>
        </div>

        <div className="flex flex-col gap-1 border-t border-white/5 pt-4">
          {[{ icon: "settings", label: "Settings" }, { icon: "help", label: "Help" }].map((item) => (
            <a key={item.label} href="#" className="flex items-center gap-4 px-6 py-2 text-[var(--color-on-surface-variant)] hover:bg-white/5 hover:text-[var(--color-on-surface)] transition-all">
              <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
              <span className="text-xs font-semibold uppercase tracking-wider">{item.label}</span>
            </a>
          ))}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-[280px] px-6 md:px-10 pb-20 max-w-[1440px] mx-auto w-full pt-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-xs text-[var(--color-on-surface-variant)] mb-4">
          <Link href="/search" className="hover:text-[var(--color-primary)] transition-colors">Search</Link>
          <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          <Link href="/search" className="hover:text-[var(--color-primary)] transition-colors">Backend Engineers</Link>
          <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          <span className="text-[var(--color-on-surface)]">Senior Go Developer</span>
        </div>

        {/* Header */}
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-[clamp(28px,4vw,48px)] font-bold text-[var(--color-on-surface)] mb-2" style={{ letterSpacing: "-0.02em" }}>
              {resume.title}
            </h1>
            <div className="flex items-center gap-6 text-sm text-[var(--color-on-surface-variant)]">
              <span className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[18px]">location_on</span>
                {resume.location}
              </span>
              <span className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[18px]">work_history</span>
                {resume.experience}
              </span>
            </div>
          </div>
          <a
            href="https://reddit.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold uppercase tracking-wider transition-all"
            style={{ border: "1px solid var(--color-outline-variant)", color: "var(--color-on-surface-variant)" }}
          >
            <span className="material-symbols-outlined text-[18px]">forum</span>
            Source: r/resumes
          </a>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Resume Content */}
          <div className="lg:col-span-12 flex flex-col gap-6">
            {/* Summary */}
            <section
              className="rounded-xl p-6"
              style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)", borderTop: "1px solid rgba(255,255,255,0.2)" }}
            >
              <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-3 flex items-center gap-2">
                <span className="material-symbols-outlined">person</span> Summary
              </h3>
              <p className="text-sm text-[var(--color-on-surface-variant)] leading-relaxed">{resume.summary}</p>
            </section>

            {/* Technical Arsenal */}
            <section
              className="rounded-xl p-6"
              style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)", borderTop: "1px solid rgba(255,255,255,0.2)" }}
            >
              <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined">terminal</span> Technical Arsenal
              </h3>
              {Object.entries(resume.skills).map(([cat, skills]) => (
                <div key={cat} className="mb-4">
                  <h4 className="text-xs font-semibold uppercase tracking-widest text-[var(--color-on-surface)] mb-2">
                    {cat === "languages" ? "Languages" : cat === "infrastructure" ? "Infrastructure & Tools" : "Databases & Messaging"}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {skills.map((s) => (
                      <span key={s} className="skill-badge">{s}</span>
                    ))}
                  </div>
                </div>
              ))}
            </section>

            {/* Experience */}
            <section
              className="rounded-xl p-6"
              style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)", borderTop: "1px solid rgba(255,255,255,0.2)" }}
            >
              <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined">work</span> Professional Experience
              </h3>
              <div className="relative border-l border-[var(--color-outline-variant)]/40 ml-3 pl-6">
                {resume.experience_items.map((item, idx) => (
                  <div key={idx} className={`relative ${idx < resume.experience_items.length - 1 ? "mb-8" : ""}`}>
                    <div
                      className="absolute w-3 h-3 rounded-full -left-[31px] top-1.5"
                      style={{
                        background: item.active ? "var(--color-primary)" : "var(--color-outline-variant)",
                        border: "2px solid var(--color-surface)",
                      }}
                    />
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="text-lg font-semibold text-[var(--color-on-surface)]">{item.title}</h4>
                        <p className="text-sm text-[var(--color-secondary)]">{item.company}</p>
                      </div>
                      <span
                        className="text-xs font-medium px-2 py-1 rounded"
                        style={{ background: "rgba(70,69,84,0.4)", color: "var(--color-on-surface-variant)" }}
                      >
                        {item.period}
                      </span>
                    </div>
                    <ul className="list-disc list-outside ml-4 space-y-1.5">
                      {item.bullets.map((b, i) => (
                        <li key={i} className="text-sm text-[var(--color-on-surface-variant)] leading-relaxed">{b}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>

            {/* Projects */}
            <section
              className="rounded-xl p-6"
              style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)", borderTop: "1px solid rgba(255,255,255,0.2)" }}
            >
              <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-5 flex items-center gap-2">
                <span className="material-symbols-outlined">rocket_launch</span> Notable Projects
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {resume.projects.map((p) => (
                  <div
                    key={p.name}
                    className="p-4 rounded-lg transition-colors"
                    style={{ background: "rgba(27,31,44,0.5)", border: "1px solid rgba(255,255,255,0.05)" }}
                  >
                    <h4 className="text-base font-semibold text-[var(--color-on-surface)] mb-1">{p.name}</h4>
                    <p className="text-xs text-[var(--color-on-surface-variant)] mb-3 leading-relaxed">{p.description}</p>
                    <div className="flex gap-2">
                      {p.tags.map((t) => (
                        <span key={t} className="text-[11px] px-2 py-0.5 rounded" style={{ background: "rgba(192,193,255,0.1)", color: "var(--color-primary)" }}>{t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Education */}
            <section
              className="rounded-xl p-6"
              style={{ background: "rgba(30,41,59,0.7)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)", borderTop: "1px solid rgba(255,255,255,0.2)" }}
            >
              <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined">school</span> Education
              </h3>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-base font-semibold text-[var(--color-on-surface)]">{resume.education.degree}</h4>
                  <p className="text-sm text-[var(--color-on-surface-variant)]">{resume.education.school}</p>
                </div>
                <span className="text-xs text-[var(--color-on-surface-variant)]">{resume.education.period}</span>
              </div>
            </section>
          </div>


        </div>
      </main>
    </div>
  );
}
