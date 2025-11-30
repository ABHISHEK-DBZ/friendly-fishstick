# 🌐 Multi-Language Support - Implementation Guide

## Overview
AI Krishi Sahayak now supports **English and Hindi** to reach more farmers across India.

## Features Added

### 1. **Translations Module** (`translations.py`)
- Centralized translation dictionary for English (`en`) and Hindi (`hi`)
- All UI labels, messages, and instructions translated
- Advisory prompts customized for each language

### 2. **Language Selection**
Users can switch between languages:

**Web Interface:**
```python
# Route to switch language
GET /set_language/<lang>
# where lang = 'en' or 'hi'
```

**Session Storage:**
```python
session['language'] = 'en'  # or 'hi'
```

### 3. **Advisory Agent Enhancement**
The Advisory Agent now generates action plans in the user's selected language:

```python
# In agents/advisory_agent.py
language = research_data.get("language", "en")
advisory_prompt = get_advisory_instruction(
    diagnosis=diagnosis,
    research=research,
    weather=str(weather),
    language=language
)
```

### 4. **Main Coordinator Update**
```python
# In main.py
await coordinator.diagnose_plant(
    image_path=filepath,
    user_id=user_id,
    location=location,
    additional_context=additional_info,
    language="hi"  # or "en"
)
```

## Usage Examples

### Web Application
```python
# User selects language from dropdown
<select onchange="window.location='/set_language/' + this.value">
    <option value="en">English</option>
    <option value="hi">हिंदी</option>
</select>
```

### API Call
```python
# Diagnose in Hindi
result = await coordinator.diagnose_plant(
    image_path="tomato_leaf.jpg",
    user_id="farmer001",
    location="Pune",
    language="hi"
)
```

### CLI (Command Line)
```python
# Future enhancement
language = Prompt.ask(
    "Select language / भाषा चुनें",
    choices=["en", "hi"],
    default="en"
)
```

## Translation Keys

### Interface Labels
| Key | English | Hindi |
|-----|---------|-------|
| `app_title` | AI Krishi Sahayak | एआई कृषि सहायक |
| `diagnose` | Diagnose Plant | पौधे की जांच करें |
| `history` | My History | मेरा इतिहास |
| `upload_image` | Upload Plant Image | पौधे की तस्वीर अपलोड करें |

### Action Plan Sections
| Key | English | Hindi |
|-----|---------|-------|
| `problem_identified` | PROBLEM IDENTIFIED | समस्या की पहचान |
| `what_to_do` | WHAT YOU NEED TO DO | आपको क्या करना है |
| `timeline` | TIMELINE | समय-सारणी |
| `safety_tips` | SAFETY TIPS | सुरक्षा सुझाव |

## Sample Output

### English Output
```
🌱 PROBLEM IDENTIFIED
Your tomato plant has Early Blight disease...

🔍 WHAT YOU NEED TO DO
Step 1: Remove affected leaves immediately
Step 2: Apply Neem oil spray (2ml per liter)
Step 3: Avoid overhead watering

⏰ TIMELINE
Today: Remove affected leaves
Tomorrow: First neem spray
Day 3: Second spray
```

### Hindi Output
```
🌱 समस्या की पहचान
आपके टमाटर के पौधे में अर्ली ब्लाइट रोग है...

🔍 आपको क्या करना है
चरण 1: प्रभावित पत्तियों को तुरंत हटाएं
चरण 2: नीम के तेल का स्प्रे लगाएं (2ml प्रति लीटर)
चरण 3: ऊपर से पानी देने से बचें

⏰ समय-सारणी
आज: प्रभावित पत्तियों को हटाएं
कल: पहला नीम स्प्रे
दिन 3: दूसरा स्प्रे
```

## Adding New Languages

To add more languages (e.g., Marathi, Kannada):

1. **Update `translations.py`:**
```python
TRANSLATIONS = {
    "en": {...},
    "hi": {...},
    "mr": {  # Marathi
        "app_title": "एआय कृषी सहाय्यक",
        "diagnose": "झाडाची तपासणी करा",
        ...
    }
}
```

2. **Update language routes:**
```python
@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['en', 'hi', 'mr']:  # Add new language
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))
```

3. **Add advisory instructions for new language**

## Template Usage

In Flask templates, access translations:
```html
<h1>{{ get_text('app_title') }}</h1>
<button>{{ get_text('submit') }}</button>

<!-- Current language -->
<span>Language: {{ lang }}</span>
```

## Technical Implementation

### Translation Function
```python
def get_text(key: str, language: str = "en") -> str:
    """Get translated text for a given key"""
    return TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, key)
```

### Context Processor
```python
@app.context_processor
def inject_language():
    """Make language available in all templates"""
    lang = session.get('language', 'en')
    return dict(lang=lang, get_text=lambda key: get_text(key, lang))
```

## Testing

### Test English Output
```bash
curl -X POST https://claimai.vercel.app/diagnose \
  -F "image=@tomato_leaf.jpg" \
  -F "language=en" \
  -b "session_cookie"
```

### Test Hindi Output
```bash
curl -X POST https://claimai.vercel.app/diagnose \
  -F "image=@tomato_leaf.jpg" \
  -F "language=hi" \
  -b "session_cookie"
```

## Files Modified

1. ✅ `translations.py` - New file with all translations
2. ✅ `agents/advisory_agent.py` - Language-aware action plans
3. ✅ `main.py` - Added language parameter to diagnose_plant()
4. ✅ `app.py` - Language switcher route, context processor
5. ✅ Templates - Use translation keys (future enhancement)

## Deployment Status

✅ **Live at:** https://claimai.vercel.app
✅ **Multi-language support:** English & Hindi
✅ **API ready:** Language parameter working
⚠️ **Templates:** Need to be updated to use translation keys

## Next Steps

1. Update HTML templates to use `{{ get_text() }}` function
2. Add language selector dropdown in navbar
3. Test with real farmers in both languages
4. Add more regional languages (Marathi, Tamil, Telugu, etc.)
5. Consider voice input/output for low-literacy users

## Benefits

✅ **Accessibility:** Reaches Hindi-speaking farmers (41% of India)
✅ **Trust:** Local language builds confidence
✅ **Adoption:** Easier for farmers with limited English
✅ **Scalability:** Easy to add more languages
✅ **Government Programs:** Aligns with Digital India initiatives

---

**Live Demo:** https://claimai.vercel.app
**Repository:** https://github.com/ABHISHEK-DBZ/friendly-fishstick
