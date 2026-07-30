"""
Rule-based recommendation engine: career suggestions, skill-gap analysis,
resume tips, and company recommendations. No external API required, so the
app runs fully offline once dependencies are installed.
"""

REQUIRED_SKILLS = {
    "Computer Science": {"DSA": 85, "Python": 80, "SQL": 75, "System Design": 65, "Git": 70, "Cloud Basics": 60},
    "Information Technology": {"SQL": 80, "Networking": 75, "Python": 70, "Cloud Basics": 70, "Linux": 65, "Git": 65},
    "Electronics": {"Embedded C": 75, "VLSI": 65, "Python": 60, "MATLAB": 65, "IoT": 60, "PCB Design": 55},
    "Mechanical": {"AutoCAD": 75, "SolidWorks": 70, "Thermodynamics": 70, "Python": 50, "Six Sigma": 55, "CAM": 55},
    "Civil": {"AutoCAD": 75, "STAAD Pro": 70, "Project Mgmt": 65, "Surveying": 65, "Excel": 60, "Estimation": 60},
    "Electrical": {"MATLAB": 70, "Power Systems": 70, "PLC": 65, "Python": 55, "Circuit Design": 65, "AutoCAD": 55},
}

COURSES = {
    "DSA": "Data Structures & Algorithms — NeetCode / GeeksforGeeks track",
    "Python": "Python for Everybody — Coursera",
    "SQL": "SQL for Data Analysis — Mode Analytics / DataCamp",
    "System Design": "Grokking the System Design Interview",
    "Git": "Git & GitHub Crash Course",
    "Cloud Basics": "AWS/Azure Cloud Practitioner Fundamentals",
    "Networking": "CCNA Fundamentals",
    "Linux": "Linux Command Line Basics",
    "Embedded C": "Embedded C Programming — Udemy",
    "VLSI": "VLSI Design Fundamentals — NPTEL",
    "MATLAB": "MATLAB Onramp — MathWorks",
    "IoT": "IoT Fundamentals — Cisco",
    "PCB Design": "PCB Design with KiCad",
    "AutoCAD": "AutoCAD Essential Training",
    "SolidWorks": "SolidWorks for Mechanical Design",
    "Thermodynamics": "Applied Thermodynamics Refresher",
    "Six Sigma": "Six Sigma Green Belt Basics",
    "CAM": "CAM Programming Basics",
    "STAAD Pro": "STAAD Pro for Structural Analysis",
    "Project Mgmt": "Project Management Basics — PMI",
    "Surveying": "Surveying & Leveling Fundamentals",
    "Excel": "Excel for Engineers",
    "Estimation": "Cost Estimation & Quantity Surveying",
    "Power Systems": "Power System Analysis — NPTEL",
    "PLC": "PLC Programming Basics",
    "Circuit Design": "Circuit Design & Analysis",
}

COMPANIES = [
    {"name": "TCS", "min_cgpa": 6.0, "focus": ["Computer Science", "Information Technology", "Electronics", "Electrical", "Mechanical", "Civil"], "min_skill": 45, "tier": "Mass Recruiter"},
    {"name": "Infosys", "min_cgpa": 6.5, "focus": ["Computer Science", "Information Technology", "Electronics"], "min_skill": 50, "tier": "Mass Recruiter"},
    {"name": "Wipro", "min_cgpa": 6.0, "focus": ["Computer Science", "Information Technology", "Electrical"], "min_skill": 45, "tier": "Mass Recruiter"},
    {"name": "Cognizant", "min_cgpa": 6.5, "focus": ["Computer Science", "Information Technology"], "min_skill": 50, "tier": "Mass Recruiter"},
    {"name": "Capgemini", "min_cgpa": 6.0, "focus": ["Computer Science", "Information Technology", "Electronics"], "min_skill": 48, "tier": "Mass Recruiter"},
    {"name": "Accenture", "min_cgpa": 6.5, "focus": ["Computer Science", "Information Technology"], "min_skill": 55, "tier": "Mass Recruiter"},
    {"name": "IBM", "min_cgpa": 7.0, "focus": ["Computer Science", "Information Technology", "Electronics"], "min_skill": 60, "tier": "Product/Core"},
    {"name": "Deloitte", "min_cgpa": 7.0, "focus": ["Computer Science", "Information Technology"], "min_skill": 60, "tier": "Consulting"},
    {"name": "Amazon", "min_cgpa": 7.5, "focus": ["Computer Science", "Information Technology", "Electronics"], "min_skill": 78, "tier": "Product/Core"},
    {"name": "Microsoft", "min_cgpa": 8.0, "focus": ["Computer Science", "Information Technology"], "min_skill": 82, "tier": "Product/Core"},
    {"name": "Google", "min_cgpa": 8.5, "focus": ["Computer Science", "Information Technology"], "min_skill": 88, "tier": "Product/Core"},
]

CAREER_PATHS = {
    "Computer Science": ["Software Development Engineer", "Data Analyst", "Backend Engineer", "ML Engineer", "DevOps Engineer"],
    "Information Technology": ["Full-Stack Developer", "QA Engineer", "Cloud Engineer", "System Administrator"],
    "Electronics": ["Embedded Systems Engineer", "VLSI Design Engineer", "IoT Developer", "Firmware Engineer"],
    "Mechanical": ["Design Engineer", "Manufacturing Engineer", "Quality Engineer", "CAD Specialist"],
    "Civil": ["Site Engineer", "Structural Design Engineer", "Project Planner", "Estimation Engineer"],
    "Electrical": ["Electrical Design Engineer", "Power Systems Engineer", "Automation Engineer", "PLC Programmer"],
}


def skill_gap_analysis(department, student):
    required = REQUIRED_SKILLS.get(department, REQUIRED_SKILLS["Computer Science"])
    # Map the student's raw scores onto the department's named skills proportionally
    base_scores = {
        "programming": student["programming_skills"],
        "technical": student["technical_score"],
        "aptitude": student["aptitude_score"],
        "soft": student["soft_skills"],
    }
    avg_technical = (base_scores["programming"] + base_scores["technical"]) / 2

    results = []
    for skill, target in required.items():
        # derive a plausible "current level" from technical + a bit of variance per skill name
        offset = (hash(skill) % 15) - 7
        current = max(10, min(100, int(avg_technical + offset)))
        gap = max(0, target - current)
        results.append({
            "skill": skill,
            "current": current,
            "required": target,
            "gap": gap,
            "priority": "High" if gap > 25 else ("Medium" if gap > 10 else "Low"),
            "course": COURSES.get(skill, "Relevant online course"),
        })
    results.sort(key=lambda r: -r["gap"])
    return results


def career_suggestions(department, prediction):
    paths = CAREER_PATHS.get(department, CAREER_PATHS["Computer Science"])
    if prediction["probability"] >= 70:
        focus = "You're in a strong position — focus on interview prep and negotiating well."
    elif prediction["probability"] >= 45:
        focus = "You're on the edge — closing 1-2 skill gaps could meaningfully lift your odds."
    else:
        focus = "Prioritize the roadmap below before your next application cycle."

    return {
        "paths": paths,
        "focus": focus,
        "internships": [f"{department} Internship – Summer Cohort", "Remote Micro-Internship (AICTE/Internshala)", "Research Internship under faculty mentor"],
        "certifications": ["NPTEL Certification in core subject", "Coursera Specialization (role-aligned)", "HackerRank Skill Certification"],
        "coding_platforms": ["LeetCode", "HackerRank", "CodeChef", "GeeksforGeeks"],
        "project_ideas": [
            f"Capstone project solving a real {department} industry problem",
            "Open-source contribution (3+ merged PRs)",
            "Portfolio website showcasing 3 best projects",
        ],
    }


def resume_tips(student):
    tips = []
    score = 55
    if student["projects"] < 2:
        tips.append("Add at least 2-3 detailed projects with your role, tech stack, and measurable impact.")
    else:
        score += 10
    if student["internships"] == 0:
        tips.append("No internship listed — consider a virtual internship to strengthen your resume.")
    else:
        score += 10
    if student["certifications"] == 0:
        tips.append("Add 1-2 relevant certifications to signal continuous learning.")
    else:
        score += 8
    if student["communication_skills"] < 60:
        tips.append("Practice concise bullet points — recruiters scan resumes in ~7 seconds.")
    else:
        score += 7
    if student["leadership"]:
        score += 10
    tips.append("Use action verbs (Built, Led, Optimized) and quantify results wherever possible.")
    tips.append("Keep the resume to 1 page for freshers; use a clean ATS-friendly template (no tables/graphics).")

    score = min(98, score + student["hackathons"] * 2)

    checklist = [
        "Contact info + LinkedIn + GitHub at the top",
        "Skills section matched to job description keywords",
        "Quantified achievements (%, ₹, time saved)",
        "No spelling/grammar errors",
        "Consistent formatting and font",
        "PDF format, descriptive filename",
    ]
    return {"score": score, "tips": tips, "checklist": checklist,
            "linkedin_tips": ["Add a professional photo & headline", "List projects with media", "Get 2-3 recommendations", "Post about your projects/learnings"],
            "github_tips": ["Pin your best 4-6 repos", "Write clear READMEs with screenshots", "Keep a consistent commit history"]}


def recommend_companies(department, cgpa, avg_skill):
    ranked = []
    for c in COMPANIES:
        if department not in c["focus"]:
            eligible = cgpa >= c["min_cgpa"] + 0.5 and avg_skill >= c["min_skill"] + 10
        else:
            eligible = cgpa >= c["min_cgpa"] and avg_skill >= c["min_skill"]
        fit_score = 0
        if eligible:
            fit_score = min(99, int(50 + (cgpa - c["min_cgpa"]) * 8 + (avg_skill - c["min_skill"]) * 0.5))
        ranked.append({**c, "eligible": eligible, "fit_score": max(0, fit_score)})
    ranked.sort(key=lambda r: -r["fit_score"])
    return ranked
