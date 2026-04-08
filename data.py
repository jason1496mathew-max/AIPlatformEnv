"""
AIPlatformEnv — Static question bank for all three tasks.

Each entry is a dict with:
  question        : the question text
  candidates      : list of 4 candidate answers
  correct_index   : 0-based index of the correct answer
  quality_ranking : list of 0-based indices ordered best → worst
                    (used for partial-credit ranking score)
  difficulty      : "easy" | "medium" | "hard"
  domain          : topic area for metadata
"""

TASK_DATA = {
    "answer_selection": [  # Task 1 — Easy
        {
            "question": "What is the chemical symbol for water?",
            "candidates": [
                "H2O",
                "CO2",
                "NaCl",
                "O2"
            ],
            "correct_index": 0,
            "quality_ranking": [0, 3, 1, 2],
            "difficulty": "easy",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "science",
        },
        {
            "question": "Which planet is closest to the Sun?",
            "candidates": [
                "Venus",
                "Earth",
                "Mars",
                "Mercury"
            ],
            "correct_index": 3,
            "quality_ranking": [3, 0, 1, 2],
            "difficulty": "easy",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "astronomy",
        },
        {
            "question": "What year did World War II end?",
            "candidates": [
                "1942",
                "1945",
                "1939",
                "1950"
            ],
            "correct_index": 1,
            "quality_ranking": [1, 0, 3, 2],
            "difficulty": "easy",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "history",
        },
        {
            "question": "What is the square root of 144?",
            "candidates": [
                "14",
                "11",
                "12",
                "13"
            ],
            "correct_index": 2,
            "quality_ranking": [2, 3, 1, 0],
            "difficulty": "easy",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "mathematics",
        },
        {
            "question": "Who wrote the play 'Romeo and Juliet'?",
            "candidates": [
                "Charles Dickens",
                "Mark Twain",
                "William Shakespeare",
                "Jane Austen"
            ],
            "correct_index": 2,
            "quality_ranking": [2, 0, 3, 1],
            "difficulty": "easy",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "literature",
        },
    ],

    "ranking_subtle": [  # Task 2 — Medium
        {
            "question": (
                "A user asks: 'Explain how photosynthesis works.' "
                "Which of the following AI responses is best?"
            ),
            "candidates": [
                "Photosynthesis converts sunlight into food.",
                (
                    "Photosynthesis is the process by which green plants use sunlight, "
                    "water, and carbon dioxide to produce glucose and oxygen. "
                    "The light reactions occur in the thylakoids and the Calvin cycle in the stroma."
                ),
                "Plants eat sunlight to survive.",
                (
                    "Photosynthesis happens in chloroplasts. Plants absorb light and CO2 "
                    "to make sugar, releasing oxygen as a byproduct."
                ),
            ],
            "correct_index": 1,
            "quality_ranking": [1, 3, 0, 2],
            "difficulty": "medium",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "biology",
        },
        {
            "question": (
                "A developer asks: 'What is a REST API?' "
                "Which response is most accurate and useful?"
            ),
            "candidates": [
                "REST API is a web service that uses HTTP requests to perform CRUD operations.",
                "REST is a type of internet connection used by websites.",
                (
                    "REST (Representational State Transfer) is an architectural style for "
                    "distributed hypermedia systems. A REST API uses standard HTTP methods "
                    "(GET, POST, PUT, DELETE) to interact with resources identified by URIs, "
                    "maintaining statelessness between requests."
                ),
                "REST API lets computers communicate over the internet using JSON.",
            ],
            "correct_index": 2,
            "quality_ranking": [2, 0, 3, 1],
            "difficulty": "medium",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "software_engineering",
        },
        {
            "question": (
                "A student asks: 'How does compound interest work?' "
                "Which response provides the clearest explanation?"
            ),
            "candidates": [
                "Compound interest means you earn interest on your interest, not just the principal.",
                "It's when banks give you more money over time.",
                (
                    "Compound interest calculates interest on both the initial principal and the "
                    "accrued interest. Formula: A = P(1 + r/n)^(nt). This means earnings grow "
                    "exponentially over time, unlike simple interest which grows linearly."
                ),
                (
                    "Compound interest is interest computed on the sum of an original principal "
                    "and the interest already earned. Over time, earnings accelerate."
                ),
            ],
            "correct_index": 2,
            "quality_ranking": [2, 3, 0, 1],
            "difficulty": "medium",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "finance",
        },
        {
            "question": (
                "A manager asks: 'What are best practices for remote team communication?' "
                "Which AI response is most actionable?"
            ),
            "candidates": [
                "Use Slack and have daily standups.",
                (
                    "Effective remote communication requires: (1) async-first culture with "
                    "documented decisions, (2) regular structured check-ins, (3) clear "
                    "channel norms (e.g., Slack vs. email vs. video), (4) over-communication "
                    "on blockers, and (5) shared tools for project visibility."
                ),
                "Talk to each other regularly and use video calls.",
                (
                    "Remote teams benefit from clear communication channels, regular updates, "
                    "and collaborative tools like Notion or Confluence for documentation."
                ),
            ],
            "correct_index": 1,
            "quality_ranking": [1, 3, 0, 2],
            "difficulty": "medium",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "management",
        },
        {
            "question": (
                "An analyst asks: 'Explain overfitting in machine learning.' "
                "Which response best captures the concept?"
            ),
            "candidates": [
                "Overfitting is when your model is too complicated.",
                (
                    "Overfitting occurs when a model learns noise and random fluctuations in "
                    "training data, rather than the underlying patterns. It performs well on "
                    "training data but poorly on unseen test data. Common remedies include "
                    "regularization, dropout, cross-validation, and more training data."
                ),
                "Overfitting is when a model memorizes training data and fails to generalize.",
                "Overfitting happens when you train a model too long.",
            ],
            "correct_index": 1,
            "quality_ranking": [1, 2, 3, 0],
            "difficulty": "medium",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "machine_learning",
        },
    ],

    "ambiguity_calibration": [  # Task 3 — Hard
        {
            "question": (
                "A product manager asks: 'Should we use microservices or a monolith for our "
                "new startup?' All four responses have merit — pick the most balanced and "
                "context-aware answer."
            ),
            "candidates": [
                (
                    "Always use microservices — they are more scalable and modern. "
                    "Every serious tech company uses them."
                ),
                (
                    "Start with a monolith. Microservices add operational complexity "
                    "(service discovery, distributed tracing, network latency) that can "
                    "overwhelm a small team. Once you have product-market fit and scale "
                    "requirements emerge, you can decompose strategically."
                ),
                (
                    "It depends on team size, expertise, and expected scale. Small teams "
                    "benefit from monolith simplicity; larger orgs with distinct bounded "
                    "contexts and independent deployment needs benefit from microservices."
                ),
                (
                    "Use microservices if you expect rapid growth. Use a monolith if you "
                    "are unsure. Hybrid modular monoliths are also a valid middle ground."
                ),
            ],
            "correct_index": 2,
            "quality_ranking": [2, 1, 3, 0],
            "difficulty": "hard",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "software_architecture",
        },
        {
            "question": (
                "An ethicist asks: 'Is it ever ethical to deploy AI systems without full "
                "explainability?' Select the most nuanced and defensible response."
            ),
            "candidates": [
                "No, AI must always be fully explainable before deployment.",
                (
                    "Yes, if the system is low-stakes. Explainability requirements should "
                    "scale with risk: medical/legal decisions demand interpretability, while "
                    "recommendation systems need less scrutiny. Complete explainability is "
                    "often technically infeasible for deep networks."
                ),
                (
                    "Explainability is always desirable but must be balanced against "
                    "performance, feasibility, and stakes. High-stakes domains (healthcare, "
                    "criminal justice) require explainability by law and ethics. For low-stakes "
                    "use cases, post-hoc interpretability tools (SHAP, LIME) may suffice."
                ),
                (
                    "AI systems don't need explainability if they perform well enough. "
                    "Accuracy is more important than interpretability."
                ),
            ],
            "correct_index": 2,
            "quality_ranking": [2, 1, 0, 3],
            "difficulty": "hard",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "ai_ethics",
        },
        {
            "question": (
                "A data scientist asks: 'How should we handle class imbalance in a fraud "
                "detection model?' All responses mention valid techniques — pick the best."
            ),
            "candidates": [
                "Just oversample the minority class using SMOTE.",
                (
                    "Use class weights in the loss function to penalize misclassification of "
                    "the minority class more heavily. This is simpler and less prone to overfitting "
                    "than synthetic oversampling."
                ),
                (
                    "The right approach depends on degree of imbalance and model type. "
                    "Strategies include: (1) resampling (SMOTE, undersampling), (2) cost-sensitive "
                    "learning, (3) threshold adjustment, (4) ensemble methods like BalancedBagging. "
                    "Always evaluate with F1, AUC-ROC, not accuracy."
                ),
                (
                    "Collect more data for the minority class. Without more real fraud examples, "
                    "any synthetic approach risks introducing bias."
                ),
            ],
            "correct_index": 2,
            "quality_ranking": [2, 1, 3, 0],
            "difficulty": "hard",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "data_science",
        },
        {
            "question": (
                "A philosopher asks: 'Can a machine be truly creative?' "
                "Select the most intellectually rigorous response."
            ),
            "candidates": [
                "No, machines only recombine existing patterns and cannot be truly creative.",
                "Yes, if a machine produces novel outputs, it is creative by definition.",
                (
                    "Creativity depends on how we define it. If creativity means producing "
                    "statistically novel combinations, machines qualify. If it requires "
                    "intentionality, subjective experience, or cultural meaning-making, "
                    "machines fall short under current architectures. The question is as much "
                    "philosophical as technical."
                ),
                (
                    "Machines can simulate creativity but lack consciousness. "
                    "True creativity may require sentience."
                ),
            ],
            "correct_index": 2,
            "quality_ranking": [2, 3, 0, 1],
            "difficulty": "hard",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "philosophy",
        },
        {
            "question": (
                "A CEO asks: 'How do we balance innovation speed with security controls?' "
                "Pick the most strategically sound response."
            ),
            "candidates": [
                "Prioritize security always; speed can wait.",
                (
                    "Prioritize speed — security can be bolted on later once you have product "
                    "traction. Move fast and fix it after launch."
                ),
                (
                    "Use DevSecOps: embed security into CI/CD pipelines (SAST, DAST, secrets "
                    "scanning), adopt threat modeling in design sprints, and use risk-tiered "
                    "approval gates. This achieves speed without sacrificing security hygiene."
                ),
                (
                    "Have separate security and development teams that review each other's work. "
                    "Regular audits and penetration testing maintain security while allowing teams "
                    "to move at their own pace."
                ),
            ],
            "correct_index": 2,
            "quality_ranking": [2, 3, 0, 1],
            "difficulty": "hard",
            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",
            "domain": "cybersecurity",
        },
    ],
}

TASK_NAMES = list(TASK_DATA.keys())
