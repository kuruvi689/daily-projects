import json, sys, re, argparse, os, textwrap, datetime
from collections import Counter

# Simple skill extraction using regex patterns (can be expanded)
SKILL_PATTERN = re.compile(r"\b([A-Za-z\+\#]{2,})\b", re.IGNORECASE)

def load_resume(path: str) -> set:
    """Load resume text and extract a set of skill tokens."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return {m.group(1).lower() for m in SKILL_PATTERN.finditer(text)}

def load_job_descriptions(dir_path: str) -> dict:
    """Read all *.txt files in a directory as job descriptions.
    Returns a mapping of filename → set of extracted skills.
    """
    jobs = {}
    for fname in os.listdir(dir_path):
        if not fname.lower().endswith('.txt'):
            continue
        full = os.path.join(dir_path, fname)
        with open(full, "r", encoding="utf-8") as f:
            text = f.read()
        jobs[fname] = {m.group(1).lower() for m in SKILL_PATTERN.finditer(text)}
    return jobs

def compute_gap(resume_skills: set, job_skills: set) -> set:
    """Return the set of skills required by the job that are missing from the resume."""
    return job_skills - resume_skills

def summarize_gaps(gap_map: dict) -> Counter:
    """Aggregate missing skills across all jobs for a frequency count."""
    counter = Counter()
    for gaps in gap_map.values():
        counter.update(gaps)
    return counter

def format_report(gap_map: dict, aggregated: Counter) -> str:
    lines = []
    lines.append("# Opportunity Gap Analysis Report")
    lines.append(f"Generated: {datetime.datetime.utcnow().isoformat()}Z\n")
    for job, gaps in gap_map.items():
        lines.append(f"## {job}")
        if gaps:
            lines.append("Missing Skills:")
            for skill in sorted(gaps):
                lines.append(f"- {skill}")
        else:
            lines.append("All required skills present. ✅")
        lines.append("")
    lines.append("---")
    lines.append("## Aggregate Missing Skill Frequency")
    for skill, cnt in aggregated.most_common():
        lines.append(f"- {skill}: missing in {cnt} job(s)")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Analyze skill gaps between a resume and multiple job descriptions.")
    parser.add_argument("resume", help="Path to a plain‑text resume file")
    parser.add_argument("jobs_dir", help="Directory containing *.txt job description files")
    parser.add_argument("-o", "--output", default="gap_report.md",
                        help="Output markdown report file (default: gap_report.md)")
    args = parser.parse_args()

    if not os.path.isfile(args.resume):
        sys.exit(f"Resume file not found: {args.resume}")
    if not os.path.isdir(args.jobs_dir):
        sys.exit(f"Jobs directory not found: {args.jobs_dir}")

    resume_skills = load_resume(args.resume)
    job_map = load_job_descriptions(args.jobs_dir)

    gap_map = {job: compute_gap(resume_skills, skills) for job, skills in job_map.items()}
    aggregated = summarize_gaps(gap_map)
    report = format_report(gap_map, aggregated)

    with open(args.output, "w", encoding="utf-8") as out:
        out.write(report)
    print(f"Report written to {args.output}")

if __name__ == "__main__":
    main()
