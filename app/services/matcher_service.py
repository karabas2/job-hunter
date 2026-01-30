from typing import List, Dict

def detect_seniority(text: str) -> str:
    text = text.lower()
    student_keywords = ["student", "öğrenci", "intern", "staj", "undergraduate", "part-time", "part time"]
    junior_keywords = ["junior", "new graduate", "yeni mezun", "entry level", "entry-level", "0-2 years"]
    
    if any(k in text for k in student_keywords):
        return "Student"
    if any(k in text for k in junior_keywords):
        return "Graduate"
    
    return "Experienced" # Default

def match_job(job_description: str, keywords: List[str], exclude_keywords: List[str] = None, target_status: str = "Student") -> bool:
    content = job_description.lower()
    seniority = detect_seniority(content)
    
    # Career stage matches (Student vs Graduate vs Experienced)
    # If user wants student/intern, we only show those.
    # If user is Graduate, we show Student and Graduate roles.
    if target_status == "Student":
        if seniority != "Student":
            return False
    elif target_status == "Graduate":
        if seniority == "Experienced":
            return False
            
    # Check only for excluded keywords (things user definitely doesn't want)
    if exclude_keywords:
        for ex in exclude_keywords:
            if ex.lower() in content:
                return False
                
    # We no longer filter out jobs that don't match technical keywords.
    # Everything that fits the career stage and isn't excluded is a "match".
    return True

def simple_ranking(job: Dict, keywords: List[str]) -> float:
    # Very basic ranking based on keyword matches in title/description
    score = 0.0
    text = (job.get('title', '') + " " + job.get('description', '')).lower()
    
    for kw in keywords:
        if kw.lower() in text:
            score += 1.0
            
    return score / len(keywords) if keywords else 1.0
