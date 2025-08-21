import streamlit as st
from database.db_manager import execute_query

def get_legal_response(query, language="English"):
    """Generate legal responses based on query and language"""
    legal_responses = {
        "English": {
            "fir": "To file an FIR (First Information Report): 1) Visit the nearest police station, 2) Provide details of the incident, 3) Get a copy of the FIR with number, 4) Keep it safe for future reference. You have the right to file an FIR for any cognizable offense.",
            "bail": "Bail is the temporary release of an accused person awaiting trial. Types: Regular bail, Anticipatory bail, Interim bail. Contact a lawyer for proper guidance based on your specific case.",
            "divorce": "In India, divorce can be filed under: 1) Hindu Marriage Act, 2) Indian Christian Marriage Act, 3) Special Marriage Act. Grounds include cruelty, desertion, conversion, mental disorder, etc. Mutual consent divorce is faster.",
            "property": "Property disputes can be civil or criminal. Documents needed: Sale deed, mutation records, survey settlement records. Consider mediation before court proceedings.",
            "consumer": "Consumer rights include: Right to safety, information, choice, redressal. File complaints at District/State/National Consumer Forums based on compensation amount.",
            "employment": "Labor laws protect workers' rights. Issues like unfair dismissal, non-payment of wages, workplace harassment can be addressed through Labor Courts or appropriate authorities."
        },
        "Hindi": {
            "fir": "प्राथमिकी (FIR) दर्ज करने के लिए: 1) निकटतम पुलिस स्टेशन जाएं, 2) घटना का विवरण दें, 3) FIR की नंबर के साथ कॉपी लें, 4) भविष्य के संदर्भ के लिए सुरक्षित रखें।",
            "bail": "जमानत एक अभियुक्त व्यक्ति की अस्थायी रिहाई है। प्रकार: नियमित जमानत, अग्रिम जमानत, अंतरिम जमानत। अपने मामले के लिए वकील से संपर्क करें।",
            "divorce": "भारत में तलाक दायर किया जा सकता है: 1) हिंदू विवाह अधिनियम, 2) भारतीय ईसाई विवाह अधिनियम, 3) विशेष विवाह अधिनियम के तहत।",
            "property": "संपत्ति विवाद दीवानी या फौजदारी हो सकते हैं। आवश्यक दस्तावेज: बिक्री विलेख, म्यूटेशन रिकॉर्ड, सर्वे सेटलमेंट रिकॉर्ड।",
            "consumer": "उपभोक्ता अधिकारों में शामिल हैं: सुरक्षा का अधिकार, जानकारी का अधिकार, पसंद का अधिकार, निवारण का अधिकार।",
            "employment": "श्रम कानून श्रमिकों के अधिकारों की रक्षा करते हैं। अनुचित बर्खास्तगी, वेतन न मिलना जैसे मुद्दों को श्रम न्यायालयों में उठाया जा सकता है।"
        }
    }

    query_lower = query.lower()
    responses = legal_responses.get(language, legal_responses["English"])

    # Check for keywords in query
    for key, response in responses.items():
        if key in query_lower:
            return response

    # Default response
    default_responses = {
        "English": f"I understand you're asking about legal matters. For specific guidance, please consult with a verified lawyer through our platform. You can also visit our Legal Awareness section for general information about Indian laws and procedures.",
        "Hindi": f"मैं समझता हूं कि आप कानूनी मामलों के बारे में पूछ रहे हैं। विशिष्ट मार्गदर्शन के लिए, कृपया हमारे प्लेटफॉर्म के माध्यम से एक सत्यापित वकील से सलाह लें।"
    }

    return default_responses.get(language, default_responses["English"])

def save_chat_message(user_id, message, response, language):
    """Save chat message to database"""
    try:
        execute_query(
            "INSERT INTO chat_messages (user_id, message, response, language) VALUES (%s, %s, %s, %s)",
            (user_id, message, response, language)
        )
        return True
    except Exception as e:
        st.error(f"Error saving chat: {e}")
        return False

def get_quick_questions():
    """Return list of quick questions for the chatbot"""
    return [
        "How to file an FIR?",
        "What is bail process?",
        "Divorce procedure in India",
        "Property dispute resolution",
        "Consumer rights protection",
        "Employment law basics"
    ]
