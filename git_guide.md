# ClannAI Git Workflow Guide

Our goal is to keep our project history clean and easy to follow. We do this by working on features in separate **branches**. Never commit directly to `master`.

---

## The 3 Main Stages of Development

1.  **Starting a New Task**
2.  **Working on Your Task**
3.  **Finishing Your Task**

---

### 1. Starting a New Task

**Goal:** Create a fresh, up-to-date branch for your new feature.

**Commands:**
```bash
# 1. Get the latest project history
git fetch origin

# 2. Create your new branch from the latest version of master
git checkout -b your-branch-name origin/master
```
> **What this does:** This ensures you are starting your work from the most recent version of the main project.

---

### 2. Working on Your Task

**Goal:** Save your progress and keep your branch in sync with `master` as you work.

**A. Save Your Progress (Commit Early, Commit Often)**

As you complete small, logical chunks of work, save them to your branch's history.
```bash
# See what you've changed
git status

# Add the files you've changed
git add .

# Save them with a clear message that explains the change
git commit -m "feat: Describe the change you made"
```

**B. Stay Up-to-Date with `master`**

At least once a day, sync your branch with the latest changes from `master`.
```bash
# This command automatically syncs and cleans up your branch history
git pull --rebase origin master
```
> **What this does:** This is the safest way to keep your branch updated. It takes the latest `master` and neatly places your commits on top of it. If you have local, uncommitted changes, you may need to `git stash` before this step.

---

### 3. Finishing Your Task

**Goal:** Finalize your work and merge it into the main project. There are two paths for this: the recommended **Pull Request (PR)** path and the **Direct Push** path.

---
#### **Path A: The Recommended Workflow (via Pull Request)**
This is the standard for team collaboration, as it includes a code review step.

**1. Final Review and Commit**

Before you share your work, make sure everything is saved and committed.
```bash
# See the final status of your branch
git status

# Add any last-minute changes
git add .

# Create your final commit
git commit -m "feat: A summary of the completed feature"
```

**2. Final Sync with `master`**

Do one last sync to ensure your branch has the absolute latest changes from `master`.
```bash
git pull --rebase origin master
```

**3. Push Your Branch**

Upload your completed feature branch to the remote repository.
```bash
git push -u origin your-branch-name
```

**4. Open and Merge the Pull Request**

Go to GitHub to create a **Pull Request (PR)** to merge your branch into `master`. This allows teammates to review the changes before they are integrated. Once approved, the PR is merged.

---
#### **Path B: The Direct Push Workflow (Use With Caution)**

This workflow bypasses the code review step and should only be used in specific cases.

**When to Use It:**
*   You are the sole developer on the project.
*   You are making a trivial change (e.g., fixing a typo) and the team agrees a PR is not necessary.

**The Workflow:**
```bash
# 1. After committing your work on your branch, switch to master
git checkout master

# 2. Get the latest version of master
git pull origin master

# 3. Merge your feature branch into it
git merge your-branch-name

# 4. Push the newly updated master branch
git push origin master
```

---
This guide provides flexible options for both robust team collaboration and rapid individual contributions. 