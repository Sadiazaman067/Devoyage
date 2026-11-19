
CAREER_PATHS = [
    {
        "slug": "software_engineering",
        "title": "Software Engineering",
        "summary": (
            "Software engineers design, build, test, and maintain "
            "applications and systems that solve real-world problems."
        ),
        "day_to_day": (
            "A typical week involves writing code, fixing bugs, "
            "reviewing teammates' changes, and testing features. "
            "Engineers also collaborate to plan improvements "
            "and understand user needs."
        ),
        "skills": [
            "Python or JavaScript",
            "Data structures and algorithms",
            "Git and GitHub",
            "Debugging and testing",
            "Problem-solving and teamwork"
        ],
        "first_steps": [
            "Learn Python fundamentals and practice writing functions.",
            "Build a small project such as a task manager.",
            "Learn Git and publish your project on GitHub.",
            "Practice basic data structures and algorithms.",
            "Add tests and improve your project using feedback."
        ],
        "position": 1
    },
    {
        "slug": "data",
        "title": "Data Science and Analytics",
        "summary": (
            "Data professionals collect, clean, analyze, and interpret "
            "information to help organizations make better decisions."
        ),
        "day_to_day": (
            "A typical week involves exploring datasets, writing SQL "
            "queries, creating visualizations, and identifying trends. "
            "Data professionals also communicate findings through "
            "reports and presentations."
        ),
        "skills": [
            "Python and SQL",
            "Statistics and probability",
            "Data cleaning",
            "Pandas and visualization",
            "Analytical communication"
        ],
        "first_steps": [
            "Learn Python basics and introductory statistics.",
            "Practice SQL queries using a sample database.",
            "Analyze a public dataset with Pandas.",
            "Create charts that explain your findings.",
            "Publish a data analysis project on GitHub."
        ],
        "position": 2
    },
    {
        "slug": "security",
        "title": "Cybersecurity",
        "summary": (
            "Cybersecurity professionals protect computer systems, "
            "networks, and information from threats and unauthorized access."
        ),
        "day_to_day": (
            "A typical week may include reviewing security alerts, "
            "investigating vulnerabilities, and checking system configurations. "
            "Security teams also document risks and recommend protections."
        ),
        "skills": [
            "Computer networking",
            "Linux fundamentals",
            "Python scripting",
            "Security principles",
            "Incident analysis"
        ],
        "first_steps": [
            "Learn how networks, operating systems, and HTTP work.",
            "Practice Linux commands in a virtual machine.",
            "Study authentication, encryption, and common vulnerabilities.",
            "Complete beginner security labs in authorized environments.",
            "Document what you learned in a GitHub repository."
        ],
        "position": 3
    },
    {
        "slug": "machine_learning",
        "title": "Machine Learning",
        "summary": (
            "Machine learning professionals develop systems that learn "
            "patterns from data to make predictions or support decisions."
        ),
        "day_to_day": (
            "A typical week involves preparing datasets, training models, "
            "evaluating results, and improving performance. "
            "Teams also investigate errors and consider how models "
            "will behave with new data."
        ),
        "skills": [
            "Python programming",
            "Linear algebra and calculus",
            "Probability and statistics",
            "Scikit-learn",
            "Model evaluation"
        ],
        "first_steps": [
            "Strengthen Python, algebra, and statistics fundamentals.",
            "Learn supervised learning and model evaluation concepts.",
            "Train a simple classifier using Scikit-learn.",
            "Compare model performance on a held-out test dataset.",
            "Publish a small machine learning project on GitHub."
        ],
        "position": 4
    }
]


RESOURCES = [
    # Learning
    {
        "title": "Harvard CS50",
        "url": "https://cs50.harvard.edu/x/",
        "category": "learning",
        "why": "Introduces programming, algorithms, and computer science fundamentals through practical assignments.",
        "is_free": 1,
        "position": 1,
    },
    {
        "title": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/",
        "category": "learning",
        "why": "Offers structured programming lessons and projects that beginners can complete at their own pace.",
        "is_free": 1,
        "position": 2,
    },
    {
        "title": "Google Machine Learning Crash Course",
        "url": "https://developers.google.com/machine-learning/crash-course",
        "category": "learning",
        "why": "Explains foundational machine learning concepts through lessons, visualizations, and exercises.",
        "is_free": 1,
        "position": 3,
    },

    # Practice
    {
        "title": "Exercism",
        "url": "https://exercism.org/",
        "category": "practice",
        "why": "Helps students improve programming skills through exercises and community feedback.",
        "is_free": 1,
        "position": 4,
    },
    {
        "title": "Kaggle Learn",
        "url": "https://www.kaggle.com/learn",
        "category": "practice",
        "why": "Provides hands-on exercises in Python, data analysis, and machine learning.",
        "is_free": 1,
        "position": 5,
    },
    {
        "title": "PortSwigger Web Security Academy",
        "url": "https://portswigger.net/web-security",
        "category": "practice",
        "why": "Teaches web security concepts through interactive labs in authorized practice environments.",
        "is_free": 1,
        "position": 6,
    },

    # Tools
    {
        "title": "Git",
        "url": "https://git-scm.com/",
        "category": "tools",
        "why": "Helps developers track code changes and collaborate safely on software projects.",
        "is_free": 1,
        "position": 7,
    },
    {
        "title": "Visual Studio Code",
        "url": "https://code.visualstudio.com/",
        "category": "tools",
        "why": "Provides a code editor with debugging, extensions, and integrated Git support.",
        "is_free": 1,
        "position": 8,
    },
    {
        "title": "Project Jupyter",
        "url": "https://jupyter.org/",
        "category": "tools",
        "why": "Supports interactive programming and data exploration using notebooks.",
        "is_free": 1,
        "position": 9,
    },

    # Communities
    {
        "title": "Stack Overflow",
        "url": "https://stackoverflow.com/",
        "category": "communities",
        "why": "Lets students learn from technical questions and answers shared by developers.",
        "is_free": 1,
        "position": 10,
    },
    {
        "title": "GitHub Community",
        "url": "https://github.com/orgs/community/discussions",
        "category": "communities",
        "why": "Connects students with discussions about GitHub workflows and software collaboration.",
        "is_free": 1,
        "position": 11,
    },
    {
        "title": "DEV Community",
        "url": "https://dev.to/",
        "category": "communities",
        "why": "Provides developer articles, project experiences, and opportunities to share technical knowledge.",
        "is_free": 1,
        "position": 12,
    },

    # Career
    {
        "title": "O*NET OnLine",
        "url": "https://www.onetonline.org/",
        "category": "career",
        "why": "Helps students explore occupations and understand the skills and tasks associated with each role.",
        "is_free": 1,
        "position": 13,
    },
    {
        "title": "Occupational Outlook Handbook",
        "url": "https://www.bls.gov/ooh/",
        "category": "career",
        "why": "Provides information about career responsibilities, education requirements, pay, and job outlook.",
        "is_free": 1,
        "position": 14,
    },
    {
        "title": "roadmap.sh",
        "url": "https://roadmap.sh/",
        "category": "career",
        "why": "Shows structured learning paths that help students identify skills needed for different technology roles.",
        "is_free": 1,
        "position": 15,
    },
]
