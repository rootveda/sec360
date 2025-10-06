# 🔄 Sec360 Git Workflow Example

## 📋 **Standard Development Workflow**

### **1. Check Current Status**
```bash
# See what files have changed
git status

# See detailed changes
git diff
```

### **2. Make Your Changes**
```bash
# Edit files as needed
# Test your changes
# Ensure all features work correctly
```

### **3. Stage Changes**
```bash
# Stage all changes
git add .

# Or stage specific files
git add core/practice_session_manager.py
git add README.md
```

### **4. Commit with Descriptive Message**
```bash
git commit -m "🔧 MAJOR FIX: Automatic Detailed Session Creation & Risk Viewer Display

✅ Fixed Issues:
- Automatic detailed session file creation during session end
- Risk viewer now displays correct data (Total Lines, Final Score, Risk Level)
- Category breakdown with field/data calculations and multipliers
- Enhanced debug logging for troubleshooting

🔧 Technical Changes:
- Fixed _save_analysis_details() method to use passed final_metrics parameter
- Updated risk viewer to read data from correct JSON structure locations
- Enhanced cleanup scripts to handle detailed_sessions directory
- Added comprehensive debug logging throughout the flow

📊 Features Working:
- ✅ End Session button properly creates detailed session files
- ✅ Risk Score Details viewer shows correct calculations
- ✅ Category breakdown with PII, Medical, HEPA, API/Security data
- ✅ Field and data point calculations with multipliers
- ✅ Session timeout and manual end both work correctly

🎯 Impact:
- Users now see complete risk analysis breakdown
- Detailed session files automatically created for all sessions
- Risk viewer displays accurate field counts and calculations
- Enhanced debugging capabilities for future maintenance"
```

### **5. Push to GitHub**
```bash
# Push to main branch
git push origin main

# Or push to feature branch
git push origin feature-branch-name
```

## 🚀 **Feature Development Workflow**

### **1. Create Feature Branch**
```bash
# Create and switch to new branch
git checkout -b feature/enhanced-risk-viewer

# Or from main branch
git checkout main
git checkout -b feature/automatic-session-creation
```

### **2. Develop Feature**
```bash
# Make your changes
# Test thoroughly
# Update documentation
# Commit frequently with descriptive messages
```

### **3. Merge Back to Main**
```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge feature branch
git merge feature/enhanced-risk-viewer

# Push merged changes
git push origin main

# Delete feature branch (optional)
git branch -d feature/enhanced-risk-viewer
```

## 🔧 **Hotfix Workflow**

### **1. Create Hotfix Branch**
```bash
# From main branch
git checkout main
git checkout -b hotfix/fix-session-creation-bug
```

### **2. Fix Issue**
```bash
# Make minimal changes to fix the issue
# Test the fix thoroughly
# Commit the fix
git commit -m "🐛 HOTFIX: Fix session creation bug

- Fixed AttributeError in _save_analysis_details method
- Corrected parameter passing in end_session flow
- Added debug logging for troubleshooting
- Verified fix works for all session end scenarios"
```

### **3. Merge and Deploy**
```bash
# Merge hotfix to main
git checkout main
git merge hotfix/fix-session-creation-bug
git push origin main

# Clean up
git branch -d hotfix/fix-session-creation-bug
```

## 📚 **Documentation Updates**

### **When to Update Documentation**
- After adding new features
- After fixing major bugs
- After changing user-facing functionality
- When updating dependencies or requirements

### **Files to Update**
- `README.md` - Main project overview
- `HOW_TO_RUN.md` - Setup and usage instructions
- `FEATURES_AND_FUNCTIONALITY.md` - Complete feature documentation
- `UPLOAD_GUIDE.md` - Upload and deployment guide

### **Example Documentation Commit**
```bash
git commit -m "📚 Update Documentation for v2.1.0

✅ Updated Files:
- README.md: Added recent updates section
- HOW_TO_RUN.md: Added new features and troubleshooting
- FEATURES_AND_FUNCTIONALITY.md: Updated with enhanced viewers
- UPLOAD_GUIDE.md: Reflected current project state

🔧 Changes:
- Added automatic detailed session creation documentation
- Updated risk viewer feature descriptions
- Added enhanced debugging capabilities
- Updated cross-platform compatibility notes

📊 Impact:
- Users have accurate documentation for all features
- Setup instructions reflect current functionality
- Feature descriptions match actual implementation"
```

## 🎯 **Best Practices**

### **Commit Messages**
- Use descriptive, clear messages
- Include emoji for visual clarity
- Break down complex changes into sections
- Mention impact and benefits

### **Branch Naming**
- `feature/feature-name` - New features
- `hotfix/issue-description` - Bug fixes
- `docs/documentation-update` - Documentation changes
- `refactor/component-name` - Code refactoring

### **Testing Before Commit**
- Test all functionality works
- Verify cross-platform compatibility
- Check documentation is accurate
- Ensure no breaking changes

### **Regular Maintenance**
```bash
# Weekly cleanup
git gc --prune=now

# Check for large files
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | sed -n 's/^blob //p' | sort --numeric-sort --key=2 | tail -10

# Update dependencies
pip install --upgrade -r requirements.txt
git add requirements.txt
git commit -m "📦 Update dependencies"
```

---

**Happy coding! 🚀**
