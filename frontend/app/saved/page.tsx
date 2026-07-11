"use client";
import Link from "next/link";

const savedCollections = [
  {
    title: "Recently Saved",
    showViewAll: true,
    cards: [
      {
        id: "1",
        name: "Sarah Jenkins",
        role: "Senior Frontend Dev",
        skills: ["React", "TypeScript", "UI/UX"],
        bio: "Expert in building scalable design systems and high-performance web applications using modern JavaScript frameworks.",
        avatar: "SJ",
        avatarColor: "#494bd6",
        saved: true,
      },
      {
        id: "2",
        name: "Marcus Chen",
        role: "Data Engineer",
        skills: ["Python", "Spark", "AWS"],
        bio: "Specializes in building robust ETL pipelines and migrating legacy data warehouses to scalable cloud infrastructure.",
        avatar: "MC",
        avatarColor: "#03b5d3",
        saved: true,
      },
    ],
  },
  {
    title: "Interview Ready",
    icon: "verified",
    iconColor: "var(--color-secondary)",
    cards: [
      {
        id: "3",
        name: "Elena Rodriguez",
        role: "Product Manager",
        skills: ["Agile", "B2B SaaS"],
        interviewNote: "Interview scheduled: Tomorrow 2 PM",
        avatar: "EL",
        avatarColor: "#8083ff",
        saved: true,
        borderAccent: true,
      },
    ],
  },
  {
    title: "Backend Inspiration",
    empty: true,
  },
];

export default function SavedPage() {
  return (
    <main className="pt-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-10 flex flex-col gap-12">
        {/* Header */}
        <header className="flex flex-col gap-2 border-b pb-8" style={{ borderColor: "rgba(70,69,84,0.3)" }}>
          <h1 className="text-4xl font-bold text-[var(--color-primary)]" style={{ letterSpacing: "-0.02em" }}>
            Saved Resumes
          </h1>
          <p className="text-base text-[var(--color-on-surface-variant)]">
            Organize and review your curated talent profiles.
          </p>
        </header>

        {/* Collections */}
        <div className="flex flex-col gap-14">
          {savedCollections.map((collection) => (
            <section key={collection.title} className="flex flex-col gap-6">
              {/* Section Header */}
              <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: "rgba(70,69,84,0.2)" }}>
                <h2 className="text-xl font-semibold text-[var(--color-inverse-surface)] flex items-center gap-2">
                  {collection.icon && (
                    <span className="material-symbols-outlined" style={{ color: collection.iconColor || "inherit" }}>
                      {collection.icon}
                    </span>
                  )}
                  {collection.title}
                </h2>
                {collection.showViewAll && (
                  <button className="btn-ghost text-xs font-semibold uppercase tracking-wider px-3 py-1.5 rounded text-[var(--color-on-surface-variant)]">
                    View All
                  </button>
                )}
              </div>

              {/* Empty state */}
              {collection.empty ? (
                <div
                  className="rounded-xl p-16 flex flex-col items-center justify-center text-center gap-5"
                  style={{
                    background: "rgba(15,19,31,0.3)",
                    border: "2px dashed rgba(70,69,84,0.4)",
                    backdropFilter: "blur(8px)",
                  }}
                >
                  <span className="material-symbols-outlined text-7xl text-[var(--color-surface-variant)]">person_search</span>
                  <div>
                    <h3 className="text-lg font-semibold text-[var(--color-on-surface)] mb-1">No saved resumes yet</h3>
                    <p className="text-sm text-[var(--color-on-surface-variant)] max-w-md mx-auto">
                      Explore the Talent directory to find and save profiles that fit your backend engineering requirements.
                    </p>
                  </div>
                  <Link
                    href="/search"
                    id="explore-talent-btn"
                    className="btn-ghost text-[var(--color-primary)] text-xs font-semibold uppercase tracking-wider px-4 py-2 rounded-lg flex items-center gap-2 mt-2"
                  >
                    <span className="material-symbols-outlined text-sm">search</span>
                    Explore Talent
                  </Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {collection.cards?.map((card) => (
                    <Link
                      key={card.id}
                      href={`/resume/${card.id}`}
                      id={`saved-card-${card.id}`}
                      className="glass-panel rounded-xl p-6 flex flex-col gap-4 cursor-pointer group"
                      style={card.borderAccent ? { borderLeft: "4px solid var(--color-secondary)" } : {}}
                    >
                      {/* Card Header */}
                      <div className="flex justify-between items-start">
                        <div className="flex gap-4 items-center">
                          <div
                            className="w-12 h-12 rounded-full flex items-center justify-center text-base font-bold text-white"
                            style={{ background: card.avatarColor }}
                          >
                            {card.avatar}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-[var(--color-on-surface)] group-hover:text-[var(--color-primary)] transition-colors">
                              {card.name}
                            </h3>
                            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--color-outline)]">{card.role}</p>
                          </div>
                        </div>
                        <span
                          className="material-symbols-outlined text-[var(--color-primary)] hover:scale-110 transition-transform cursor-pointer"
                          style={{ fontVariationSettings: "'FILL' 1" }}
                        >
                          bookmark
                        </span>
                      </div>

                      {/* Skills */}
                      <div className="flex flex-wrap gap-2 mt-1">
                        {card.skills.map((s) => (
                          <span
                            key={s}
                            className="text-[11px] font-semibold uppercase tracking-wider px-2 py-1 rounded-full"
                            style={{
                              background: "var(--color-surface-container-high)",
                              color: "var(--color-on-surface-variant)",
                              border: "1px solid rgba(70,69,84,0.3)",
                            }}
                          >
                            {s}
                          </span>
                        ))}
                      </div>

                      {/* Bio or Interview Note */}
                      {card.bio && (
                        <p className="text-sm text-[var(--color-on-surface-variant)] line-clamp-2 leading-relaxed">{card.bio}</p>
                      )}
                      {card.interviewNote && (
                        <div
                          className="mt-2 p-3 rounded-lg flex items-center gap-2 text-sm"
                          style={{ background: "#000", border: "1px solid rgba(70,69,84,0.3)", color: "var(--color-secondary)" }}
                        >
                          <span className="material-symbols-outlined text-[16px]">calendar_month</span>
                          <span>{card.interviewNote}</span>
                        </div>
                      )}
                    </Link>
                  ))}
                </div>
              )}
            </section>
          ))}
        </div>
      </div>
    </main>
  );
}
