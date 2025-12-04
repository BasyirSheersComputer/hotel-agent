# Git Workflow Guide - v1.0 to v2.0 Migration

## Step 1: Approve Pending Commit ✋ (WAITING)

**STATUS**: There is a pending git commit command waiting for your approval in Antigravity.

**Command**:
```bash
git commit -m "v1.0.0: Stable single-tenant build with dashboard and metrics..."
```

**To Approve**:
- Look for the approval prompt in Antigravity's UI
- Click "Approve" or "Run" to execute the commit

**Alternative (Manual)**:
If the approval dialog is not visible, you can run manually:
```bash
cd d:\Priv\hotel-agent
git status  # Verify files are staged
git commit -m "v1.0.0: Stable single-tenant build with dashboard and metrics

Features:
- Hybrid intelligence (RAG + Google Maps)
- 100% query routing accuracy  
- Performance analytics dashboard
- Real-time metrics tracking
- Chat-dashboard integration
- Cloud-deployable

Complete system specification in SYSTEM_SPEC_V1.0.md"
```

---

## Step 2: Tag the Release (NEXT)

Once commit is approved/completed:

```bash
git tag -a v1.0.0 -m "Resort Genius v1.0.0 - Stable Single-Tenant Build"
git tag  # Verify tag created
```

---

## Step 3: Push to Remote (NEXT)

```bash
git push origin main
git push origin v1.0.0  # Push the tag
```

---

## Step 4: Create v2.0 Development Branch (NEXT)

```bash
git checkout -b feature/v2-saas
git push -u origin feature/v2-saas
```

---

## Step 5: Verify Branch Setup (NEXT)

```bash
git branch  # Should show: main and feature/v2-saas (with * on feature/v2-saas)
git log --oneline -1  # Should show v1.0.0 commit
```

---

## Branch Strategy

### `main` branch (v1.0.x)
- **Purpose**: Stable single-tenant production releases
- **Protection**: Only bug fixes and minor enhancements
- **Documentation**: SYSTEM_SPEC_V1.0.md (frozen reference)

### `feature/v2-saas` branch (v2.0.x)  
- **Purpose**: Multi-tenant SaaS development
- **Changes**: Breaking changes allowed, major refactoring
- **Documentation**: SYSTEM_SPEC_V2.0.md (new architecture)

### Merging Strategy
- v1.x hotfixes can be cherry-picked to v2.0 branch if applicable
- v2.0 will NOT merge back to main (different architecture)
- When v2.0 is stable, it becomes the new `main` and v1.0 moves to `legacy/v1` branch

---

## After Branching Complete

You'll be on `feature/v2-saas` branch and ready to:
1. Continue Phase 3 implementation (auth, chat history, admin dashboard, multi-language)
2. All new v2.0 files will be in this branch
3. v1.0 remains safe on `main` branch for rollback

---

**CURRENT STATUS**: Waiting for Step 1 approval
**ONCE APPROVED**: I will automatically execute Steps 2-5
