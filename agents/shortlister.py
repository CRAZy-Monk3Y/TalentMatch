# --- agents/shortlister.py ---
def shortlist_candidates(
    candidates,
    all_resumes,
    threshold,
    progress_bar,
    progress_val,
    progress_segments,
    shortlisted_resumes,
):
    selected_candidates = []
    increments = (
        int(progress_segments / len(candidates))
        if len(candidates) > 0
        else progress_segments
    )
    for index, candidate in enumerate(candidates):
        match_eval = (
            int(candidate["match"].replace("%", ""))
            if "match" in candidate and isinstance(candidate["match"], str)
            else int(candidate["match"])
            if "match" in candidate and isinstance(candidate["match"], int)
            else 0
        )
        if match_eval >= int(threshold):
            selected_candidates.append(candidate)
            shortlisted_resumes.append(all_resumes[index])
        # print("Threshold", threshold)
        # print("Match", match_eval)
        # print(selected_candidates)
        progress_val += increments
        progress_bar.progress(
            progress_val,
            f"Overall completion {progress_val}% Shortlisting resumes for the role...",
        )

    return selected_candidates
