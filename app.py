import streamlit as st

# Configure page - MUST be the first Streamlit command
st.set_page_config(
    page_title="PHQ-9 Mental Health Screening",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import json
import datetime
from typing import Dict, List, Tuple
import os

# Try to import Google Generative AI with proper error handling
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    st.warning("⚠️ Google Generative AI package not installed properly. Running in fallback mode.")

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(180deg, #87CEEB 0%, #98FF98 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(180deg, #87CEEB 0%, #98FF98 100%);
    }
    
    .question-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .title-header {
        text-align: center;
        color: #333333;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #555555;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .progress-bar {
        background-color: #e0e0e0;
        border-radius: 10px;
        height: 10px;
        margin: 1rem 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #4682B4, #87CEFA);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    .encouragement-box {
        background: linear-gradient(135deg, #E8F4FD, #F0F8FF);
        border-left: 4px solid #4682B4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        font-style: italic;
        color: #2C3E50;
    }
    
    .result-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        margin: 1rem 0;
        text-align: center;
    }
    
    .severity-low { border-left: 6px solid #28a745; }
    .severity-mild { border-left: 6px solid #ffc107; }
    .severity-moderate { border-left: 6px solid #fd7e14; }
    .severity-severe { border-left: 6px solid #dc3545; }
    
    .nav-button {
        background: #4682B4;
        color: white;
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
    }
    
    .nav-button:hover {
        background: #87CEFA;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(70, 130, 180, 0.3);
    }
    
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .language-selector {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: white;
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0

# Language translations
TRANSLATIONS = {
    'English': {
        'title': 'PHQ-9 Mental Health Screening',
        'subtitle': 'Professional Depression Assessment Tool',
        'start_button': 'Start Assessment',
        'next_button': 'Next Question',
        'back_button': 'Previous Question',
        'submit_button': 'Complete Assessment',
        'home': 'Home',
        'about': 'About',
        'resources': 'Resources',
        'privacy_note': '🔒 Your data is encrypted and never shared without consent.',
        'encouragement_1': "You're taking an important step for your mental health. 💚",
        'encouragement_2': "Every question helps us understand how you're feeling. You're doing great! 🌟",
        'encouragement_3': "Remember, seeking help is a sign of strength, not weakness. 💪",
        'questions': [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed, or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead, or of hurting yourself"
        ],
        'options': ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        'result_title': 'Your PHQ-9 Assessment Results',
        'ai_analysis': 'AI Analysis and Recommendations',
        'score_display': 'Your PHQ-9 Score',
        'analyzing': '🤖 AI is analyzing your responses...',
        'personalized_analysis': 'Personalized Analysis',
        'response_breakdown': 'Response Breakdown',
        'professional_recommendations': 'Professional Recommendations',
        'take_again': 'Take Again',
        'view_resources': 'View Resources'
    },
    'French': {
        'title': 'Dépistage de Santé Mentale PHQ-9',
        'subtitle': 'Outil Professionnel d\'Évaluation de la Dépression',
        'start_button': 'Commencer l\'Évaluation',
        'next_button': 'Question Suivante',
        'back_button': 'Question Précédente',
        'submit_button': 'Terminer l\'Évaluation',
        'home': 'Accueil',
        'about': 'À Propos',
        'resources': 'Ressources',
        'privacy_note': '🔒 Vos données sont cryptées et jamais partagées sans consentement.',
        'encouragement_1': "Vous franchissez une étape importante pour votre santé mentale. 💚",
        'encouragement_2': "Chaque question nous aide à comprendre comment vous vous sentez. Vous faites du bon travail! 🌟",
        'encouragement_3': "Rappelez-vous, demander de l'aide est un signe de force, pas de faiblesse. 💪",
        'questions': [
            "Peu d'intérêt ou de plaisir à faire des choses",
            "Se sentir déprimé(e), triste ou désespéré(e)",
            "Difficultés à s'endormir ou à rester endormi(e), ou dormir trop",
            "Se sentir fatigué(e) ou avoir peu d'énergie",
            "Manque d'appétit ou manger trop",
            "Se sentir mal dans sa peau ou penser qu'on est un(e) raté(e) ou qu'on a déçu sa famille",
            "Difficultés à se concentrer sur des choses comme lire le journal ou regarder la télévision",
            "Bouger ou parler si lentement que d'autres personnes l'ont remarqué, ou au contraire être si agité(e) qu'on bouge beaucoup plus que d'habitude",
            "Penser qu'on serait mieux mort(e) ou penser à se faire du mal"
        ],
        'options': ['Jamais', 'Plusieurs jours', 'Plus de la moitié des jours', 'Presque tous les jours'],
        'result_title': 'Vos Résultats d\'Évaluation PHQ-9',
        'ai_analysis': 'Analyse IA et Recommandations',
        'score_display': 'Votre Score PHQ-9',
        'analyzing': '🤖 L\'IA analyse vos réponses...',
        'personalized_analysis': 'Analyse Personnalisée',
        'response_breakdown': 'Répartition des Réponses',
        'professional_recommendations': 'Recommandations Professionnelles',
        'take_again': 'Reprendre',
        'view_resources': 'Voir les Ressources'
    },
    'Yoruba': {
        'title': 'PHQ-9 Ayewo Ilera Opolo',
        'subtitle': 'Ohun Elo Alamọdaju fun Ayewo Ibanuje',
        'start_button': 'Bere Ayewo',
        'next_button': 'Ibeere To Tele',
        'back_button': 'Ibeere To Koja',
        'submit_button': 'Pari Ayewo',
        'home': 'Ile',
        'about': 'Nipa Wa',
        'resources': 'Awọn Ohun Elo',
        'privacy_note': '🔒 A ti fi ohun elo idena pamọ data rẹ, a ko pin si ẹnikẹni laisi ẹ gbọ.',
        'encouragement_1': "O n gbe igbesẹ pataki fun ilera ọpọlọ rẹ. 💚",
        'encouragement_2': "Gbogbo ibeere n ran wa lọwọ lati loye bi o ṣe rilara. O n ṣe daradara! 🌟",
        'encouragement_3': "Ranti pe, wiwa iranlọwọ jẹ ami agbara, kii ṣe ailera. 💪",
        'questions': [
            "Aifẹ tabi idunnu kekere ninu ṣiṣe awọn nkan",
            "Rilara aibalẹ, ibanuje, tabi ainireti",
            "Iṣoro lati sun tabi duro ninu oorun, tabi sisun pupọ ju",
            "Rilara arẹ tabi ni agbara kekere",
            "Ebi ko si tabi jijẹ pupọ ju",
            "Rilara buburu nipa ara ẹ tabi pe o jẹ asikuna tabi ti jẹ ki ẹbi rẹ ṣe tabi sofo",
            "Iṣoro lati kojuumọ si awọn nkan bi kika iwe iroyin tabi wiwo tẹlifisiọnu",
            "Gbigbe tabi sọrọ kia titi ti awọn eniyan miiran le ṣe akiyesi, tabi idakeji - jijẹ alarabara tabi ainisimi titi ti o ti n gbe ju iwọntunwọnsi",
            "Ero pe o yoo dara julọ ti o ba ku, tabi lati ṣe ara rẹ ni ipalara"
        ],
        'options': ['Rara', 'Ọjọ diẹ', 'Ju ọpọ ọjọ lọ', 'Fẹrẹẹ gbogbo ọjọ'],
        'result_title': 'Awọn Abajade Ayewo PHQ-9 Rẹ',
        'ai_analysis': 'Itupalẹ AI ati Awọn Iṣeduro',
        'score_display': 'Awọn Abajade PHQ-9 Rẹ',
        'analyzing': '🤖 AI n ṣe itupalẹ awọn idahun rẹ...',
        'personalized_analysis': 'Itupalẹ Ti ara ẹni',
        'response_breakdown': 'Ipin Awọn Idahun',
        'professional_recommendations': 'Awọn Iṣeduro Ọprofessionals',
        'take_again': 'Tun Gba',
        'view_resources': 'Wo Awọn Ohun Elo'
    },
    'Igbo': {
        'title': 'PHQ-9 Nyocha Ahụike Uche',
        'subtitle': 'Ngwa Ọkachamara Maka Nyocha Ịda Mba',
        'start_button': 'Malite Nyocha',
        'next_button': 'Ajụjụ Na-eso',
        'back_button': 'Ajụjụ Gara Aga',
        'submit_button': 'Mechaa Nyocha',
        'home': 'Ụlọ',
        'about': 'Gbasara Anyị',
        'resources': 'Ihe Ndị Dị Mkpa',
        'privacy_note': '🔒 Ezonọ data gị ma ọ dịghị onye anyị na-ekerịta ya na ya na-enweghị nkwenye gị.',
        'encouragement_1': "Ị na-eme nzọụkwụ dị mkpa maka ahụike uche gị. 💚",
        'encouragement_2': "Ajụjụ ọ bụla na-enyere anyị aka ịghọta otú ị na-eche. Ị na-eme nke ọma! 🌟",
        'encouragement_3': "Cheta na ịchọ enyemaka bụ ihe ngosi nke ike, ọ bụghị adịghị ike. 💪",
        'questions': [
            "Obere mmasị ma ọ bụ obi ụtọ n'ime ihe ndị na-eme",
            "Ịda mba, obi mwute, ma ọ bụ enweghị olileanya",
            "Nsogbu ịrahụ ụra ma ọ bụ ịnọgide na ụra, ma ọ bụ ihi ụra nke ukwuu",
            "Ike gwụ ma ọ bụ inwe obere ume",
            "Agụụ na-adịghị ma ọ bụ iri nri nke ukwuu",
            "Inwe mmetụta ọjọọ gbasara onwe gị ma ọ bụ iche na ị bụ onye dara ada ma ọ bụ meela ka ezinụlọ gị kwaa ákwá",
            "Nsogbu ilekwasị uche n'ihe ndị dị ka ịgụ akwụkwọ akụkọ ma ọ bụ ikiri telivishọn",
            "Ịkwagharị ma ọ bụ ikwu okwu nke nwayọọ nke na ndị ọzọ nwere ike ịchọpụta, ma ọ bụ ihe megidere ya - inwe nsogbu ma ọ bụ enweghị izu ike nke na ị na-akwagharị karịa ka ị na-emebu",
            "Echiche na ọ ga-aka mma ma ọ bụrụ na ị nwụọ, ma ọ bụ icheta imerụ onwe gị ahụ"
        ],
        'options': ['Ọ dịghị ma ọlị', 'Ụbọchị ole na ole', 'Ihe karịrị ọkara ụbọchị', 'Ihe fọrọ nke nta ka ọ bụrụ kwa ụbọchị'],
        'result_title': 'Nsonaazụ Nyocha PHQ-9 Gị',
        'ai_analysis': 'Nnyocha AI na Ntụziaka',
        'score_display': 'Nsonaazụ PHQ-9 Gị',
        'analyzing': '🤖 AI na-enyocha azịza gị...',
        'personalized_analysis': 'Nyocha Nkeonwe',
        'response_breakdown': 'Nkewa Azịza',
        'professional_recommendations': 'Nkwado Ọkachamara',
        'take_again': 'Weghachite',
        'view_resources': 'Lee Ihe Ndi Di Mkpa'
    },
    'Hausa': {
        'title': 'PHQ-9 Binciken Lafiyar Hankali',
        'subtitle': 'Kayan Aiki na Ƙwararru don Gwajin Baƙin Ciki',
        'start_button': 'Fara Gwaji',
        'next_button': 'Tambaya Ta Gaba',
        'back_button': 'Tambaya Ta Baya',
        'submit_button': 'Kammala Gwaji',
        'home': 'Gida',
        'about': 'Game da Mu',
        'resources': 'Kayan Aiki',
        'privacy_note': '🔒 An ɓoye bayananku kuma ba a raba su ba sai da amincewarku.',
        'encouragement_1': "Kuna ɗaukar muhimmin mataki don lafiyar hankalinku. 💚",
        'encouragement_2': "Kowace tambaya tana taimaka mana mu fahimci yadda kuke ji. Kuna yin kyau! 🌟",
        'encouragement_3': "Ku tuna cewa, neman taimako alama ce ta ƙarfi, ba rauni ba. 💪",
        'questions': [
            "Ƙarancin sha'awa ko jin daɗi wajen yin abubuwa",
            "Jin baƙin ciki, damuwa, ko rashin bege",
            "Matsala wajen yin barci ko ci gaba da barci, ko yin barci da yawa",
            "Jin gajiya ko samun ƙarancin kuzari",
            "Rashin ci ko cin abinci da yawa",
            "Jin mummunan abu game da kanku ko tunanin cewa kun gaza ko kun ba da kunya ga danginku",
            "Matsala wajen mai da hankali kan abubuwa kamar karanta jarida ko kallon talabijin",
            "Motsi ko yin magana a hankali har sauran mutane sun lura, ko akasin haka - zama marasa natsuwa ko damuwa har kun yi motsi fiye da yadda kuka saba",
            "Tunanin cewa zai fi kyau ku mutu, ko tunanin cutar da kanku"
        ],
        'options': ['Ba ko kaɗan', 'Kwanaki kaɗan', 'Fiye da rabin kwanaki', 'Kusan kowace rana'],
        'result_title': 'Sakamakon Gwajin PHQ-9 Naku',
        'ai_analysis': 'Bincike na AI da Shawarwari',
        'score_display': 'Sakamakon PHQ-9 Naku',
        'analyzing': '🤖 AI na nazarin amsoshin ku...',
        'personalized_analysis': 'Nazarin Musamman',
        'response_breakdown': 'Rarraba Amsoshi',
        'professional_recommendations': 'Shawarwari Masana',
        'take_again': 'Sake ɗauka',
        'view_resources': 'Duba Kayan Aiki'
    }
}

# Gemini API configuration (placeholder - user needs to add their API key)
def configure_gemini_api():
    """Configure Gemini API with error handling"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.warning("⚠️ Gemini API key not found. Please set the GEMINI_API_KEY environment variable for AI analysis.")
            return False
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.warning("⚠️ Error configuring Gemini API. Falling back to basic analysis.")
        return False

def get_ai_analysis(responses: Dict, total_score: int, language: str) -> str:
    """Get AI analysis using Gemini API with professional prompting"""
    # Check if Gemini is available
    if not GEMINI_AVAILABLE:
        return get_fallback_analysis(total_score, language)
        
    try:
        # Try to configure the API
        if not configure_gemini_api():
            return get_fallback_analysis(total_score, language)
            
        # Create the model and prepare response data
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare response data for analysis
            response_text = ""
            t = TRANSLATIONS[language]
            for i, response_score in responses.items():
                question = t['questions'][i]
                answer = t['options'][response_score]
                response_text += f"Q{i+1}: {question} - Answer: {answer} (Score: {response_score})\n"
            
            # Professional prompt for Gemini
            prompt = f"""
            You are a licensed clinical psychologist and mental health professional with expertise in depression assessment and the PHQ-9 screening tool. 

            PATIENT CONTEXT:
            - A patient has completed the PHQ-9 depression screening questionnaire
            - Total PHQ-9 Score: {total_score}/27
            - Language: {language}
            
            DETAILED RESPONSES:
            {response_text}
            
            INSTRUCTIONS:
            Please provide a professional, compassionate, and evidence-based analysis following these guidelines:

            1. **Professional Tone**: Write as a healthcare professional would - caring but clinical
            2. **Severity Assessment**: Based on standard PHQ-9 scoring:
               - 0-4: Minimal depression
               - 5-9: Mild depression  
               - 10-14: Moderate depression
               - 15-27: Severe depression
            
            3. **Key Elements to Include**:
               - Brief interpretation of the score in context
               - Identify specific symptom patterns from responses
               - Provide appropriate level of urgency for professional help
               - Suggest 2-3 specific, actionable next steps
               - Include reassurance and hope where appropriate
               
            4. **Important Limitations**:
               - Emphasize this is a screening tool, not a diagnosis
               - Recommend professional evaluation for definitive assessment
               - If score is 15+, emphasize urgency of professional help
               - If item 9 (self-harm thoughts) > 0, prioritize safety planning
            
            5. **Cultural Sensitivity**: 
               - Be mindful of cultural context for {language} speakers
               - Use appropriate, respectful language
               
            6. **Length**: Keep response to 150-200 words, clear and focused
            
            Please respond in {language} and provide professional mental health guidance appropriate for this PHQ-9 assessment.
            """
            
            # Generate response with timeout handling
            try:
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                st.warning(f"⚠️ AI analysis failed. Using fallback analysis.")
                return get_fallback_analysis(total_score, language)
                
        except Exception as e:
            st.warning("⚠️ Could not initialize AI model. Using fallback analysis.")
            return get_fallback_analysis(total_score, language)
            
    except Exception as e:
        st.warning("⚠️ AI analysis encountered an error. Using fallback analysis.")
        return get_fallback_analysis(total_score, language)

    # Final fallback if we somehow get here
    return get_fallback_analysis(total_score, language)

def get_fallback_analysis(total_score: int, language: str) -> str:
    """Fallback professional analysis when API is unavailable"""
    severity = get_severity_level(total_score)
    
    fallback_analysis = {
        'English': {
            'minimal': f"Your PHQ-9 score of {total_score} suggests minimal depression symptoms. This is encouraging! Continue maintaining healthy habits like regular exercise, good sleep, and social connections. Monitor your mood and don't hesitate to reach out for support if symptoms change.",
            'mild': f"Your PHQ-9 score of {total_score} indicates mild depression symptoms. Consider discussing your feelings with a healthcare provider. Focus on self-care activities, maintain regular routines, and consider counseling as a preventive measure.",
            'moderate': f"Your PHQ-9 score of {total_score} suggests moderate depression symptoms. It's important to seek professional help from a mental health provider or your primary care doctor. They can discuss treatment options including therapy and possibly medication.",
            'severe': f"Your PHQ-9 score of {total_score} indicates severe depression symptoms. Please seek immediate professional help. Contact your doctor, a mental health professional, or a crisis helpline. Effective treatments are available and can significantly improve how you feel."
        },
        'French': {
            'minimal': f"Votre score PHQ-9 de {total_score} suggère des symptômes de dépression minimaux. C'est encourageant! Continuez à maintenir des habitudes saines comme l'exercice régulier, un bon sommeil et des liens sociaux.",
            'mild': f"Votre score PHQ-9 de {total_score} indique des symptômes de dépression légère. Envisagez de parler de vos sentiments avec un professionnel de santé. Concentrez-vous sur les activités d'autosoins.",
            'moderate': f"Votre score PHQ-9 de {total_score} suggère des symptômes de dépression modérée. Il est important de chercher l'aide d'un professionnel de la santé mentale ou de votre médecin traitant.",
            'severe': f"Votre score PHQ-9 de {total_score} indique des symptômes de dépression sévère. Veuillez chercher une aide professionnelle immédiate. Contactez votre médecin ou une ligne d'assistance d'urgence."
        },
        'Yoruba': {
            'minimal': f"Aami PHQ-9 rẹ ti {total_score} fi han pe o ni awọn aami iba je kekere. Eyi jẹ́ ìmọ̀lára dáradára! Tẹsiwaju pẹlu awọn ìwà tó dára bii ìdárayá déédéé, oorun tó dára, àti ìbágbépọ̀.",
            'mild': f"Aami PHQ-9 rẹ ti {total_score} fi han pe o ni awọn aami iba je díẹ̀. Ro nipa sísọ̀rọ̀ nípa ìmọ̀lára rẹ pẹ̀lú oníṣègùn. Ṣe àkíyèsí ìtọ́jú ara rẹ.",
            'moderate': f"Aami PHQ-9 rẹ ti {total_score} fi han pe o ni awọn aami iba je àárín. O ṣe pàtàkì láti wá ìrànlọ́wọ́ ọ̀jọ́gbọ́n lọ́dọ̀ oníṣègùn ọpọlọ tàbí oníṣègùn rẹ.",
            'severe': f"Aami PHQ-9 rẹ ti {total_score} fi han pe o ni awọn aami iba je pupọ. Jọ̀wọ́ wá ìrànlọ́wọ́ ọ̀jọ́gbọ́n lẹ́sẹ̀kẹsẹ̀. Pe oníṣègùn rẹ tàbí nọ́mbà ìrànlọ́wọ́ pàjáwìrì."
        },
        'Igbo': {
            'minimal': f"Skọọ PHQ-9 gị nke {total_score} na-egosi na ị nwere mgbaàmà nke nweda mmụọ dị ala. Nke a na-agba ume! Gaa n'ihu na-edebe omume ahụike dị mma dị ka egwuregwu, ụra ọma, na mmekọrịta mmadụ.",
            'mild': f"Skọọ PHQ-9 gị nke {total_score} na-egosi na ị nwere mgbaàmà nke nweda mmụọ dị mfe. Chee banyere ịkọrọ onye nlekọta ahụike mmetụta gị. Chụọ anya na omume nlekọta onwe gị.",
            'moderate': f"Skọọ PHQ-9 gị nke {total_score} na-egosi na ị nwere mgbaàmà nke nweda mmụọ dị n'etiti. Ọ dị mkpa ịchọta enyemaka ọkachamara site n'aka onye na-ahụ maka ahụike uche ma ọ bụ dọkịta gị.",
            'severe': f"Skọọ PHQ-9 gị nke {total_score} na-egosi na ị nwere mgbaàmà nke nweda mmụọ dị ukwuu. Biko chọta enyemaka ọkachamara ozugbo. Kpọtụrụ dọkịta gị ma ọ bụ ahụ nke enyemaka mberede."
        },
        'Hausa': {
            'minimal': f"Tambarin PHQ-9 na {total_score} yana nuna alamun rashin kwarin hankali na ƙasa. Wannan yana ban ƙarfafa! Ci gaba da kiyaye al'adun lafiya kamar motsa jiki akai-akai, barci mai kyau, da haɗin kai.",
            'mild': f"Tambarin PHQ-9 na {total_score} yana nuna alamun rashin kwarin hankali na tsakiya. Ka yi tunani game da magana da likita game da yadda kake ji. Mai da hankali kan ayyukan kula da kanka.",
            'moderate': f"Tambarin PHQ-9 na {total_score} yana nuna alamun rashin kwarin hankali matsakaici. Yana da muhimmanci a nemi taimakon ƙwararru daga mai ba da lafiyar hankali ko likitanka.",
            'severe': f"Tambarin PHQ-9 na {total_score} yana nuna alamun rashin kwarin hankali mai tsanani. Da fatan za a nemi taimakon ƙwararru nan take. Tuntuɓi likitanka ko layin agaji na gaggawa."
        }
    }
    
    lang_analysis = fallback_analysis.get(language, fallback_analysis['English'])
    return lang_analysis.get(severity, lang_analysis['minimal'])

def get_severity_level(score: int) -> str:
    """Determine severity level based on PHQ-9 score"""
    if score <= 4:
        return 'minimal'
    elif score <= 9:
        return 'mild'
    elif score <= 14:
        return 'moderate'
    else:
        return 'severe'

def get_severity_info(score: int, language: str) -> Tuple[str, str, str]:
    """Get severity information including level, description, and CSS class"""
    severity = get_severity_level(score)
    
    severity_info = {
        'English': {
            'minimal': ('Minimal Depression', 'Your symptoms suggest minimal or no depression. Keep up the good work with self-care!', 'severity-low'),
            'mild': ('Mild Depression', 'Your symptoms suggest mild depression. Consider speaking with a healthcare provider.', 'severity-mild'),
            'moderate': ('Moderate Depression', 'Your symptoms suggest moderate depression. Professional help is recommended.', 'severity-moderate'),
            'severe': ('Severe Depression', 'Your symptoms suggest severe depression. Please seek immediate professional help.', 'severity-severe')
        },
        'French': {
            'minimal': ('Dépression Minimale', 'Vos symptômes suggèrent une dépression minimale ou inexistante. Continuez vos soins personnels!', 'severity-low'),
            'mild': ('Dépression Légère', 'Vos symptômes suggèrent une dépression légère. Envisagez de parler à un professionnel.', 'severity-mild'),
            'moderate': ('Dépression Modérée', 'Vos symptômes suggèrent une dépression modérée. Une aide professionnelle est recommandée.', 'severity-moderate'),
            'severe': ('Dépression Sévère', 'Vos symptômes suggèrent une dépression sévère. Cherchez une aide professionnelle immédiate.', 'severity-severe')
        },
        'Yoruba': {
            'minimal': ('Ìbànújẹ́ Kékeré', 'Àwọn àmì rẹ fi hàn pé o ní ìbànújẹ́ kékeré tàbí kò sí. Tẹ̀síwájú pẹ̀lú ìtọ́jú ara rẹ!', 'severity-low'),
            'mild': ('Ìbànújẹ́ Díẹ̀', 'Àwọn àmì rẹ fi hàn pé o ní ìbànújẹ́ díẹ̀. Rò ó láti bá oníṣègùn sọ̀rọ̀.', 'severity-mild'),
            'moderate': ('Ìbànújẹ́ Àárín', 'Àwọn àmì rẹ fi hàn pé o ní ìbànújẹ́ àárín. A dábàá ìrànlọ́wọ́ oníṣègùn.', 'severity-moderate'),
            'severe': ('Ìbànújẹ́ Púpọ̀', 'Àwọn àmì rẹ fi hàn pé o ní ìbànújẹ́ púpọ̀. Jọ̀wọ́ wá ìrànlọ́wọ́ oníṣègùn lẹ́sẹ̀kẹsẹ̀.', 'severity-severe')
        },
        'Igbo': {
            'minimal': ('Nweda Mmụọ Nta', 'Ọrịa gị na-egosi na ị nwere nweda mmụọ nta ma ọ bụ ọ dịghị. Gaa n\'ihu na-elekọta onwe gị!', 'severity-low'),
            'mild': ('Nweda Mmụọ Mfe', 'Ọrịa gị na-egosi na ị nwere nweda mmụọ mfe. Chee maka ịgwa dọkịta.', 'severity-mild'),
            'moderate': ('Nweda Mmụọ N\'etiti', 'Ọrịa gị na-egosi na ị nwere nweda mmụọ n\'etiti. Anyị na-atụ aro enyemaka ọkachamara.', 'severity-moderate'),
            'severe': ('Nweda Mmụọ Ukwuu', 'Ọrịa gị na-egosi na ị nwere nweda mmụọ ukwuu. Biko chọọ enyemaka ọkachamara ozugbo.', 'severity-severe')
        },
        'Hausa': {
            'minimal': ('Rashin Kwarin Hankalin Dan Kadan', 'Alamomin ka na nuna rashin kwarin hankali na ƙasa. Ci gaba da kula da kanka!', 'severity-low'),
            'mild': ('Rashin Kwarin Hankalin Sau-Sau', 'Alamomin ka na nuna rashin kwarin hankali sau-sau. Ka yi tunani ka yi magana da likita.', 'severity-mild'),
            'moderate': ('Rashin Kwarin Hankalin Matsakaici', 'Alamomin ka na nuna rashin kwarin hankali matsakaici. Ana ba da shawarar neman taimako na likita.', 'severity-moderate'),
            'severe': ('Rashin Kwarin Hankalin Gaske', 'Alamomin ka na nuna rashin kwarin hankali mai tsanani. Don Allah nemi taimakon likita nan take.', 'severity-severe')
        }
    }
    
    lang_info = severity_info.get(language, severity_info['English'])
    return lang_info.get(severity, lang_info['minimal'])

def save_response_data(responses: Dict, total_score: int, language: str):
    """Save response data (in a real app, this would save to a database)"""
    timestamp = datetime.datetime.now().isoformat()
    data = {
        'timestamp': timestamp,
        'language': language,
        'responses': responses,
        'total_score': total_score,
        'severity': get_severity_level(total_score)
    }
    # In a real application, save this to a secure database
    # For demo, we'll just store in session state
    if 'saved_responses' not in st.session_state:
        st.session_state.saved_responses = []
    st.session_state.saved_responses.append(data)

def show_language_selector():
    """Display language selector"""
    languages = list(TRANSLATIONS.keys())
    selected_lang = st.selectbox(
        "🌐 Language / Langue / Èdè / Asụsụ / Harshe",
        languages,
        index=languages.index(st.session_state.language),
        key="lang_selector"
    )
    
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

def show_home_page():
    """Display the home page"""
    t = TRANSLATIONS[st.session_state.language]
    
    st.markdown(f'<h1 class="title-header">{t["title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t["subtitle"]}</p>', unsafe_allow_html=True)
    
    # Navigation menu
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(t['home'], key="nav_home"):
            st.session_state.current_page = 'home'
    with col2:
        if st.button(t['about'], key="nav_about"):
            st.session_state.current_page = 'about'
    with col3:
        if st.button(t['resources'], key="nav_resources"):
            st.session_state.current_page = 'resources'
    with col4:
        if st.button("🔄 Reset", key="nav_reset"):
            # Reset all session state
            for key in list(st.session_state.keys()):
                if key not in ['language']:
                    del st.session_state[key]
            st.session_state.current_page = 'home'
            st.session_state.responses = {}
            st.session_state.current_question = 0
            st.session_state.total_score = 0
            st.rerun()
    
    # Main content based on current page
    if st.session_state.current_page == 'home':
        show_main_home_content(t)
    elif st.session_state.current_page == 'about':
        show_about_page(t)
    elif st.session_state.current_page == 'resources':
        show_resources_page(t)

def show_main_home_content(t):
    """Show main home page content"""
    st.markdown("""
    <div class="question-card">
        <h3>🧠 Professional Mental Health Assessment</h3>
        <p>The PHQ-9 is a widely used, validated tool for screening depression. It takes just a few minutes to complete and provides valuable insights into your mental health.</p>
        
        <h4>✨ What makes this tool special:</h4>
        <ul>
            <li>🤖 AI-powered analysis and personalized recommendations</li>
            <li>🌍 Multi-language support (English, French, Yoruba, Igbo, Hausa)</li>
            <li>🔒 Complete privacy and data security</li>
            <li>📱 Mobile-optimized experience</li>
            <li>💡 Educational resources and support information</li>
        </ul>
        
        <h4>🎯 This assessment is for you if:</h4>
        <ul>
            <li>You're experiencing changes in mood or energy</li>
            <li>You want to monitor your mental health</li>
            <li>Your healthcare provider recommended a depression screening</li>
            <li>You're seeking professional guidance on your mental wellness</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Encouragement message
    st.markdown(f"""
    <div class="encouragement-box">
        💚 Taking care of your mental health is just as important as taking care of your physical health. You're taking a positive step by being here.
    </div>
    """, unsafe_allow_html=True)
    
    # Start button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button(f"🚀 {t['start_button']}", key="start_assessment", use_container_width=True):
            st.session_state.current_page = 'questionnaire'
            st.session_state.current_question = 0
            st.session_state.responses = {}
            st.session_state.total_score = 0
            st.rerun()

def show_about_page(t):
    """Show about page"""
    st.markdown("""
    <div class="question-card">
        <h3>📋 About the PHQ-9 Assessment</h3>
        
        <h4>What is PHQ-9?</h4>
        <p>The Patient Health Questionnaire-9 (PHQ-9) is a multipurpose instrument for screening, diagnosing, monitoring and measuring the severity of depression. It's one of the most validated tools in mental health screening.</p>
        
        <h4>🎯 How it works:</h4>
        <ul>
            <li><strong>9 Questions:</strong> Based on the 9 DSM-IV criteria for depression</li>
            <li><strong>4-Point Scale:</strong> From "not at all" to "nearly every day"</li>
            <li><strong>Score Range:</strong> 0-27 points total</li>
            <li><strong>Severity Levels:</strong> Minimal (0-4), Mild (5-9), Moderate (10-14), Severe (15-27)</li>
        </ul>
        
        <h4>🤖 AI Enhancement:</h4>
        <p>Our tool uses advanced AI to provide personalized insights and recommendations based on your responses, making the assessment more meaningful and actionable.</p>
        
        <h4>🌍 Accessibility:</h4>
        <p>Available in multiple languages to serve diverse communities and ensure everyone can access mental health screening in their preferred language.</p>
        
        <h4>⚠️ Important Notes:</h4>
        <ul>
            <li>This tool is for screening purposes only</li>
            <li>It does not replace professional medical diagnosis</li>
            <li>Always consult with healthcare providers for proper evaluation</li>
            <li>If you're in crisis, seek immediate help</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_resources_page(t):
    """Show resources page"""
    st.markdown("""
    <div class="question-card">
        <h3>📚 Mental Health Resources</h3>
        
        <h4>🚨 Crisis Resources:</h4>
        <ul>
            <li><strong>National Suicide Prevention Lifeline:</strong> 988 (US)</li>
            <li><strong>Crisis Text Line:</strong> Text HOME to 741741</li>
            <li><strong>International Association for Suicide Prevention:</strong> <a href="https://www.iasp.info/resources/Crisis_Centres/">Find local crisis centers</a></li>
        </ul>
        
        <h4>🏥 Professional Help:</h4>
        <ul>
            <li>Talk to your primary care physician</li>
            <li>Contact a mental health professional</li>
            <li>Reach out to your local community health center</li>
            <li>Consider online therapy platforms (BetterHelp, Talkspace, etc.)</li>
        </ul>
        
        <h4>💪 Self-Care Strategies:</h4>
        <ul>
            <li><strong>Exercise:</strong> Regular physical activity can improve mood</li>
            <li><strong>Sleep:</strong> Maintain consistent sleep schedules</li>
            <li><strong>Nutrition:</strong> Eat balanced, nutritious meals</li>
            <li><strong>Social Connection:</strong> Stay connected with friends and family</li>
            <li><strong>Mindfulness:</strong> Practice meditation or deep breathing</li>
            <li><strong>Hobbies:</strong> Engage in activities you enjoy</li>
        </ul>
        
        <h4>📖 Educational Resources:</h4>
        <ul>
            <li><a href="https://www.nimh.nih.gov/health/topics/depression">National Institute of Mental Health - Depression</a></li>
            <li><a href="https://www.who.int/news-room/fact-sheets/detail/depression">World Health Organization - Depression Facts</a></li>
            <li><a href="https://www.nami.org/About-Mental-Illness/Mental-Health-Conditions/Depression">NAMI - Depression Information</a></li>
        </ul>
        
        <h4>📱 Mental Health Apps:</h4>
        <ul>
            <li><strong>Mood tracking:</strong> Daylio, Moodpath</li>
            <li><strong>Meditation:</strong> Headspace, Calm</li>
            <li><strong>Therapy:</strong> BetterHelp, Talkspace</li>
            <li><strong>Crisis support:</strong> Crisis Text Line app</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_questionnaire():
    """Display the PHQ-9 questionnaire"""
    t = TRANSLATIONS[st.session_state.language]
    current_q = st.session_state.current_question
    
    # Progress bar
    progress = (current_q + 1) / len(t['questions'])
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress * 100}%"></div>
    </div>
    <p style="text-align: center; color: #666; margin-bottom: 2rem;">
        Question {current_q + 1} of {len(t['questions'])}
    </p>
    """, unsafe_allow_html=True)
    
    # Show encouragement messages at specific points
    if current_q == 2:
        st.markdown(f'<div class="encouragement-box">{t["encouragement_1"]}</div>', unsafe_allow_html=True)
    elif current_q == 5:
        st.markdown(f'<div class="encouragement-box">{t["encouragement_2"]}</div>', unsafe_allow_html=True)
    elif current_q == 8:
        st.markdown(f'<div class="encouragement-box">{t["encouragement_3"]}</div>', unsafe_allow_html=True)
    
    # Question card
    question_header = {
        'English': 'Over the last 2 weeks, how often have you been bothered by:',
        'French': 'Au cours des 2 dernières semaines, à quelle fréquence avez-vous été gêné(e) par:',
        'Yoruba': 'Ni ọsẹ meji sẹyin, igba melo ni o ti ni wahala pẹlu:',
        'Igbo': 'N\'ime izu abụọ gara aga, ugboro ole ka ihe ndị a na-ewe gị oge:',
        'Hausa': 'A cikin sati biyu da suka wuce, sau nawa lamurran nan suka damu ka:'
    }
    
    st.markdown(f"""
    <div class="question-card">
        <h3>{question_header.get(st.session_state.language, question_header['English'])}</h3>
        <h2 style="color: #4682B4; margin: 1.5rem 0;">{t['questions'][current_q]}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Answer options
    selected_option = st.radio(
        "Select your answer:",
        options=range(len(t['options'])),
        format_func=lambda x: f"{t['options'][x]} ({x} points)",
        key=f"question_{current_q}",
        index=st.session_state.responses.get(current_q, 0)
    )
    
    # Store the response
    st.session_state.responses[current_q] = selected_option
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1,2,1])
    
    with col1:
        if current_q > 0:
            if st.button(f"⬅️ {t['back_button']}", key="back_btn"):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col3:
        if current_q < len(t['questions']) - 1:
            if st.button(f"{t['next_button']} ➡️", key="next_btn"):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button(f"✅ {t['submit_button']}", key="submit_btn"):
                # Calculate total score
                st.session_state.total_score = sum(st.session_state.responses.values())
                
                # Save response data
                save_response_data(st.session_state.responses, st.session_state.total_score, st.session_state.language)
                
                # Move to results page
                st.session_state.current_page = 'results'
                st.rerun()

def show_results():
    """Display the assessment results"""
    t = TRANSLATIONS[st.session_state.language]
    score = st.session_state.total_score
    
    # Get severity information
    severity_title, severity_desc, severity_class = get_severity_info(score, st.session_state.language)
    
    st.markdown(f'<h1 class="title-header">{t["result_title"]}</h1>', unsafe_allow_html=True)
    
    # Score display
    st.markdown(f"""
    <div class="result-card {severity_class}">
        <h2>{t.get('score_display', 'Your PHQ-9 Score')}: {score}/27</h2>
        <h3>{severity_title}</h3>
        <p style="font-size: 1.1rem; margin: 1rem 0;">{severity_desc}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Analysis section
    st.markdown(f'<h2 style="text-align: center; color: #4682B4; margin: 2rem 0;">{t["ai_analysis"]}</h2>', unsafe_allow_html=True)
    
    with st.spinner(t.get('analyzing', '🤖 AI is analyzing your responses...')):
        ai_analysis = get_ai_analysis(st.session_state.responses, score, st.session_state.language)
    
    st.markdown(f"""
    <div class="question-card">
        <h3>🧠 {t.get('personalized_analysis', 'Personalized Analysis')}</h3>
        <p style="font-size: 1.2rem; line-height: 1.8; font-weight: 500; color: #2C3E50; background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">{ai_analysis}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed breakdown
    st.markdown(f"""
    <div class="question-card">
        <h3>📊 {t.get('response_breakdown', 'Response Breakdown')}</h3>
    """, unsafe_allow_html=True)
    
    # Show response summary
    for i, response in st.session_state.responses.items():
        question = t['questions'][i]
        answer = t['options'][response]
        st.markdown(f"<p><strong>Q{i+1}:</strong> {question[:50]}... → <span style='color: #4682B4;'>{answer} ({response} {t.get('points', 'pts')})</span></p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Professional recommendations
    st.markdown(f"""
    <div class="question-card">
        <h3>🩺 {t.get('professional_recommendations', 'Professional Recommendations')}</h3>
        {get_professional_recommendations(score, st.session_state.language)}
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"🔄 {t.get('take_again', 'Take Again')}", key="retake_btn", use_container_width=True):
            st.session_state.current_page = 'questionnaire'
            st.session_state.current_question = 0
            st.session_state.responses = {}
            st.session_state.total_score = 0
            st.rerun()
    
    with col2:
        if st.button(f"📚 {t.get('view_resources', 'View Resources')}", key="resources_btn", use_container_width=True):
            st.session_state.current_page = 'resources'
            st.rerun()
    
    with col3:
        if st.button(f"🏠 {t['home']}", key="home_btn", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()

def get_professional_recommendations(score: int, language: str) -> str:
    """Get professional recommendations based on score"""
    severity = get_severity_level(score)
    
    recommendations = {
        'English': {
            'minimal': """
                <ul>
                    <li>✅ Continue your current self-care practices</li>
                    <li>🏃‍♂️ Maintain regular exercise and healthy sleep</li>
                    <li>👥 Stay connected with friends and family</li>
                    <li>📊 Consider periodic mental health check-ins</li>
                    <li>🚨 Be aware of warning signs and seek help if symptoms worsen</li>
                </ul>
            """,
            'mild': """
                <ul>
                    <li>👨‍⚕️ Consider discussing your feelings with a healthcare provider</li>
                    <li>🧘‍♀️ Try stress management techniques (meditation, yoga)</li>
                    <li>💬 Consider counseling or therapy as a preventive measure</li>
                    <li>📱 Use mood tracking apps to monitor your mental health</li>
                    <li>🏃‍♂️ Increase physical activity and social engagement</li>
                </ul>
            """,
            'moderate': """
                <ul>
                    <li>🚨 <strong>Seek professional help from a mental health provider</strong></li>
                    <li>👨‍⚕️ Schedule an appointment with your primary care doctor</li>
                    <li>💊 Discuss treatment options including therapy and medication</li>
                    <li>👥 Consider joining a support group</li>
                    <li>🏠 Inform trusted family members or friends about your condition</li>
                </ul>
            """,
            'severe': """
                <ul>
                    <li>🚨 <strong>SEEK IMMEDIATE PROFESSIONAL HELP</strong></li>
                    <li>📞 Contact your doctor or mental health professional TODAY</li>
                    <li>🆘 If having thoughts of self-harm, call a crisis helpline immediately</li>
                    <li>👥 Don't isolate yourself - reach out to trusted people</li>
                    <li>💊 Discuss comprehensive treatment options urgently</li>
                    <li>🏥 Consider intensive outpatient or inpatient treatment</li>
                </ul>
            """
        },
        'French': {
            'minimal': """
                <ul>
                    <li>✅ Continuez vos pratiques actuelles de soins personnels</li>
                    <li>🏃‍♂️ Maintenez un exercice régulier et un sommeil sain</li>
                    <li>👥 Restez connecté avec vos amis et votre famille</li>
                    <li>📊 Considérez des contrôles périodiques de santé mentale</li>
                </ul>
            """,
            'mild': """
                <ul>
                    <li>👨‍⚕️ Considérez discuter de vos sentiments avec un professionnel de santé</li>
                    <li>🧘‍♀️ Essayez des techniques de gestion du stress</li>
                    <li>💬 Considérez le counseling comme mesure préventive</li>
                </ul>
            """,
            'moderate': """
                <ul>
                    <li>🚨 <strong>Cherchez l'aide professionnelle d'un prestataire de santé mentale</strong></li>
                    <li>👨‍⚕️ Planifiez un rendez-vous avec votre médecin</li>
                    <li>💊 Discutez des options de traitement</li>
                </ul>
            """,
            'severe': """
                <ul>
                    <li>🚨 <strong>CHERCHEZ IMMÉDIATEMENT L'AIDE PROFESSIONNELLE</strong></li>
                    <li>📞 Contactez votre médecin AUJOURD'HUI</li>
                    <li>🆘 Si vous avez des pensées d'auto-blessure, appelez une ligne d'écoute</li>
                </ul>
            """
        },
        'Yoruba': {
            'minimal': """
                <ul>
                    <li>✅ Tẹ̀síwájú pẹ̀lú ìtọ́jú ara rẹ</li>
                    <li>🏃‍♂️ Ṣetọju adaṣe deede ati oorun to dara</li>
                    <li>👥 Ṣe asopọ pẹlu awọn ọrẹ ati ẹbi</li>
                    <li>📊 Ronu nipa awọn ayẹwo ilera ọpọlọ igba diẹ</li>
                </ul>
            """,
            'mild': """
                <ul>
                    <li>👨‍⚕️ Ronu lati ba oníṣègùn rẹ sọrọ nipa awọn ẹdun rẹ</li>
                    <li>🧘‍♀️ Gbiyanju awọn ilana iṣakoso stress (meditation, yoga)</li>
                    <li>💬 Ronu nipa itọju tabi imọran gẹgẹbi igbese idena</li>
                </ul>
            """,
            'moderate': """
                <ul>
                    <li>🚨 <strong>Wa iranlọwọ ọjọgbọn lati ọdọ olupese ilera ọpọlọ</strong></li>
                    <li>👨‍⚕️ Ṣeto ipade pẹlu dokita akọkọ rẹ</li>
                    <li>💊 Jiroro lori awọn aṣayan itọju pẹlu itọju ati oogun</li>
                </ul>
            """,
            'severe': """
                <ul>
                    <li>🚨 <strong>WA HELP ỌJỌ́MẸTA</strong></li>
                    <li>📞 Pe dokita rẹ tabi ọjọgbọn ilera ọpọlọ LỌ́JỌ́</li>
                    <li>🆘 Ti o ba ni awọn ero ti ara ẹni, pe ila iranlọwọ pajawiri lẹsẹkẹsẹ</li>
                </ul>
            """
        },
        'Igbo': {
            'minimal': """
                <ul>
                    <li>✅ Gaa n'ihu na-elekọta onwe gị</li>
                    <li>🏃‍♂️ Nwee omume ọma na ụra kwesịrị ekwesị</li>
                    <li>👥 Nọgidenụ na mmekọrịta na ndị enyi na ezinụlọ</li>
                    <li>📊 Chee echiche banyere nyocha ahụike uche oge niile</li>
                </ul>
            """,
            'mild': """
                <ul>
                    <li>👨‍⚕️ Chee echiche ịgwa dọkịta gị okwu banyere mmetụta gị</li>
                    <li>🧘‍♀️ Gbalịa usoro njikwa nrụgide (meditation, yoga)</li>
                    <li>💬 Chee echiche banyere ọgwụgwọ ma ọ bụ ndụmọdụ dịka usoro nchebe</li>
                </ul>
            """,
            'moderate': """
                <ul>
                    <li>🚨 Chọọ enyemaka ọkachamara site n'aka onye na-ahụ maka ahụike uche</li>
                    <li>👨‍⚕️ Hazie oge ịkpọtụrụ dọkịta gị</li>
                    <li>💊 Kparịta ụka banyere nhọrọ ọgwụgwọ gụnyere ọgwụgwọ na ọgwụ</li>
                </ul>
            """,
            'severe': """
                <ul>
                    <li>🚨 CHỌTA ENYEMAKA ỌJỌ́MẸTA</li>
                    <li>📞 Kpọtụrụ dọkịta gị ma ọ bụ onye na-ahụ maka ahụike uche TAA</li>
                    <li>🆘 Ọ bụrụ na ịnwe echiche imebi onwe gị, kpọọ nọmba enyemaka ozugbo</li>
                </ul>
            """
        },
        'Hausa': {
            'minimal': """
                <ul>
                    <li>✅ Ci gaba da kula da kanka kamar yadda kake yi yanzu</li>
                    <li>🏃‍♂️ Ci gaba da motsa jiki akai-akai da barci mai kyau</li>
                    <li>👥 Kasance tare da abokai da dangi</li>
                    <li>📊 Yi la'akari da duba lafiyar kwakwalwa lokaci-lokaci</li>
                </ul>
            """,
            'mild': """
                <ul>
                    <li>👨‍⚕️ Yi la'akari da tattaunawa da mai ba da lafiya game da yadda kake ji</li>
                    <li>🧘‍♀️ Gwada hanyoyin sarrafa damuwa (yin tunani, yoga)</li>
                    <li>💬 Yi la'akari da shawarar ko magani a matsayin matakin kariya</li>
                </ul>
            """,
            'moderate': """
                <ul>
                    <li>🚨 Nemi taimako daga mai ba da lafiya na kwakwalwa</li>
                    <li>👨‍⚕️ Tsara ganawa da likitanka na farko</li>
                    <li>💊 Tattauna hanyoyin magani ciki har da magani da magani</li>
                </ul>
            """,
            'severe': """
                <ul>
                    <li>🚨 NEMI Taimako NAN TAKE</li>
                    <li>📞 Tuntuɓi likitanka ko ƙwararren lafiya yau</li>
                    <li>🆘 Idan kana da tunanin cutar da kanka, kira layin taimako nan take</li>
                </ul>
            """
        }
    }
    
    lang_recs = recommendations.get(language, recommendations['English'])
    return lang_recs.get(severity, lang_recs['minimal'])

def main():
    """Main application function"""
    # Language selector in sidebar
    with st.sidebar:
        st.markdown("### 🌐 Select Language")
        show_language_selector()
        
        st.markdown("---")
        st.markdown("### ℹ️ Quick Info")
        st.markdown("""
        - **Time:** 3-5 minutes
        - **Questions:** 9 total
        - **Privacy:** Fully secure
        - **Languages:** 5 supported
        """)
        
        st.markdown("---")
        if st.button("🆘 Crisis Resources", use_container_width=True):
            st.session_state.current_page = 'resources'
            st.rerun()
    
    # Main content routing
    if st.session_state.current_page == 'questionnaire':
        show_questionnaire()
    elif st.session_state.current_page == 'results':
        show_results()
    else:
        show_home_page()
    
    # Footer
    t = TRANSLATIONS[st.session_state.language]
    st.markdown(f"""
    <div class="footer">
        <p>{t['privacy_note']}</p>
        <p>⚠️ <strong>Disclaimer:</strong> This tool is for screening purposes only and does not replace professional medical advice, diagnosis, or treatment.</p>
        <p>🏆 <em>Innovation in AI Medicine Competition Entry</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()