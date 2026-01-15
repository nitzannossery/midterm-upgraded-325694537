# Quick Setup - Git Remote Repository

## 🚀 הדרך המהירה להגדיר Remote Repository

### אופציה 1: שימוש בסקריפט (מומלץ)

```bash
cd "/Users/nitzannossery/Desktop/untitled folder"
./setup_remote.sh
```

הסקריפט ינחה אותך צעד אחר צעד.

---

### אופציה 2: הגדרה ידנית

#### שלב 1: צור Repository ב-GitHub

1. לך ל: **https://github.com/new**
2. שם Repository: `midterm-upgraded-325694537`
3. תיאור: `Financial Analysis Multi-Agent System with Comprehensive Evaluation Framework`
4. בחר: **Public** או **Private**
5. ⚠️ **אל תוסיף README** (כבר יש לנו)
6. לחץ: **"Create repository"**

#### שלב 2: העתק את ה-URL

GitHub יציג לך URL כמו:
```
https://github.com/YOUR_USERNAME/midterm-upgraded-325694537.git
```

#### שלב 3: הרץ את הפקודות

```bash
cd "/Users/nitzannossery/Desktop/untitled folder"

# הוסף remote
git remote add origin https://github.com/YOUR_USERNAME/midterm-upgraded-325694537.git

# דחוף את הקוד
git push -u origin main
```

#### שלב 4: בדוק

ה-URL שלך יהיה:
```
https://github.com/YOUR_USERNAME/midterm-upgraded-325694537
```

---

## 🔍 בדיקת Remote

לאחר ההגדרה, בדוק:

```bash
# צפה ב-remotes
git remote -v

# צפה ב-URL
git remote get-url origin
```

---

## 📋 פקודות שימושיות

### דחיפת שינויים:
```bash
git add .
git commit -m "Your message"
git push
```

### משיכת שינויים:
```bash
git pull
```

### עדכון remote URL:
```bash
git remote set-url origin <new-url>
```

### הסרת remote:
```bash
git remote remove origin
```

---

## ⚠️ פתרון בעיות

### בעיה: "repository not found"
- ודא שיצרת את ה-repository ב-GitHub
- ודא שה-URL נכון
- ודא שיש לך הרשאות

### בעיה: "authentication failed"
- הגדר SSH keys או credentials
- GitHub: Settings → SSH and GPG keys
- או השתמש ב-HTTPS עם Personal Access Token

### בעיה: "branch 'main' does not exist"
```bash
git branch -M main
git push -u origin main
```

---

## ✅ לאחר ההגדרה

1. **צפה ב-repository**: פתח את ה-URL בדפדפן
2. **שתף את הקישור**: עם אחרים
3. **המשך לעבוד**: `git add`, `git commit`, `git push`

---

## 🎯 סיכום

**לאחר שתצור repository ב-GitHub/GitLab/Bitbucket:**

1. העתק את ה-URL
2. הרץ: `git remote add origin <URL>`
3. הרץ: `git push -u origin main`
4. ✅ מוכן!

**הקישור שלך יהיה**: `https://github.com/YOUR_USERNAME/midterm-upgraded-325694537`

---

**צריך עזרה?** הרץ את `./setup_remote.sh` או עקוב אחר ההוראות למעלה.
