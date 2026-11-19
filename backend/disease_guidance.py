PLANTVILLAGE_CLASSES = (
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
)

_SYMPTOMS = {
    "Apple___Apple_scab": "Olive or dark spots may appear on leaves and fruit.",
    "Apple___Black_rot": "Leaf lesions and dark, rotting fruit can occur.",
    "Apple___Cedar_apple_rust": "Yellow-orange leaf spots may develop, sometimes with raised growths.",
    "Cherry_(including_sour)___Powdery_mildew": "White powdery growth and curling or distorted leaves may occur.",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Gray or tan, rectangular leaf lesions may be bounded by leaf veins.",
    "Corn_(maize)___Common_rust_": "Raised reddish-brown pustules may appear on leaf surfaces.",
    "Corn_(maize)___Northern_Leaf_Blight": "Long, cigar-shaped gray-green or brown lesions may appear on leaves.",
    "Grape___Black_rot": "Brown leaf spots and dark, shriveled berries may occur.",
    "Grape___Esca_(Black_Measles)": "Leaf discoloration between veins and dark fruit spotting may occur.",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Dark or brown leaf lesions may enlarge and merge.",
    "Orange___Haunglongbing_(Citrus_greening)": "Blotchy yellow mottling, uneven leaf discoloration, or small misshapen fruit may occur.",
    "Peach___Bacterial_spot": "Small dark or water-soaked leaf spots and shot-hole symptoms may occur.",
    "Pepper,_bell___Bacterial_spot": "Small dark, sometimes water-soaked leaf spots may occur.",
    "Potato___Early_blight": "Brown leaf spots with concentric rings often begin on older leaves.",
    "Potato___Late_blight": "Irregular water-soaked lesions may spread quickly in cool, wet conditions.",
    "Squash___Powdery_mildew": "White powdery patches may form on leaf surfaces.",
    "Strawberry___Leaf_scorch": "Small purple or red spots and browning leaf edges may occur.",
    "Tomato___Bacterial_spot": "Small dark or water-soaked leaf spots and raised fruit spots may occur.",
    "Tomato___Early_blight": "Brown leaf lesions with concentric rings may develop, often on older leaves.",
    "Tomato___Late_blight": "Irregular water-soaked lesions may darken and spread rapidly in humid conditions.",
    "Tomato___Leaf_Mold": "Yellow patches on upper leaf surfaces and olive-colored growth below may occur.",
    "Tomato___Septoria_leaf_spot": "Small round leaf spots with pale centers and darker margins may occur.",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Fine leaf stippling, bronzing, or delicate webbing may occur.",
    "Tomato___Target_Spot": "Brown circular leaf spots with concentric rings may occur.",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Leaf yellowing, upward curling, and stunted growth may occur.",
    "Tomato___Tomato_mosaic_virus": "Mottled light and dark leaf patterns, curling, or distortion may occur.",
}

_SYMPTOMS_HI = {
    "Apple___Apple_scab": "पत्तियों और फलों पर जैतूनी या गहरे धब्बे दिख सकते हैं।",
    "Apple___Black_rot": "पत्तियों पर घाव और फलों में गहरा सड़न हो सकता है।",
    "Apple___Cedar_apple_rust": "पत्तियों पर पीले-नारंगी धब्बे और उभरी हुई संरचनाएं दिख सकती हैं।",
    "Cherry_(including_sour)___Powdery_mildew": "सफेद पाउडर जैसी परत और मुड़ी या विकृत पत्तियां दिख सकती हैं।",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "पत्तियों की नसों के बीच धूसर या हल्के भूरे आयताकार धब्बे दिख सकते हैं।",
    "Corn_(maize)___Common_rust_": "पत्तियों पर उभरे लाल-भूरे दाने दिख सकते हैं।",
    "Corn_(maize)___Northern_Leaf_Blight": "पत्तियों पर लंबे, सिगार जैसे धूसर-हरे या भूरे घाव दिख सकते हैं।",
    "Grape___Black_rot": "पत्तियों पर भूरे धब्बे और फलों पर गहरे, सिकुड़े धब्बे दिख सकते हैं।",
    "Grape___Esca_(Black_Measles)": "पत्ती की नसों के बीच रंग बदलना और फलों पर गहरे धब्बे हो सकते हैं।",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "पत्तियों पर गहरे या भूरे घाव बढ़कर आपस में मिल सकते हैं।",
    "Orange___Haunglongbing_(Citrus_greening)": "पत्तियों पर असमान पीला-मटमैला रंग और छोटे, विकृत फल दिख सकते हैं।",
    "Peach___Bacterial_spot": "पत्तियों पर छोटे गहरे या पानी-जैसे धब्बे और छेद जैसे लक्षण दिख सकते हैं।",
    "Pepper,_bell___Bacterial_spot": "पत्तियों पर छोटे गहरे, कभी-कभी पानी-जैसे धब्बे दिख सकते हैं।",
    "Potato___Early_blight": "पुरानी पत्तियों पर गोल छल्लों जैसे भूरे धब्बे दिख सकते हैं।",
    "Potato___Late_blight": "ठंडे और नम मौसम में पानी-जैसे अनियमित घाव तेजी से फैल सकते हैं।",
    "Squash___Powdery_mildew": "पत्तियों की सतह पर सफेद पाउडर जैसे धब्बे बन सकते हैं।",
    "Strawberry___Leaf_scorch": "पत्तियों पर छोटे बैंगनी या लाल धब्बे और किनारों पर भूरापन हो सकता है।",
    "Tomato___Bacterial_spot": "पत्तियों पर छोटे गहरे या पानी-जैसे धब्बे और फलों पर उभरे धब्बे दिख सकते हैं।",
    "Tomato___Early_blight": "अक्सर पुरानी पत्तियों पर गोल छल्लों जैसे भूरे घाव दिख सकते हैं।",
    "Tomato___Late_blight": "नम मौसम में पानी-जैसे अनियमित घाव गहरे होकर तेजी से फैल सकते हैं।",
    "Tomato___Leaf_Mold": "पत्तियों की ऊपरी सतह पर पीले धब्बे और नीचे जैतूनी रंग की परत दिख सकती है।",
    "Tomato___Septoria_leaf_spot": "पत्तियों पर हल्के केंद्र और गहरे किनारों वाले छोटे गोल धब्बे दिख सकते हैं।",
    "Tomato___Spider_mites Two-spotted_spider_mite": "पत्तियों पर बारीक बिंदु, कांस्य रंग या महीन जाला दिख सकता है।",
    "Tomato___Target_Spot": "पत्तियों पर गोल छल्लों जैसे भूरे धब्बे दिख सकते हैं।",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "पत्तियां पीली होकर ऊपर की ओर मुड़ सकती हैं और वृद्धि रुक सकती है।",
    "Tomato___Tomato_mosaic_virus": "पत्तियों पर हल्के-गहरे चितकबरे रंग, मुड़ना या विकृति दिख सकती है।",
}

_PREVENTION = (
    "Use clean seed or planting material, scout plants regularly, clean tools between "
    "areas, and avoid moving suspect plant material between fields. Ask a local KVK "
    "which practices are appropriate for this crop and disease."
)
_TREATMENT = (
    "Do not apply a pesticide based only on this image result. Photograph both sides "
    "of affected leaves and ask a local KVK or agriculture extension specialist to "
    "confirm the cause and any locally approved response. No pesticide dosage is provided."
)


def guidance_for(class_name: str, language: str = "en") -> dict[str, str]:
    if language == "hi":
        prevention = (
            "स्वच्छ बीज या रोपण सामग्री लें, पौधों का नियमित निरीक्षण करें, क्षेत्रों के बीच औजार साफ करें "
            "और संदिग्ध पौध सामग्री को खेतों के बीच न ले जाएं। इस फसल और रोग के लिए उपयुक्त तरीके स्थानीय "
            "कृषि विज्ञान केंद्र (KVK) से पूछें।"
        )
        if class_name.endswith("___healthy"):
            return {
                "symptoms": "मॉडल ने पत्ती को स्वस्थ वर्ग में रखा है; इससे शुरुआती, छिपी हुई या अन्य खेत की समस्याएं खारिज नहीं होतीं।",
                "treatment": "इस तस्वीर के वर्गीकरण से उपचार की जरूरत नहीं बताई गई है। खेत का निरीक्षण जारी रखें और लक्षण दिखें तो स्थानीय सलाह लें।",
                "prevention": prevention,
            }
        symptom = _SYMPTOMS_HI.get(
            class_name,
            "लक्षण फसल, किस्म, मौसम और वृद्धि अवस्था के अनुसार बदल सकते हैं।",
        )
        return {
            "symptoms": f"इस वर्ग से जुड़े सामान्य संकेत: {symptom} मॉडल आपके खेत में इन लक्षणों की पुष्टि नहीं करता।",
            "treatment": (
                "केवल इस तस्वीर के परिणाम के आधार पर कीटनाशक न डालें। प्रभावित पत्तियों के दोनों ओर की तस्वीर लें "
                "और कारण तथा स्थानीय रूप से स्वीकृत उपाय की पुष्टि KVK या कृषि विशेषज्ञ से करें। कोई कीटनाशक मात्रा नहीं दी जाती।"
            ),
            "prevention": prevention,
        }
    if class_name.endswith("___healthy"):
        return {
            "symptoms": "The model assigned a healthy-leaf class; this does not rule out early, hidden, or other field problems.",
            "treatment": "No treatment is indicated by this image classification. Continue field scouting and seek local advice if symptoms are present.",
            "prevention": _PREVENTION,
        }

    symptoms = _SYMPTOMS.get(
        class_name,
        "Symptoms vary with crop, variety, weather, and growth stage; the image class alone cannot confirm them.",
    )
    return {
        "symptoms": f"Common signs associated with this class: {symptoms} These signs are not confirmed in your field by the model.",
        "treatment": _TREATMENT,
        "prevention": _PREVENTION,
    }
