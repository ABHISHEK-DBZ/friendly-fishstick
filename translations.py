"""
Multi-language support for AI Krishi Sahayak
Provides translations for English and Hindi
"""

TRANSLATIONS = {
    "en": {
        # Interface labels
        "app_title": "AI Krishi Sahayak",
        "app_subtitle": "Your AI-Powered Agricultural Assistant",
        "welcome": "Welcome",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "diagnose": "Diagnose Plant",
        "history": "My History",
        "followup": "Follow-ups",
        "about": "About",
        
        # Form fields
        "user_id": "User ID",
        "name": "Name",
        "location": "Location",
        "phone": "Phone Number",
        "upload_image": "Upload Plant Image",
        "additional_info": "Additional Information",
        "submit": "Submit",
        "cancel": "Cancel",
        
        # Messages
        "upload_prompt": "Take a photo of the affected plant leaf",
        "processing": "Analyzing your plant...",
        "success": "Analysis complete!",
        "error": "An error occurred",
        "no_history": "No diagnosis history yet",
        "no_followups": "No pending follow-ups",
        
        # Action plan sections
        "problem_identified": "PROBLEM IDENTIFIED",
        "what_to_do": "WHAT YOU NEED TO DO",
        "timeline": "TIMELINE",
        "estimated_cost": "ESTIMATED COST",
        "safety_tips": "SAFETY TIPS",
        "followup_schedule": "FOLLOW-UP SCHEDULE",
        "need_help": "NEED HELP?",
        
        # Advisory prompts
        "advisory_instruction": """Create a simple, farmer-friendly action plan based on this information:

DIAGNOSIS FROM EXPERT:
{diagnosis}

RESEARCH AND RECOMMENDATIONS:
{research}

CURRENT WEATHER:
{weather}

Create a clear action plan in ENGLISH that any farmer can follow.
Include practical steps, timing, costs, and safety measures.
Make it encouraging and supportive in tone.

Use these section headers:
🌱 PROBLEM IDENTIFIED
🔍 WHAT YOU NEED TO DO
⏰ TIMELINE
💰 ESTIMATED COST (in INR)
⚠️ SAFETY TIPS
📅 FOLLOW-UP SCHEDULE
📞 NEED HELP?

Remember: This advice could save their crop and livelihood!"""
    },
    
    "hi": {
        # Interface labels (Hindi)
        "app_title": "एआई कृषि सहायक",
        "app_subtitle": "आपका एआई-संचालित कृषि सहायक",
        "welcome": "स्वागत है",
        "login": "लॉगिन",
        "register": "पंजीकरण करें",
        "logout": "लॉगआउट",
        "diagnose": "पौधे की जांच करें",
        "history": "मेरा इतिहास",
        "followup": "फॉलो-अप",
        "about": "के बारे में",
        
        # Form fields (Hindi)
        "user_id": "उपयोगकर्ता आईडी",
        "name": "नाम",
        "location": "स्थान",
        "phone": "फोन नंबर",
        "upload_image": "पौधे की तस्वीर अपलोड करें",
        "additional_info": "अतिरिक्त जानकारी",
        "submit": "जमा करें",
        "cancel": "रद्द करें",
        
        # Messages (Hindi)
        "upload_prompt": "प्रभावित पौधे की पत्ती की तस्वीर लें",
        "processing": "आपके पौधे का विश्लेषण किया जा रहा है...",
        "success": "विश्लेषण पूरा हुआ!",
        "error": "एक त्रुटि हुई",
        "no_history": "अभी तक कोई निदान इतिहास नहीं",
        "no_followups": "कोई लंबित फॉलो-अप नहीं",
        
        # Action plan sections (Hindi)
        "problem_identified": "समस्या की पहचान",
        "what_to_do": "आपको क्या करना है",
        "timeline": "समय-सारणी",
        "estimated_cost": "अनुमानित लागत",
        "safety_tips": "सुरक्षा सुझाव",
        "followup_schedule": "फॉलो-अप कार्यक्रम",
        "need_help": "मदद चाहिए?",
        
        # Advisory prompts (Hindi)
        "advisory_instruction": """इस जानकारी के आधार पर एक सरल, किसान-अनुकूल कार्य योजना बनाएं:

विशेषज्ञ से निदान:
{diagnosis}

अनुसंधान और सिफारिशें:
{research}

वर्तमान मौसम:
{weather}

HINDI में एक स्पष्ट कार्य योजना बनाएं जिसे कोई भी किसान समझ सके।
व्यावहारिक कदम, समय, लागत और सुरक्षा उपायों को शामिल करें।
प्रोत्साहक और सहायक लहजे में लिखें।

इन अनुभाग शीर्षकों का उपयोग करें:
🌱 समस्या की पहचान
🔍 आपको क्या करना है
⏰ समय-सारणी
💰 अनुमानित लागत (रुपये में)
⚠️ सुरक्षा सुझाव
📅 फॉलो-अप कार्यक्रम
📞 मदद चाहिए?

याद रखें: यह सलाह उनकी फसल और आजीविका बचा सकती है!
सभी उत्तर हिंदी में दें।"""
    }
}


def get_text(key: str, language: str = "en") -> str:
    """
    Get translated text for a given key.
    
    Args:
        key: Translation key
        language: Language code ("en" or "hi")
        
    Returns:
        Translated text or key if not found
    """
    return TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, key)


def get_advisory_instruction(diagnosis: str, research: str, weather: str, language: str = "en") -> str:
    """
    Get advisory instruction prompt in specified language.
    
    Args:
        diagnosis: Diagnosis text
        research: Research findings
        weather: Weather information
        language: Language code ("en" or "hi")
        
    Returns:
        Formatted advisory instruction
    """
    template = TRANSLATIONS.get(language, TRANSLATIONS["en"])["advisory_instruction"]
    return template.format(
        diagnosis=diagnosis,
        research=research,
        weather=weather
    )
