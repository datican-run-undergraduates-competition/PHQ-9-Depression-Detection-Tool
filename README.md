# PHQ-9-Depression-Detection-Tool
# PHQ-9 Mental Health Screening Tool

## Overview
This project is an advanced, multilingual PHQ-9 (Patient Health Questionnaire-9) mental health screening tool built with Streamlit and enhanced with AI capabilities. The application provides professional-grade depression screening in multiple languages, making mental health assessment more accessible to diverse communities.

## Key Features
- 🌐 Multilingual Support:
  - English
  - French
  - Yoruba
  - Igbo
  - Hausa

- 🤖 AI-Powered Analysis:
  - Personalized insights and recommendations
  - Context-aware response analysis
  - Professional-grade assessment summaries

- 📊 Comprehensive Assessment:
  - Standard PHQ-9 questionnaire
  - Real-time scoring
  - Severity level classification
  - Detailed response breakdown

- 🎯 User-Focused Design:
  - Intuitive interface
  - Mobile-responsive layout
  - Progress tracking
  - Encouraging messages throughout

- 🔒 Privacy & Security:
  - Secure data handling
  - No personal data storage
  - Private assessment experience

## Medical Features
- Professional depression screening using the validated PHQ-9 questionnaire
- Severity assessment levels:
  - Minimal (0-4)
  - Mild (5-9)
  - Moderate (10-14)
  - Severe (15-27)
- Crisis resources and professional recommendations
- Educational mental health resources

## Technical Stack
- Frontend: Streamlit
- AI Integration: Google Generative AI (Gemini)
- Styling: Custom CSS
- Language Support: Internationalization system

## Setup Requirements
1. Python 3.6 or higher
2. Streamlit
3. Google Generative AI package
4. Environment Variables:
   - GEMINI_API_KEY (for AI analysis features)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
1. Set up environment variables:
   ```bash
   export GEMINI_API_KEY='your-api-key'  # For Unix/Linux
   set GEMINI_API_KEY='your-api-key'     # For Windows
   ```

2. Run the application:
   ```bash
   streamlit run app.py
   ```

## Medical Disclaimer
This tool is for screening purposes only and does not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical decisions.

## Crisis Resources
- National Suicide Prevention Lifeline: 988 (US)
- Crisis Text Line: Text HOME to 741741
- International Crisis Centers: [IASP Crisis Centres](https://www.iasp.info/resources/Crisis_Centres/)

## License
[MIT License]

## Acknowledgments
- PHQ-9 screening tool developers
- Mental health professionals and organizations
- Open-source community contributors
