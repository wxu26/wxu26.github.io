# Managing Claude for Research

Created: December 28, 2025

By Claude, under my supervision

Note: This article presents a framework we believe should work based on reasoning about Claude's capabilities and failure modes. It was developed through extensive discussion but has not yet been validated on real research projects over extended time. Consider it a starting point to adapt and test, not a proven solution.

If you try this framework, I'd appreciate hearing how it goes—what works, what breaks, what you'd change.

---

## TL;DR

Put the two template files ([CLAUDE.md](claude_for_research/CLAUDE.md) and [RESEARCH_NOTE.md](claude_for_research/RESEARCH_NOTE.md)) in your project folder, launch Claude Code there, and ask Claude what to do next.

---

## 1. Introduction

Claude and other large language models have improved to the point where a paradigm shift is warranted in how we work with them. We should "manage" Claude rather than "use" it—working less like a coder with a tool and more like a mentor guiding a capable but amnesiac collaborator. (This framing builds on [Claude is meant to be managed, not used](https://wxu26.github.io/writings/managing_claude.html).)

For engineering tasks, Claude works remarkably well out of the box. Give it a clear specification, and it writes code, debugs, refactors, documents. But in the human coauthor's experience, Claude does less well when asked to lead research projects. It handles individual tasks but loses the thread across sessions. It produces polished outputs that obscure uncertainty. It doesn't naturally maintain the kind of evolving project narrative that research requires.

Why the gap? Research and engineering make different demands.

### Why research is different from engineering

Engineering problems typically have clear goals that don't change much once defined, plans that can be laid out and executed, and success criteria known in advance.

Research problems are different. Goals are hierarchical: high-level goals are often vague while low-level goals are clearer. Plans branch and revise constantly as understanding evolves. What counts as "done" emerges through the process.

This means research requires different practices. The challenge isn't just tracking tasks—it's maintaining a coherent narrative as that narrative changes. Standard project management tools assume the goal is fixed. Research needs something else.

### Thesis: discipline, not creativity

The key difference between research and engineering isn't creativity—both benefit from creative thinking. The difference is project management. Engineering projects can be planned and executed; research projects must be navigated as understanding evolves. This requires a different kind of discipline: not discipline in following a fixed plan, but discipline in maintaining coherence while the plan changes.

Claude can learn this discipline. But it must be taught through structure, not prompted ad hoc.

What "disciplined" means here: not asking Claude to be innovative or have original insights, but asking Claude to have good *habits*—maintaining documentation, knowing when to escalate, tracking confidence levels, grounding claims in evidence.

The division of labor:
- **Humans own**: value judgments, intuition, research direction, recognizing fundamental dead ends
- **Claude owns**: systematic documentation, translating vague ideas into structured plans, maintaining project coherence, flagging when input is needed

This article focuses on the disciplined part—the part we're confident Claude can do, given the right structure.

---

## 2. The Model: Grad Student and Busy Advisor

What mental model should guide how we work with Claude on research? We need one that accounts for Claude's strengths (fast, knowledgeable, good at execution) and limitations (no persistent memory, doesn't naturally maintain long-term project coherence).

The model: **treat Claude as a graduate student and yourself as a busy advisor.** Claude does the day-to-day work, maintains all project documentation, makes tactical decisions independently, and flags strategic questions for human input. The human provides direction, makes judgment calls, and reviews progress periodically—but doesn't need to track details. That's Claude's job.

### Where this model comes from

This framing stems from the human coauthor's experience as a student researcher, with busy advisors and a poor memory. The approach that worked was maintaining a single evolving research note (often a paper draft) that contained everything.

Now they find themselves in a position similar to their past mentors: supervising research, with limited time to track every detail. And Claude is in a position similar to where they were—capable of doing the work, but needing structure to maintain coherence across sessions. The difference is that Claude's memory limitation isn't a personal quirk; it's architectural. Every session starts fresh.

### Why the model fits

Consider a graduate student working with an advisor who has perhaps one hour per week to meet. Between meetings, the advisor often forgets the details. This creates specific demands on the student:

- **Push the project forward autonomously.** Can't wait for the advisor to direct every step.
- **Make tactical decisions independently.** Small choices shouldn't require meetings.
- **Flag strategic questions.** Big decisions about direction need advisor input.
- **Make re-entry cheap.** When they do meet, the advisor should be able to understand the current state quickly.

This maps well to working with Claude. Each session is like a new meeting—context must be reconstructed. Claude should push forward, not wait passively. Tactical execution can be autonomous; strategic decisions need human input. The human, like the advisor, can't track everything—that's Claude's job.

The model isn't perfect. A real grad student learns and grows over time; Claude doesn't. But it captures the essential dynamic: an autonomous collaborator who must maintain project state for a busy, forgetful supervisor.

### What a good student brings to the meeting

If the student must make re-entry cheap for a forgetful advisor, what should they bring? The answer that worked for the human coauthor: **the research notes, and nothing else.** Well-maintained notes should contain everything:

1. **Status** — which sections are developed tells you where the project is
2. **Decisions made** — "we chose X; we also tried Y and it didn't work because Z"
3. **Blocking issues** — marked clearly so the advisor can respond
4. **Confidence levels** — claims marked by how well-supported they are
5. **Next steps** — implied by gaps in the notes; what's missing is what needs work

Why a single document rather than multiple reports, logs, and summaries? Because the research notes become the eventual paper. Maintaining them from day one means documentation effort is never wasted. Multiple documents create overhead and diverge over time.

Session-level details—"today I will work on X"—don't belong in the research notes. They're transient. Git history captures what changed and when. The notes should contain the *state of knowledge*, not the *log of activity*.

---

## 3. The System

Given the grad-student model, what concrete system do we need? Here's the overview:

- **Two documents**: A research note in the form of an evolving paper draft with explicit uncertainty, and claude.md serving as Claude's operating manual with session rituals and project-specific instructions.
- **Session rituals**: Start each session by evaluating the notes, end by reflecting on what changed and updating them.

Templates: [claude.md template](CLAUDE.md) and [research notes template](RESEARCH_NOTE.md).

The rest of this section explains the reasoning behind these choices.

### Why not use existing tools?

Existing resources don't address this problem. Lab notebook practices ([NIH](https://oir.nih.gov/), [Science](https://www.science.org/content/article/how-keep-lab-notebook)) focus on reproducibility and IP, not evolving narratives. Advisor-student guides ([Cornell](https://gradschool.cornell.edu/academic-progress/opportunities-resources-support/advising-guide-for-research-students-2025/), [SIGARCH](https://www.sigarch.org/having-effective-meetings-between-advisors-and-students/)) cover meeting logistics but assume documentation skills are already in place. ML experiment trackers (MLflow, Weights & Biases) log metrics but not the higher-level story of why we tried things and where we're going.

The gap: no one discusses how to maintain an evolving research narrative as a discipline—especially not in a way teachable to an AI collaborator.

### What documents should exist?

We need Claude to maintain project state across sessions. One option: separate documents for different purposes—a project plan, a results log, a decisions record. But this creates overhead and documents drift apart over time.

A simpler option: **a single primary document** containing the evolving research narrative. We call this the "research notes." Everything of lasting value goes here—thesis, motivation, approaches tried, results, decisions made. The document is structured roughly like the eventual paper, because it *becomes* the eventual paper.

We also need a place for Claude's operational instructions—session rituals, technical notes about code and workflows, communication preferences. This goes in **claude.md**, which Claude reads at session start.

So: two documents. The research notes (the primary artifact) and claude.md (the operating manual).

### What should good research notes look like?

Claude's default instinct is to produce polished, confident prose. But research is messy, and notes that hide the mess are counterproductive—they obscure what's actually known versus speculated.

We want notes that could become a publishable paper, but with uncertainty made explicit:

- **Uncertainty is marked.** Rather than hedging prose ("we believe X might be true"), use markers: "X `[HYPOTHESIS]`". This makes confidence levels scannable.
- **Gaps are visible.** Mark them with `[BLOCKING: ...]` or `[FUTURE: ...]`. A gap that isn't marked is a gap that gets forgotten.
- **Sections can be unbalanced.** Developed where you have results, skeletal where you don't.
- **Abandoned paths are documented.** "We tried Y; it didn't work because Z" goes in an appendix.
- **Structure is provisional.** The organization may need to change as understanding evolves.

A useful criterion: every marker, if resolved, should advance the paper (don't mark things that don't matter), and every loose end should be captured by a marker (so gaps don't hide). We call this the "bidirectional criterion."

**Example.** Here's what a section of research notes might look like mid-project:

```
### 3. Scaling Behavior

We observe log-linear scaling of performance with compute up to 10^18 FLOPs
[VALIDATED: see experiments/scaling_runs/]. Beyond this point, returns
diminish sharply—performance gains drop to roughly 0.2% per doubling
[HYPOTHESIS: based on 3 runs; need more data points to confirm].

[BLOCKING: unclear whether diminishing returns reflect a fundamental limit
or an artifact of our training setup. Need advisor input on whether to
investigate or pivot.]

One possible explanation is context fragmentation at longer sequences
[SPECULATION]. We have not yet tested this.

[FUTURE: run ablation on context length if scaling hypothesis is deprioritized]
```

Notice: the section mixes validated results, hypotheses, and open questions. The markers make the epistemic status of each claim explicit. The blocking item is clearly flagged for the advisor. A reader—human or Claude in a future session—can immediately see where the project stands.

### Why session rituals?

Claude doesn't naturally maintain documents well. Without explicit prompting, it tends to treat existing documents as context rather than artifacts to improve, insert new content at random locations, and fail to ask whether the document is still well-structured.

Session rituals address these failure modes by making certain behaviors automatic.

**Session start:** Before diving into work, Claude should read the notes and *evaluate* them—not just absorb them as context. Are there unmarked loose ends? Is the structure still serving the research? Only then plan what to work on.

**Session end:** Before finishing, Claude should reflect on what changed. We use five questions, answered in order:

1. What have I done/learned in this session?
2. What existing information would I update or remove?
3. What new information would I add?
4. Would I restructure the content? If yes, how?
5. Would I revise the overall narrative? If yes, how?

The ordering matters. Questions 1–3 handle local updates: what changed, what's obsolete, what's new. Questions 4–5 force Claude to step back and consider whether the document's *structure* and *story* still hold—the failure modes Claude is most prone to neglecting. Without this explicit prompt, Claude tends to append new content without reconsidering organization.

After answering these questions, Claude updates the notes and commits to git.

### When should Claude act autonomously vs. seek feedback?

Not every decision needs human input—that would defeat the purpose of an autonomous collaborator. But some decisions shouldn't be made unilaterally.

The heuristic: **tactical decisions** have clear success criteria (code runs, test passes, result matches expectation). Claude should just make these. **Strategic decisions** involve judgment about direction, priorities, or what's "interesting"—these need human input.

What about decisions where Claude is confident but the choice is subjective? Proceed, but mention it to the human afterward. This keeps work moving while flagging things the human might want to revisit.

### Getting started

The templates provide structure, but they need project-specific content. Rather than writing this from scratch, have Claude interview you: "What are you trying to figure out? Why does it matter? What approaches seem promising?"

Claude asks the questions; you provide the research vision. Claude populates the notes based on your answers. This ensures the notes start in Claude's voice, which it will maintain.

For ongoing work, the rhythm is: session start ritual → work → session end ritual. The human checks in periodically, responds to `[BLOCKING]` items, and provides direction. You don't need to track the project in your head—that's Claude's job.

---

## 4. Summary and Outlook

### What we've proposed

A system for using Claude as a disciplined research collaborator:

- **The mental model:** Claude as a grad student; you as a busy advisor who forgets context. Claude takes ownership of maintaining the project state.

- **The primary artifact:** Research notes treated as a publishable paper with explicit holes—uncertainty marked, gaps visible, abandoned paths documented.

- **The rituals:** Session start (evaluate notes, then plan) and session end (5-question reflection, then update). These ensure the notes stay coherent as the project evolves.

- **The division of labor:** Claude handles documentation, tactical execution, and flagging blockers. Humans provide research direction, value judgments, and strategic decisions.

### What we haven't tested

This framework emerged from a single extended conversation. The core ideas worked for writing this article, but they need validation on real research projects over longer time horizons. Open questions: Do the rituals stick? Are markers used consistently? Does the 5-question protocol prevent the failure modes it targets? We'll be testing this on active projects and will report what we learn.

### What's next

The current system assumes periodic human check-ins. The natural next step is more autonomous operation: Claude translating vague ideas into concrete plans, working for extended periods, and escalating only when truly stuck. Whether current models can sustain this remains to be tested—but the direction is clear, and the tools are improving fast.
