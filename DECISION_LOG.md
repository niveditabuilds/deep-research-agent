# Decision log — what worked vs what failed

Arm A = fluent research draft from one run.  
Arm B = same run, after trust checks (only keep claims we can verify against sources).

About **20 claims** checked per demo.

---

## Worked

| Decision | Why we did it | Result in the demos |
|---|---|---|
| **Confidence = source type** (paper / news / blog), not high/medium/low | Matches how readers already judge sources | Some runs were paper-heavy; others blog-heavy — same rules applied |
| **Citation must check out** (page loads + fact appears on the page) | An impressive link alone is not proof | **9–15 of 20** claims failed the check and left the main report |
| **Same research run for A and B** | So we isolate the trust filter, not a luckier second search | One draft produced both A and B |
| **Also use links the agent visited**, not only links pasted in the sentence | Drafts often under-cite even after good search | More claims could be checked at all (e.g. 12/20 got URLs on synthetic data) |
| **Failed checks go in collapsed Needs review** | Keep them inspectable without looking like answers | Unverified numbers stay out of the summary |

---

## Failed / reversed

Priority order. Each item: what we tried → why it was wrong → what we do now.

### 1. Letting unchecked claims through when the automatic check failed

**Tried:** If a link looked important (e.g. arXiv), still treat the claim as a finding when the page wouldn’t load or the quoted fact wasn’t on the page.  
**Wrong because:** That puts fluent-but-unchecked text back into the main report — the problem Arm B is meant to fix.  
**Now:** Failed check ⇒ not a finding (Needs review only). We accept some false negatives rather than promoting unchecked claims.

### 2. Building Arm B as a checklist instead of a report

**Tried:** After filtering, print headings plus bullet lists of surviving sentences.  
**Wrong because:** Readers expect a research report with paragraphs; a checklist looked like an audit log next to A’s essay.  
**Now:** B is a multi-section prose report using only claims that passed the checks.

### 3. Using only three flat buckets (Findings / Extra / Unresolved)

**Tried:** Ignore themes (benefits, risks, debates); sort every claim into three piles.  
**Wrong because:** Hard to compare with A’s thematic structure; B felt randomly organized.  
**Now:** Keep a thematic outline; trust only decides what may be said in each section.

### 4. Showing failed checks as a normal section next to findings

**Tried:** List “could not verify” items in the main body.  
**Wrong because:** Skimmers treated that list as more answers.  
**Now:** Failed items only in a collapsed Needs review block.

### 5. Only checking sentences that already contained a URL

**Tried:** No URL in the sentence ⇒ fail immediately.  
**Wrong because:** The agent often writes without inline links even after visiting good pages, so B had almost nothing left.  
**Now:** Also use URLs from the agent’s search/read history.

---

## Results (Arm B trust check)

| Research question | Kept as findings | Needs review | Share kept |
|---|---:|---:|---:|
| Synthetic data for LLMs | 5 | 15 | 25% |
| Chain-of-thought debate | 10 | 10 | 50% |
| Inference-time compute scaling | 11 | 9 | 55% |

**Takeaway:** A maximizes a complete fluent story. B maximizes claims you can stand behind. The drop is intentional.
