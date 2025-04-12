def calculate_match_score(resume_skills, jd_skills):
    if not resume_skills or not jd_skills:
        return 0, []

    matched_skills = list(set(resume_skills).intersection(set(jd_skills)))
    match_percent = (len(matched_skills) / len(jd_skills)) * 100

    return round(match_percent, 2), matched_skills


    matched_skills = list(set(resume_skills).intersection(set(jd_skills)))
    match_percent = (len(matched_skills) / len(jd_skills)) * 100

    return round(match_percent, 2), matched_skills
