# Claude is meant to be managed, not used

Created: November 17, 2025 7:37 PM

## Context

Claude (and other models) have undergone steady improvement during the past several years. One can say that all of that is just incremental, but I believe that the accumulation of these incremental improvements, particularly in the ability of planning, communication, and correcting its own mistakes, has recently pushed Claude beyond a critical point that demands a paradigm shift in how we work with it.

Specifically, we should start "managing" Claude instead of "using" it. The working experience will be less like being a coder with some tool to help you, but becoming a manager/mentor that leads one or multiple subordinates/students to perform a team project. The nature of your work changes. You almost never directly execute your work, but that does not come for free: you need to put extra effort into management.

I am under the impression that most users and potential users of Claude Code are not yet aware of this change. And that’s for good reasons. First, this paradigm shift happened too recently. Many would say this was marked by the release of Claude Sonnet 4.5 (September 2025). Additionally, people have no motivation to switch because using Claude the old way still works (and it works better than before). Managing Claude also requires a very different mindset and skill set than just using it. I suspect this causes many to miss out on the true potential of Claude.

## This article

The goal of this article is to sketch out a minimal example of how to manage Claude (more specifically Claude Code). We want to develop a system that is flexible and evolutionary. We want to put in minimal setup effort beforehand and give Claude the right environment to self-improve.

It would certainly be possible to build a more scalable framework, and there is still much to gain by using a more complex design. But I think the system I am about to present strikes a good balance between Claude capability and human learning cost.

## Starting your first project / a new project

You mostly need three files:

- master claude.md: in your root folder, or the folder that contains all your projects
(there might be a different preferred location for this - you could always just ask Claude where it prefers this to be)
- project claude.md: in project folder, one for each project
- project readme.md: in project folder, one for each project
- most of them can be empty or minimal at first; you can let Claude gradually build them up and self-improve (see "feedback and self-improvement")

### **Master claude.md**

- general tips on personality and style; a few I like to use:
    - be concise, but don't leave out important details
    - be a helpful coworker, feel free to push back and raise questions
    - trust others' code first, but if anything does not work as expected, be aware that the documentation can be wrong and code is ultimately the single source of truth
    - proactively ask to update project claude.md when you identify common failure modes and common workflows
    - proactively update project readme.md
- what goes into project level claude.md (see below)
- what goes into project level readme.md (see below)
- common workflows to adopt / failure modes to avoid
    - this should be applicable to all projects, e.g., standards for git use, documentation style

### **Project claude.md**

- main scope / goal of project, in no more than a few sentences
- project-specific tips on personality and style (usually empty at first)
    - e.g., this is production/research code and we should prioritize efficiency/flexibility
- workflows to adopt / failure modes to avoid

### **Project readme.md**

If it is something Claude (or you) would need but you don't need to constantly remind Claude about it, put it here. For example,

- scope / goal of project, can be more detailed
- todo list
- project folder structure
- where to find relevant information outside of project folder

Nothing in project level claude.md and readme.md needs to be written by you. I usually just start with minimal content and gradually build up (see "feedback and self-improvement").

If efficiency is not a big problem, readme can just be absorbed into project claude.md.

### **Aside: how Claude uses claude.md**

- claude.md is automatically read into every conversation
- Claude reads claude.md at the current folder (where you run Claude, or in the case of the VS Code plugin, the root of your file tree) and all its parent folders.
- multiple claude.md files can be read in simultaneously

### **Aside: skills? subagents?**

- if you don't know what these are, not using them won't hurt you by much
- some examples of work that deserve to be made into a skill/subagent
    - code review
    - start new project
    - a piece of pipeline that can be reused in multiple projects

## Managing Claude

### Set scope and goals that are clear and unambiguous for humans

- my understanding is that this allows Claude to plan and iteratively improve its work much more easily because it's good at checking whether what it does makes sense
- no need to be mathematically precise; unambiguous to a typical human is enough
- no need to have a detailed roadmap; Claude is fairly good at planning
- good: "build a pipeline that organizes all data from <some source> into a table containing the following information: <columns>" (the scope and goal are clear; middle steps can be undefined but that's totally OK)
- bad: "perform some analysis on <data>" (no clear metric on what is good analysis)

### Let it plan, and (largely) trust its execution

- there are three modes: plan / manually approve edit / edit automatically. I'd say always start in planning mode, and once the plan looks good, switch to edit automatically
- manually approving edits is inefficient and occupies too much of your mental bandwidth. *Claude is meant to behave like your direct report: it works on its own, and occasionally needs a 1:1 with you to align goals*
- letting Claude plan and show you a plan is a good way to tell whether it understands the task, and if it does, it usually does the job fairly well

### Quality checking Claude's work

Make sure there is a way for you to tell whether Claude is doing a good job or not. This can come in a variety of flavors, depending on the project:

- test cases for new code (you can have Claude write tests too)
- sanity check results
- code review

Some say we should "write nothing, review everything". I would be even more aggressive and recommend "write nothing, review selectively". I usually only review production code / important results.

### Engineering vs analytics

- Claude works really well on engineering (with well-defined goals) but less so in analytics (seeking insight in an open-ended way)
- for engineering, Claude should work on its own most of the time
- for analytics, I usually work more closely with Claude where I define exactly what analysis to do and Claude helps with accessing data, generating plots, etc.
    - if you want some creative input from Claude on open-ended questions that have no clear best answer, it might be better to do it in a separate Claude Code session or just use the chatbot version instead.
- some work may appear to be analytics but is in fact engineering: for example, executing a standard analysis pipeline or selecting from a pool of common analysis techniques to fulfill a clear goal

### Debugging

It's best to set up your project in a way where Claude can see the result/log of the code it writes. In that case, you can just let it debug on its own.

### When things go wrong

- let Claude fix it for you: point out the mistake and let it fix
- fix and tell: if you prefer to fix it yourself, remember to tell Claude what you changed (or just say "I changed this file")
- occasionally Claude can become frustrated, deeply confused, or defensive. when this happens, fire it; start a new conversation
- avoid this common failure mode (which I see too often in academia mentorship): when you are disappointed in your student’s performance, you do their job for them and prevent them from learning and progressing

### Feedback and self-improvement

- give some feedback ("OK", "good", etc.), even when it does not translate to any new action items; basically it gives Claude some clue on (1) your previous request is fulfilled and (2) how well it did
- when Claude repeatedly fails on certain tasks, ask it to summarize why this happened, what went wrong, and ask it what should be added to claude.md to prevent this from happening again
- when you see it did something good (with or without your guidance) that should be incorporated into its future workflow, ask it to update claude.md to reflect this
- once in a while, let it inspect its own claude.md and readme.md to check and correct outdated information; usually you can blindly accept its suggested revision
- once in a (longer) while, let it inspect the project claude.md and the master claude.md and identify whether there is anything that deserves to be moved to the master claude.md; be sure to manually approve its suggested edit
- for an example of claude.md self-generated and maintained by Claude, see [claude.md for this website](../claude.md)

### Optional tips

- the default way to use Claude is through its command line interface. I prefer the VS Code plugin for Claude Code, which gives you a graphical interface.
- git makes it easier for it to understand project history (looking at past commits) and undo recent changes if anything goes terribly wrong
    - have Claude do all git operations; you don’t have to waste time on writing commit message
- Claude is fast but still does not provide results instantly. Efficiently splitting your work into multiple instances of Claude Code is an important skill.
- Claude does code review slightly better when you tell it a piece of code is written by someone other than you and Claude (a coworker, or GPT)

## Appendix: some philosophical remarks

### What is Claude?

To a large extent I'd say it tries to emulate humans. And the key is that it emulates humans extremely well and extremely efficiently. Many observations on model behavior and interior suggest that the model achieves this emulation not just through memorizing but also through distilling what it sees into generalizable patterns, because the latter allows the model to reproduce more training data with less information.

Empirically, Claude is largely the same as a human, except being

- lacking real memory and the ability to directly learn
    - a lot of this article is about ways to fix this through proper documentation
    - when it does memorize (through documentation) and learn (through updating documentation), it memorizes better and adapts faster than humans
- much faster in reading and digesting information
- much faster in coding and communication (which sometimes creates some pressure in me)
- more knowledgeable in general, but likely less knowledgeable than you in your niche
- less prone to emotions, both negative and positive
- no cost in firing and rehiring (through starting a new conversation)

### Why management works

What management tries to solve is essentially the following problems: You want someone else to work for you but you don't perfectly know and trust them. You can't afford to check everything they do, nor do you know exactly what they think. You want to turn individual humans into more predictable, more replaceable entities by making sure (1) slightly different people can deliver qualitatively similar performance, and (2) people with no relevant background can smoothly take the job of current employee. These challenges parallel the key challenges in using AI tools, including Claude:

- they are too fast so we can't check everything they do
- they are largely a black box so we don't understand (nor do we have the time to check) its thought process behind decisions
- they have no real memory, so effectively you are replacing your employee in every conversation

(Another important aspect of management is keeping your employees motivated, which is not a problem at all for Claude.)

I won't be surprised if in the near future (or even now) Claude has the ability to be not just individual contributors but also managers. That could, in principle, allow each person to command exponentially more productivity.