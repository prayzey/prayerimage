# Prayer Image Generator

A web application that generates beautiful prayer images with customizable text and scripture references.

## Features

- Generate prayer images with custom text
- Automatic scripture reference detection
- Prayer number detection
- Beautiful gradient backgrounds
- Mobile-friendly web interface

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask development server:
```bash
python app.py
```

3. Open http://localhost:5000 in your browser

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

## GitHub Setup

1. Create a new repository on GitHub
2. Initialize git and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Technology Stack

- Flask (Python web framework)
- Pillow (Image processing)
- NumPy (Numerical computations)
- TailwindCSS (Styling)
