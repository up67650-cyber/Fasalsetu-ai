import { useEffect, useRef, useState } from 'react'
import {
  Activity, AlertTriangle, ArrowRight, ArrowUpRight, BadgeCheck,
  BarChart3, Bell, BookOpen, Check, ChevronDown, ChevronRight,
  Cloud, CloudDrizzle, CloudSun, Droplets, Globe2, HelpCircle, Home, Leaf,
  Menu, MessageCircle, Search, Settings2, ShieldCheck, Sprout, Sun,
  ThermometerSun, Upload, Wind, X
} from 'lucide-react'
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'
import { api } from './api'

const translations = {
  en: {
    dashboard: 'Overview', doctor: 'Crop doctor', weather: 'Weather', advisory: 'Crop advisory',
    assistant: 'Farm assistant', farm: 'My farm', welcome: 'Good morning, farmer',
    subtitle: 'A clearer view of your farm, today and every day.', overview: 'Farm overview',
    weatherTitle: 'Weather outlook', health: 'Crop health', alerts: 'Farm alerts',
    recommendations: 'For your farm', activity: 'Farm activity', seeAll: 'See all',
    quickActions: 'Quick actions', disease: 'Check a leaf', ask: 'Ask the assistant',
    plan: 'Plan irrigation', location: 'Pune, Maharashtra', search: 'Search anything...',
    hi: 'हिन्दी', en: 'English', good: 'All systems looking good'
  },
  hi: {
    dashboard: 'अवलोकन', doctor: 'फसल डॉक्टर', weather: 'मौसम', advisory: 'फसल सलाह',
    assistant: 'कृषि सहायक', farm: 'मेरा खेत', welcome: 'सुप्रभात, किसान',
    subtitle: 'आज और हर दिन अपने खेत की स्पष्ट जानकारी।', overview: 'खेत का विवरण',
    weatherTitle: 'मौसम का अनुमान', health: 'फसल स्वास्थ्य', alerts: 'खेत के अलर्ट',
    recommendations: 'आपके खेत के लिए', activity: 'खेत की गतिविधि', seeAll: 'सभी देखें',
    quickActions: 'त्वरित कार्य', disease: 'पत्ते की जांच', ask: 'सहायक से पूछें',
    plan: 'सिंचाई की योजना', location: 'पुणे, महाराष्ट्र', search: 'कुछ भी खोजें...',
    hi: 'हिन्दी', en: 'English', good: 'सभी संकेत सामान्य हैं'
  }
}

const hindiText = {
  'WORKSPACE': 'कार्यक्षेत्र', 'YOUR FARM': 'आपका खेत', 'KHARIF SEASON': 'खरीफ का मौसम',
  'Season planner': 'मौसम योजना', 'Help & support': 'मदद और सहायता', 'Farm owner': 'खेत के मालिक',
  'Switch language': 'भाषा बदलें', 'Close menu': 'मेनू बंद करें', 'Close navigation': 'नेविगेशन बंद करें',
  'Open navigation': 'नेविगेशन खोलें', 'Notifications': 'सूचनाएं',
  'Farm settings': 'खेत की सेटिंग', 'YOUR FARM AT A GLANCE': 'आपके खेत की एक झलक',
  'Grow with confidence.': 'आत्मविश्वास से खेती करें।', 'One season at a time.': 'हर मौसम में बेहतर खेती।',
  'Get the information you need to make your next farm decision.': 'खेती के अगले फैसले के लिए जरूरी जानकारी पाएं।',
  'Get crop advice': 'फसल सलाह पाएं', 'Live conditions and insights for your farm': 'आपके खेत की ताजा स्थिति और जानकारी',
  'LIVE OVERVIEW': 'ताजा जानकारी', 'TEMPERATURE': 'तापमान', 'Awaiting weather': 'मौसम जानकारी की प्रतीक्षा',
  'Weather unavailable': 'मौसम उपलब्ध नहीं', 'Connecting to weather': 'मौसम से जुड़ रहे हैं',
  'CROP HEALTH': 'फसल स्वास्थ्य', 'not assessed': 'जांच नहीं हुई', 'No saved model diagnosis': 'कोई मॉडल जांच सहेजी नहीं',
  'ACTIVE ALERTS': 'सक्रिय चेतावनी', 'weather risks': 'मौसम जोखिम', 'no data yet': 'अभी जानकारी नहीं',
  'Based on available forecast': 'उपलब्ध पूर्वानुमान पर आधारित', 'FARM RECORDS': 'खेत के रिकॉर्ड',
  'saved entries': 'सहेजी प्रविष्टियां', 'field activities recorded': 'खेत की गतिविधियां दर्ज',
  'LAST 7 DAYS': 'पिछले 7 दिन', 'Farm activity records': 'खेत की गतिविधियों के रिकॉर्ड',
  'SQLite history': 'SQLite इतिहास', 'Saved events': 'सहेजी गतिविधियां',
  'Counts are calculated from saved SQLite history; they are not sensor measurements.': 'गिनती SQLite में सहेजे रिकॉर्ड से है; यह सेंसर माप नहीं है।',
  'No farm records in the last seven days yet.': 'पिछले सात दिनों में खेत का कोई रिकॉर्ड नहीं है।',
  'Loading saved farm activity…': 'सहेजी गतिविधियां लोड हो रही हैं…',
  'LOCAL FORECAST': 'स्थानीय पूर्वानुमान', 'Open-Meteo live': 'Open-Meteo से लाइव',
  'Waiting for data': 'जानकारी की प्रतीक्षा', 'Current conditions': 'वर्तमान स्थिति',
  'Weather data unavailable': 'मौसम जानकारी उपलब्ध नहीं', 'Fetching local conditions': 'स्थानीय मौसम लोड हो रहा है',
  'Connecting to Open-Meteo': 'Open-Meteo से जुड़ रहे हैं', 'Today': 'आज',
  'PAY ATTENTION': 'ध्यान दें', 'No verified alerts yet': 'अभी सत्यापित चेतावनी नहीं',
  'No significant weather risks in the forecast.': 'पूर्वानुमान में कोई बड़ा मौसम जोखिम नहीं।',
  'Weather risk checks appear when live forecast is available.': 'लाइव पूर्वानुमान उपलब्ध होने पर मौसम जोखिम दिखेंगे।',
  'View weather intelligence': 'मौसम जानकारी देखें', 'PERSONALIZED GUIDANCE': 'आपके लिए सलाह',
  'Build your crop advisory': 'फसल सलाह तैयार करें', 'Add your crop, soil and growth stage to get tailored guidance.': 'उपयुक्त सलाह के लिए फसल, मिट्टी और वृद्धि अवस्था भरें।',
  'Get recommendations': 'सलाह पाएं', 'Check crop health': 'फसल स्वास्थ्य जांचें',
  'Upload a leaf photo. Diagnosis needs a configured model.': 'पत्ते की तस्वीर अपलोड करें। जांच के लिए मॉडल जरूरी है।',
  'Open crop doctor': 'फसल डॉक्टर खोलें', 'RECENT UPDATES': 'हाल के अपडेट',
  'Your farm activity will show here as you use the app.': 'ऐप का उपयोग करने पर खेत की गतिविधियां यहां दिखेंगी।',
  'AI CROP DOCTOR': 'AI फसल डॉक्टर', 'A closer look at crop health': 'फसल स्वास्थ्य की गहरी जांच',
  'Upload a clear leaf photo for a model-assisted classification. Results require field confirmation.': 'मॉडल विश्लेषण के लिए पत्ते की साफ तस्वीर अपलोड करें। परिणाम की खेत में पुष्टि जरूरी है।',
  'LEAF IMAGE': 'पत्ते की तस्वीर', 'Upload a crop photo': 'फसल की तस्वीर अपलोड करें',
  'Drop a leaf photo here': 'पत्ते की तस्वीर यहां छोड़ें', 'or browse files': 'या फाइल चुनें',
  'JPG, PNG or WebP · Max 10 MB': 'JPG, PNG या WebP · अधिकतम 10 MB',
  'Remove': 'हटाएं', 'Analyze leaf': 'पत्ते का विश्लेषण करें', 'Analysis unavailable': 'विश्लेषण उपलब्ध नहीं',
  'Analyzing leaf…': 'पत्ते का विश्लेषण हो रहा है…', 'Choose a JPG, PNG or WebP image.': 'JPG, PNG या WebP तस्वीर चुनें।',
  'Image must be 10 MB or smaller.': 'तस्वीर 10 MB या उससे छोटी होनी चाहिए।',
  'Important:': 'महत्वपूर्ण:', 'Possible symptoms': 'संभावित लक्षण', 'Safer next steps': 'सुरक्षित अगले कदम',
  'Prevention': 'बचाव', 'HOW TO GET A GOOD PHOTO': 'अच्छी तस्वीर कैसे लें',
  'A few tips for a clearer check': 'बेहतर जांच के लिए कुछ सुझाव', 'Show the whole leaf': 'पूरा पत्ता दिखाएं',
  'Include both healthy and affected parts.': 'स्वस्थ और प्रभावित दोनों हिस्से दिखाएं।',
  'Use natural light': 'प्राकृतिक रोशनी में लें', 'Avoid heavy shadows and blur.': 'गहरी छाया और धुंधलापन न हो।',
  'One leaf at a time': 'एक बार में एक पत्ता', 'Keep the leaf in focus against a plain background.': 'सादे बैकग्राउंड पर पत्ते को फोकस में रखें।',
  'Designed for responsible advice': 'जिम्मेदार सलाह के लिए बनाया गया',
  'Predictions require local confirmation. The current model is trained for PlantVillage classes and may not generalize to field conditions.': 'पूर्वानुमान की स्थानीय पुष्टि जरूरी है। मौजूदा मॉडल PlantVillage वर्गों पर प्रशिक्षित है और खेत की स्थितियों में सही न भी हो।',
  'Model scores are not guaranteed accuracy. Predictions need local expert confirmation; no pesticide dosage is provided. Images are not retained by the app.': 'मॉडल स्कोर निश्चित सटीकता नहीं है। स्थानीय विशेषज्ञ से पुष्टि करें; कीटनाशक की मात्रा नहीं दी जाती। तस्वीरें ऐप में सहेजी नहीं जातीं।',
  'WEATHER INTELLIGENCE': 'मौसम जानकारी', 'Know what’s coming': 'आगे के मौसम को जानें',
  'Live conditions and forecast from Open-Meteo. Weather risks are guidance, not a substitute for local alerts.': 'Open-Meteo से लाइव मौसम और पूर्वानुमान। जोखिम संकेत स्थानीय चेतावनी का विकल्प नहीं हैं।',
  'Choose a forecast location': 'पूर्वानुमान के लिए स्थान चुनें', 'Search city or district': 'शहर या जिले का नाम खोजें',
  'Search locations': 'स्थान खोजें', 'Searching…': 'खोज रहे हैं…', 'Selected:': 'चयनित:',
  'Enter at least 2 characters to search.': 'खोज के लिए कम से कम 2 अक्षर लिखें।',
  'NEXT 7 DAYS': 'अगले 7 दिन', 'Daily forecast': 'दैनिक पूर्वानुमान', 'Humidity': 'नमी',
  'Wind speed': 'हवा की गति', 'Rain chance today': 'आज बारिश की संभावना', 'Feels like': 'अनुभव तापमान',
  'Weather risk analysis': 'मौसम जोखिम विश्लेषण', 'FIELD READINESS': 'खेत की तैयारी',
  'No high weather risks detected in this forecast.': 'इस पूर्वानुमान में कोई बड़ा मौसम जोखिम नहीं मिला।',
  'Rules use the available 7-day forecast and are informational. Follow official IMD and local advisories.': 'नियम उपलब्ध 7-दिन के पूर्वानुमान पर आधारित हैं। IMD और स्थानीय सलाह का पालन करें।',
  'Forecast-informed irrigation check': 'पूर्वानुमान के आधार पर सिंचाई जांच',
  'Check field soil moisture and follow local agronomic advice; this weather rule is informational.': 'खेत की मिट्टी की नमी जांचें और स्थानीय कृषि सलाह लें; यह मौसम संकेत केवल जानकारी के लिए है।',
  'SMART CROP ADVISORY': 'स्मार्ट फसल सलाह', 'Advice that starts with your field': 'आपके खेत से शुरू होने वाली सलाह',
  'Tell us what you’re growing. Recommendations are rule-based and should be confirmed locally.': 'आप क्या उगा रहे हैं बताएं। सलाह नियम-आधारित है और स्थानीय रूप से सत्यापित करें।',
  'YOUR FIELD DETAILS': 'आपके खेत की जानकारी', 'Personalize your guidance': 'अपनी सलाह तय करें',
  'Crop': 'फसल', 'Soil type': 'मिट्टी का प्रकार', 'Location': 'स्थान', 'Forecast location': 'पूर्वानुमान का स्थान',
  'Farm size (acres)': 'खेत का आकार (एकड़)', 'Growth stage': 'वृद्धि अवस्था',
  'Get my crop guidance': 'मेरी फसल सलाह पाएं', 'Preparing guidance…': 'सलाह तैयार हो रही है…',
  'General educational guidance only. It is not a diagnosis or pesticide prescription.': 'केवल सामान्य शैक्षिक सलाह। यह निदान या कीटनाशक निर्देश नहीं है।',
  'Good guidance begins with context': 'सही संदर्भ से बेहतर सलाह मिलती है',
  'Choose your crop, soil and growth stage to get practical, general recommendations for your field.': 'अपने खेत के लिए सामान्य सलाह पाने हेतु फसल, मिट्टी और वृद्धि अवस्था चुनें।',
  'FARM ASSISTANT': 'कृषि सहायक', 'Ask a question about farming': 'खेती के बारे में सवाल पूछें',
  'Practical guidance, with context': 'संदर्भ के साथ उपयोगी सलाह',
  'English & Hindi questions': 'अंग्रेज़ी और हिंदी में सवाल',
  'Verify critical decisions locally': 'महत्वपूर्ण फैसलों की स्थानीय पुष्टि करें',
  'Need crop-specific help?': 'फसल-विशेष सहायता चाहिए?',
  'Talk to your local Krishi Vigyan Kendra (KVK) or agriculture extension officer.': 'अपने कृषि विज्ञान केंद्र (KVK) या कृषि विस्तार अधिकारी से संपर्क करें।',
  'Checking guidance…': 'सलाह देख रहे हैं…', 'Send question': 'सवाल भेजें',
  'A little about your field': 'आपके खेत के बारे में',
  'Keep your farm details up to date to make future guidance more relevant.': 'बेहतर सलाह के लिए खेत की जानकारी अपडेट रखें।',
  'FARM PROFILE': 'खेत की प्रोफ़ाइल', 'Farmer & field details': 'किसान और खेत की जानकारी',
  'Farmer name': 'किसान का नाम', 'Your name': 'आपका नाम', 'Village, district, state': 'गांव, जिला, राज्य',
  'Main crop': 'मुख्य फसल', 'Save farm profile': 'खेत की प्रोफ़ाइल सहेजें', 'Saving…': 'सहेज रहे हैं…',
  'YOUR ACTIVITY': 'आपकी गतिविधि', 'Farming history': 'खेती का इतिहास',
  'Your farm story starts here': 'आपके खेत की कहानी यहां शुरू होती है',
  'Saved guidance and assistant conversations will appear here when available.': 'सहेजी सलाह और सहायक की बातचीत यहां दिखेगी।',
  'Farm details are stored locally in the app’s SQLite database.': 'खेत की जानकारी ऐप के स्थानीय SQLite डेटाबेस में सहेजी जाती है।',
  'CROP RECORDS': 'फसल रिकॉर्ड', 'Track crops in your farm': 'अपने खेत की फसलें दर्ज करें',
  'Variety': 'किस्म', 'Area (acres)': 'क्षेत्र (एकड़)', 'Planting date': 'बुवाई की तारीख',
  'Add crop': 'फसल जोड़ें', 'No crop records yet. Add one above to track field progress.': 'अभी फसल रिकॉर्ड नहीं है। प्रगति दर्ज करने के लिए ऊपर फसल जोड़ें।',
  'FIELD JOURNAL': 'खेत की डायरी', 'Record farm activity': 'खेत की गतिविधि दर्ज करें',
  'Activity': 'गतिविधि', 'Field scouting': 'खेत का निरीक्षण', 'Not specified': 'निर्दिष्ट नहीं',
  'Notes': 'टिप्पणी', 'What did you do or observe?': 'आपने क्या किया या देखा?',
  'Save activity': 'गतिविधि सहेजें', 'SAVED RECORDS': 'सहेजे रिकॉर्ड',
  'Advisory, diagnosis & activity history': 'सलाह, जांच और गतिविधियों का इतिहास',
  'No saved history yet': 'अभी कोई इतिहास सहेजा नहीं',
  'Advisories, completed model diagnoses and farm activities will appear here.': 'सलाह, मॉडल की पूरी हुई जांच और खेत की गतिविधियां यहां दिखेंगी।',
  'Records persist in the local SQLite database. Uploaded images are not stored.': 'रिकॉर्ड स्थानीय SQLite डेटाबेस में रहते हैं। अपलोड तस्वीरें सहेजी नहीं जातीं।',
  'Irrigation': 'सिंचाई', 'Fertilizing': 'खाद डालना', 'Planting': 'बुवाई', 'Harvest': 'कटाई', 'Other': 'अन्य',
  'Remove crop record?': 'फसल रिकॉर्ड हटाएं?', 'acres': 'एकड़', 'Wheat': 'गेहूं', 'Rice': 'चावल',
  'Maize': 'मक्का', 'Cotton': 'कपास', 'Tomato': 'टमाटर', 'Chickpea': 'चना', 'Soybean': 'सोयाबीन',
  'Loamy': 'दोमट', 'Clay': 'चिकनी मिट्टी', 'Sandy': 'रेतीली', 'Black cotton': 'काली मिट्टी',
  'Red': 'लाल मिट्टी', 'Alluvial': 'जलोढ़ मिट्टी', 'Sowing': 'बुवाई', 'Seedling': 'अंकुर',
  'Vegetative': 'विकास अवस्था', 'Flowering': 'फूल अवस्था', 'Fruiting': 'फल अवस्था',
  'Open-Meteo · live': 'Open-Meteo · लाइव',
  'Rain': 'बारिश', 'Wind': 'हवा', 'today': 'आज', 'rain': 'बारिश',
  'CHECKING MODEL': 'मॉडल जांच रहे हैं',
  'MODEL READY': 'मॉडल तैयार', 'DEMO MODE · NO MODEL': 'डेमो मोड · मॉडल उपलब्ध नहीं',
  'Checking model availability…': 'मॉडल उपलब्धता जांच रहे हैं…',
  'No trained disease model is installed. No predictions will be made.': 'प्रशिक्षित रोग मॉडल उपलब्ध नहीं है। कोई पूर्वानुमान नहीं दिया जाएगा।',
  'A crop disease model is loaded.': 'फसल रोग मॉडल लोड है।',
  'Install a trained model to enable classification.': 'वर्गीकरण चालू करने के लिए प्रशिक्षित मॉडल स्थापित करें।',
  'Selected crop leaf': 'चुना हुआ फसल पत्ता',
  'Model score:': 'मॉडल स्कोर:', 'uncertain result': 'अनिश्चित परिणाम',
  'DATA UNAVAILABLE': 'जानकारी उपलब्ध नहीं', 'Source: Open-Meteo': 'स्रोत: Open-Meteo',
  'RULE-BASED': 'नियम-आधारित',
  'IRRIGATION CHECK': 'सिंचाई जांच', 'rain chance': 'बारिश की संभावना',
  'References:': 'संदर्भ:',
  'Temperature': 'तापमान', 'Acres': 'एकड़',
  'Farm profile saved.': 'खेत की प्रोफ़ाइल सहेजी गई।',
  'Crop record saved.': 'फसल रिकॉर्ड सहेजा गया।', 'Crop record removed.': 'फसल रिकॉर्ड हटाया गया।',
  'Farm activity saved.': 'खेत की गतिविधि सहेजी गई।',
  'Crop diagnosis could not be completed.': 'फसल जांच पूरी नहीं हो सकी।',
  'Weather location could not be saved.': 'मौसम का स्थान सहेजा नहीं जा सका।',
  'No matching locations found.': 'इस नाम से कोई स्थान नहीं मिला।',
  'For farming support, contact your local Krishi Vigyan Kendra (KVK) or agriculture extension officer.': 'खेती संबंधी सहायता के लिए स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि विस्तार अधिकारी से संपर्क करें।',
  'Start with a suggestion or type your own question below.': 'सुझाव से शुरू करें या नीचे अपना सवाल लिखें।',
  'AI replies are labeled when a provider is configured. If unavailable, a curated rule-based fallback answers common questions.': 'प्रदाता उपलब्ध होने पर AI जवाब स्पष्ट रूप से बताए जाते हैं। अन्यथा आम सवालों के लिए नियम-आधारित जवाब मिलता है।',
  'Farm crop and soil context may be sent to the configured provider': 'खेत की फसल और मिट्टी का संदर्भ चुने हुए प्रदाता को भेजा जा सकता है',
  'AI available': 'AI उपलब्ध', 'Curated fallback available': 'संकलित वैकल्पिक सलाह उपलब्ध',
  'AI + FALLBACK': 'AI + वैकल्पिक सलाह', 'FALLBACK MODE': 'वैकल्पिक सलाह मोड',
  'Forecast-aware guidance uses the selected Weather location. Edit the name to request general guidance without a forecast.': 'मौसम-आधारित सलाह चुने गए स्थान का उपयोग करती है। नाम बदलने पर पूर्वानुमान के बिना सामान्य सलाह मिलेगी।',
  'planted': 'बोया गया', 'My farm': 'मेरा खेत', 'Farmer profile': 'किसान की प्रोफ़ाइल',
  'FARMING, MADE CLEARER': 'खेती, अब और आसान',
  'LIVE · OPEN-METEO': 'लाइव · Open-Meteo',
  'You’re all caught up.': 'अभी कोई नई सूचना नहीं है।',
  'Live weather isn’t available': 'लाइव मौसम उपलब्ध नहीं है',
  'Waiting for the backend to connect to Open-Meteo.': 'बैकएंड Open-Meteo से जुड़ने की प्रतीक्षा कर रहा है।',
  'Start the FastAPI service and check your internet connection. No weather values are filled in with estimates.': 'FastAPI सेवा शुरू करें और इंटरनेट कनेक्शन जांचें। मौसम के अनुमानित मान नहीं दिखाए जाते।',
  'Live weather is unavailable. Check your connection and try again.': 'लाइव मौसम उपलब्ध नहीं है। कनेक्शन जांचकर फिर कोशिश करें।',
  'Open-Meteo returned incomplete forecast data.': 'Open-Meteo से अधूरा पूर्वानुमान मिला।',
  'Upload a JPG, PNG or WebP image.': 'JPG, PNG या WebP तस्वीर अपलोड करें।',
  'Image contents do not match the selected image format.': 'तस्वीर की सामग्री चुने गए फ़ाइल प्रकार से मेल नहीं खाती।',
  'Image dimensions are too large to process safely.': 'तस्वीर के आयाम सुरक्षित रूप से संसाधित करने के लिए बहुत बड़े हैं।',
  'The uploaded file is not a valid, supported image.': 'अपलोड की गई फ़ाइल मान्य समर्थित तस्वीर नहीं है।',
  'Crop diagnosis is unavailable: no trained disease model is configured. No prediction was made.': 'फसल जांच उपलब्ध नहीं है: प्रशिक्षित रोग मॉडल सेट नहीं है। कोई पूर्वानुमान नहीं दिया गया।',
  'Low model score: treat this result as especially uncertain and seek local expert confirmation.': 'मॉडल स्कोर कम है: परिणाम विशेष रूप से अनिश्चित है; स्थानीय कृषि विशेषज्ञ से पुष्टि करें।',
  'Model confidence is not a calibrated probability or a guarantee of accuracy. Field conditions may differ from training images.': 'मॉडल स्कोर कैलिब्रेटेड संभावना या सटीकता की गारंटी नहीं है। खेत की स्थिति प्रशिक्षण तस्वीरों से अलग हो सकती है।',
  'Image classification is an aid, not a field diagnosis. Confirm with a local agriculture expert or KVK before taking action. No pesticide dosage is provided.': 'तस्वीर का वर्गीकरण केवल सहायक संकेत है, खेत में रोग का निदान नहीं। कोई कदम उठाने से पहले स्थानीय कृषि विशेषज्ञ या KVK से पुष्टि करें। कीटनाशक की मात्रा नहीं दी जाती।',
  'Rule-based guidance — not an AI prediction': 'नियम-आधारित सलाह — AI पूर्वानुमान नहीं',
  'Crop diagnosis completed': 'फसल जांच पूरी हुई',
  'Farm profile updated': 'खेत की प्रोफ़ाइल अपडेट हुई',
  'Forecast location updated': 'पूर्वानुमान का स्थान अपडेट हुआ',
  'Crop added': 'फसल जोड़ी गई',
  'Crop details updated': 'फसल की जानकारी अपडेट हुई',
  'Crop removed': 'फसल हटाई गई',
  'Farm activity recorded': 'खेत की गतिविधि दर्ज हुई',
  'Planting recorded': 'बुवाई दर्ज हुई',
  'Irrigation recorded': 'सिंचाई दर्ज हुई',
  'Fertilizer activity recorded': 'खाद डालने की गतिविधि दर्ज हुई',
  'Field scouting recorded': 'खेत का निरीक्षण दर्ज हुआ',
  'Harvest recorded': 'कटाई दर्ज हुई',
  'Crop advisory generated': 'फसल सलाह तैयार हुई',
  'Farm assistant used': 'कृषि सहायक का उपयोग हुआ',
  'AI-generated · verify locally': 'AI द्वारा तैयार · स्थानीय पुष्टि करें',
  'verify in the field': 'खेत में पुष्टि करें',
  'Curated fallback · AI provider is not configured': 'संकलित वैकल्पिक सलाह · AI प्रदाता सेट नहीं है',
  'Curated fallback · AI provider is unavailable': 'संकलित वैकल्पिक सलाह · AI प्रदाता उपलब्ध नहीं है',
  'Apple': 'सेब', 'Blueberry': 'ब्लूबेरी', 'Cherry (including sour)': 'चेरी',
  'Corn (maize)': 'मक्का', 'Grape': 'अंगूर', 'Orange': 'संतरा', 'Peach': 'आड़ू',
  'Pepper, bell': 'शिमला मिर्च', 'Potato': 'आलू', 'Raspberry': 'रसभरी',
  'Squash': 'स्क्वैश', 'Strawberry': 'स्ट्रॉबेरी',
  'Apple scab': 'सेब का स्कैब रोग', 'Black rot': 'काला सड़न रोग',
  'Cedar apple rust': 'सेब का रतुआ रोग', 'healthy': 'स्वस्थ',
  'Powdery mildew': 'चूर्णिल आसिता', 'Cercospora leaf spot Gray leaf spot': 'सर्कोस्पोरा पत्ती धब्बा',
  'Common rust': 'सामान्य रतुआ', 'Northern Leaf Blight': 'उत्तरी पत्ती झुलसा',
  'Esca (Black Measles)': 'एस्का रोग', 'Leaf blight (Isariopsis Leaf Spot)': 'पत्ती झुलसा',
  'Haunglongbing (Citrus greening)': 'सिट्रस ग्रीनिंग रोग', 'Bacterial spot': 'जीवाणु धब्बा रोग',
  'Early blight': 'अगेती झुलसा', 'Late blight': 'पछेती झुलसा', 'Leaf scorch': 'पत्ती झुलसा',
  'Leaf Mold': 'पत्ती फफूंद', 'Septoria leaf spot': 'सेप्टोरिया पत्ती धब्बा',
  'Spider mites Two-spotted spider mite': 'मकड़ी घुन', 'Target Spot': 'लक्ष्याकार धब्बा',
  'Tomato Yellow Leaf Curl Virus': 'टमाटर पीला पत्ती-मोड़ विषाणु',
  'Tomato mosaic virus': 'टमाटर मोज़ेक विषाणु',
  'Farm profile': 'खेत की प्रोफ़ाइल',
  'Farm history': 'खेत का इतिहास',
  'Dashboard data': 'डैशबोर्ड जानकारी',
  'Could not save profile:': 'प्रोफ़ाइल सहेजी नहीं जा सकी:',
  'Could not load the saved weather location:': 'सहेजा हुआ मौसम स्थान लोड नहीं हो सका:',
  'This location is selected for now but could not be saved:': 'यह स्थान अभी चुना गया है, लेकिन सहेजा नहीं जा सका:',
  'Location search is unavailable:': 'स्थान खोज उपलब्ध नहीं है:',
  'Request failed': 'अनुरोध विफल हुआ',
  'Assistant status unavailable': 'सहायक की स्थिति उपलब्ध नहीं है',
  'ASSISTANT UNAVAILABLE': 'सहायक उपलब्ध नहीं',
  'Failed to fetch': 'सर्वर से कनेक्शन नहीं हो सका।',
  'Could not load crop guidance.': 'फसल सलाह लोड नहीं हो सकी।',
  'Enter a valid farm location.': 'खेत का मान्य स्थान दर्ज करें।',
  'Enter a valid forecast location.': 'पूर्वानुमान के लिए मान्य स्थान दर्ज करें।',
  'Enter a crop name.': 'फसल का नाम दर्ज करें।',
  'Farm crop was not found.': 'खेत की फसल का रिकॉर्ड नहीं मिला।',
  'Add a short description of the activity.': 'गतिविधि का छोटा विवरण लिखें।',
  'Latitude or longitude is out of range.': 'अक्षांश या देशांतर मान्य सीमा से बाहर है।',
  'Provide both latitude and longitude for forecast-aware guidance.': 'पूर्वानुमान-आधारित सलाह के लिए अक्षांश और देशांतर दोनों दें।'
}

function tr(value, language) {
  if (typeof value !== 'string') return value
  if (language !== 'hi') return value
  if (hindiText[value]) return hindiText[value]
  const prefixes = [
    'Could not save profile:',
    'Could not load the saved weather location:',
    'This location is selected for now but could not be saved:',
    'Location search is unavailable:'
  ]
  const prefix = prefixes.find((candidate) => value.startsWith(candidate))
  if (prefix) return `${hindiText[prefix]} ${tr(value.slice(prefix.length).trim(), language)}`
  const providerLabel = value.match(/^AI-generated · (.+) · verify locally$/)
  if (providerLabel) return `AI द्वारा तैयार · ${providerLabel[1]} · स्थानीय पुष्टि करें`
  return value
}

const navGroups = [
  { title: 'WORKSPACE', items: [
    { id: 'dashboard', icon: Home }, { id: 'doctor', icon: Activity },
    { id: 'weather', icon: CloudSun }, { id: 'advisory', icon: BookOpen }
  ] },
  { title: 'YOUR FARM', items: [
    { id: 'assistant', icon: MessageCircle }, { id: 'farm', icon: Sprout }
  ] }
]

const defaultLocation = { name: 'Pune, Maharashtra, India', latitude: 18.5204, longitude: 73.8567 }

function App() {
  const [page, setPage] = useState('dashboard')
  const [language, setLanguage] = useState(() => localStorage.getItem('fasalsetu-language') === 'hi' ? 'hi' : 'en')
  const [mobileOpen, setMobileOpen] = useState(false)
  const [weather, setWeather] = useState(null)
  const [weatherError, setWeatherError] = useState('')
  const [selectedLocation, setSelectedLocation] = useState(defaultLocation)
  const [locationReady, setLocationReady] = useState(false)
  const [locationSaveError, setLocationSaveError] = useState('')
  const [farm, setFarm] = useState({ farmer_name: '', location: 'Pune, Maharashtra', crop: 'Wheat', farm_size_acres: 2, soil_type: 'Loamy', growth_stage: 'Vegetative' })
  const [history, setHistory] = useState([])
  const [farmCrops, setFarmCrops] = useState([])
  const [dashboardSummary, setDashboardSummary] = useState(null)
  const [farmError, setFarmError] = useState('')
  const [historyError, setHistoryError] = useState('')
  const [summaryError, setSummaryError] = useState('')
  const [assistantStatus, setAssistantStatus] = useState(null)
  const [assistantStatusError, setAssistantStatusError] = useState('')
  const [assistantDraft, setAssistantDraft] = useState('')
  const [searchText, setSearchText] = useState('')
  const [toast, setToast] = useState('')
  const searchInputRef = useRef(null)
  const t = translations[language]

  useEffect(() => {
    const handleSearchShortcut = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        searchInputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handleSearchShortcut)
    return () => window.removeEventListener('keydown', handleSearchShortcut)
  }, [])

  useEffect(() => {
    let active = true
    if (!locationReady) return () => { active = false }
    setWeatherError('')
    api.weather(selectedLocation.latitude, selectedLocation.longitude, language)
      .then((data) => { if (active) setWeather({ ...data, location_name: selectedLocation.name }) })
      .catch((error) => { if (active) { setWeather(null); setWeatherError(error.message) } })
    return () => { active = false }
  }, [selectedLocation, locationReady, language])

  useEffect(() => {
    let active = true
    api.farm().then((data) => { if (active) setFarm(data) }).catch((error) => { if (active) setFarmError(error.message) })
    api.weatherLocation()
      .then((location) => {
        if (active) setSelectedLocation(location)
      })
      .catch((error) => {
        if (active) setLocationSaveError(`Could not load the saved weather location: ${error.message}`)
      })
      .finally(() => { if (active) setLocationReady(true) })
    api.assistantStatus()
      .then((status) => {
        if (active) {
          setAssistantStatus(status)
          setAssistantStatusError('')
        }
      })
      .catch((error) => {
        if (active) setAssistantStatusError(error.message)
      })
    refreshHistory()
    return () => { active = false }
  }, [])

  const refreshHistory = async () => {
    try {
      const data = await api.history()
      setHistory(data.entries || [])
      setHistoryError('')
    } catch (error) {
      setHistoryError(error.message)
    }
    try {
      const summary = await api.dashboardSummary()
      setDashboardSummary(summary)
      setSummaryError('')
    } catch (error) {
      setSummaryError(error.message)
    }
    try {
      const data = await api.farmCrops()
      setFarmCrops(data.crops || [])
    } catch (error) {
      setFarmError((current) => current || `Crop records: ${error.message}`)
    }
  }

  const selectLocation = async (location) => {
    setSelectedLocation(location)
    setLocationSaveError('')
    try {
      await api.saveWeatherLocation(location)
      await refreshHistory()
    } catch (error) {
      setLocationSaveError(`This location is selected for now but could not be saved: ${error.message}`)
      notify('Weather location could not be saved.')
    }
  }

  const navigate = (next) => {
    setPage(next)
    setMobileOpen(false)
  }
  const notify = (message) => {
    setToast(message)
    window.setTimeout(() => setToast(''), 3200)
  }

  return (
    <div className="app-shell">
      {mobileOpen && <button className="mobile-backdrop" aria-label={tr('Close menu', language)} onClick={() => setMobileOpen(false)} />}
      <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Sprout size={22} strokeWidth={2.2} /></div>
          <div><div className="brand-name">fasal<span>setu</span></div><div className="brand-caption">{tr('FARMING, MADE CLEARER', language)}</div></div>
          <button className="icon-btn sidebar-close" onClick={() => setMobileOpen(false)} aria-label={tr('Close navigation', language)}><X size={19} /></button>
        </div>
        <button className="farm-switcher" onClick={() => navigate('farm')}>
          <div className="farm-avatar"><Sprout size={18} /></div>
          <div className="switcher-copy"><strong>{farm.farmer_name || tr('My farm', language)}</strong><span>{farm.location || t.location}</span></div>
          <ChevronDown size={16} className="switch-chevron" />
        </button>
        <nav className="sidebar-nav">
          {navGroups.map((group) => <div className="nav-group" key={group.title}>
            <div className="nav-label">{tr(group.title, language)}</div>
            {group.items.map(({ id, icon: Icon }) => <button key={id} onClick={() => navigate(id)} className={`nav-item ${page === id ? 'active' : ''}`}>
              <Icon size={18} strokeWidth={1.8} /><span>{t[id]}</span>{id === 'doctor' && <span className="nav-new">AI</span>}
            </button>)}
          </div>)}
        </nav>
        <div className="sidebar-bottom">
          <button className="season-card" onClick={() => navigate('advisory')}><div className="season-icon"><Sun size={18} /></div><div><span>{tr('KHARIF SEASON', language)}</span><strong>{tr('Season planner', language)}</strong></div><ArrowRight size={16} /></button>
          <button className="nav-item support-link" onClick={() => notify(tr('For farming support, contact your local Krishi Vigyan Kendra (KVK) or agriculture extension officer.', language))}><HelpCircle size={18} /><span>{tr('Help & support', language)}</span></button>
          <div className="profile-row"><div className="profile-avatar">{farm.farmer_name ? farm.farmer_name.slice(0, 1).toUpperCase() : 'F'}</div><div className="profile-copy"><strong>{farm.farmer_name || tr('Farmer profile', language)}</strong><span>{tr('Farm owner', language)}</span></div><Settings2 size={17} className="profile-settings" /></div>
        </div>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <button className="icon-btn menu-trigger" onClick={() => setMobileOpen(true)} aria-label={tr('Open navigation', language)}><Menu size={21} /></button>
          <div className="breadcrumb"><span>FasalSetu</span><ChevronRight size={14} /><strong>{t[page]}</strong></div>
          <div className="topbar-right">
            <div className="global-search" onClick={(e) => e.currentTarget.querySelector('input').focus()}><Search size={16} /><input ref={searchInputRef} placeholder={t.search} value={searchText} onChange={(e) => setSearchText(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && searchText.trim()) { setAssistantDraft(searchText.trim()); setSearchText(''); navigate('assistant') } }} /><kbd>⌘ K</kbd></div>
            <button className="language-toggle" onClick={() => setLanguage((current) => { const next = current === 'en' ? 'hi' : 'en'; localStorage.setItem('fasalsetu-language', next); return next })} title={tr('Switch language', language)}><Globe2 size={16} /><span>{language === 'en' ? t.hi : t.en}</span></button>
            <button className="icon-btn notification-btn" aria-label={tr('Notifications', language)} onClick={() => notify('You’re all caught up.')}><Bell size={18} /><i /></button>
          </div>
        </header>
        <div className="page-content">
          {(farmError || historyError || summaryError) && <div className="error-box load-error" role="alert">{[[tr('Farm profile', language), farmError], [tr('Farm history', language), historyError], [tr('Dashboard data', language), summaryError]].filter(([, error]) => error).map(([label, error]) => `${label}: ${tr(error, language)}`).join(' · ')}</div>}
          {page === 'dashboard' && <Dashboard t={t} language={language} weather={weather} weatherError={weatherError} farm={farm} history={history} summary={dashboardSummary} locationName={selectedLocation.name} navigate={navigate} />}
          {page === 'doctor' && <Doctor language={language} notify={notify} onHistoryUpdate={refreshHistory} />}
          {page === 'weather' && <WeatherPage language={language} weather={weather} error={weatherError} selectedLocation={selectedLocation} locationSaveError={locationSaveError} onLocationSelect={selectLocation} />}
          {page === 'advisory' && <Advisory language={language} farm={farm} selectedLocation={selectedLocation} notify={notify} onHistoryUpdate={refreshHistory} />}
          {page === 'assistant' && <Assistant language={language} status={assistantStatus} statusError={assistantStatusError} initialQuestion={assistantDraft} onInitialQuestionConsumed={() => setAssistantDraft('')} onHistoryUpdate={refreshHistory} />}
          {page === 'farm' && <FarmPage language={language} farm={farm} setFarm={setFarm} crops={farmCrops} history={history} notify={notify} onHistoryUpdate={refreshHistory} />}
        </div>
      </main>
      {toast && <div className="toast"><Check size={17} />{tr(toast, language)}</div>}
    </div>
  )
}

function PageHeading({ eyebrow, title, description, action, language = 'en' }) {
  return <div className="page-heading"><div><div className="eyebrow">{tr(eyebrow, language)}</div><h1>{tr(title, language)}</h1><p>{tr(description, language)}</p></div>{action}</div>
}

function Dashboard({ t, language, weather, weatherError, farm, history, summary, locationName, navigate }) {
  const temperature = weather?.current?.temperature_2m
  const rain = weather?.daily?.precipitation_probability_max?.[0]
  const diagnosis = summary?.latest_diagnosis?.prediction
  const hasActivity = summary?.daily_activity?.some((day) => day.count > 0)
  const dailyActivity = summary?.daily_activity?.map((day) => ({
    ...day,
    label: new Date(`${day.date}T12:00:00`).toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en', { weekday: 'short' })
  }))
  return <>
    <PageHeading language={language} eyebrow={new Date().toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en-IN', { weekday: 'long', day: 'numeric', month: 'long' }).toUpperCase()} title={`${t.welcome}${farm.farmer_name ? `, ${farm.farmer_name}` : ''}`} description={t.subtitle} action={<button className="button button-outline" onClick={() => navigate('farm')}><Settings2 size={16} /> {tr('Farm settings', language)}</button>} />
    <div className="dashboard-hero">
      <div className="hero-text"><div className="hero-kicker"><span className="live-dot" /> {tr('YOUR FARM AT A GLANCE', language)}</div><h2>{tr('Grow with confidence.', language)}<br /><em>{tr('One season at a time.', language)}</em></h2><p>{tr('Get the information you need to make your next farm decision.', language)}</p><button className="button button-light" onClick={() => navigate('advisory')}>{tr('Get crop advice', language)} <ArrowRight size={16} /></button></div>
      <div className="hero-art" aria-hidden="true"><div className="sun-disc" /><div className="hero-hill hill-back" /><div className="hero-hill hill-front" /><div className="hero-plant plant-one"><span /><i /><i /></div><div className="hero-plant plant-two"><span /><i /><i /></div><div className="hero-stats"><span>{tr('YOUR FARM', language)}</span><strong>{farm.farm_size_acres || 2} {tr('acres', language)}</strong><small>{tr(farm.crop || 'Wheat', language)} · {tr(farm.growth_stage || 'Vegetative', language)}</small></div></div>
    </div>
    <div className="section-title-row"><div><h2>{t.overview}</h2><p>{tr('Live conditions and insights for your farm', language)}</p></div><div className="updated-label"><span className="live-dot" /> {tr('LIVE OVERVIEW', language)}</div></div>
    <div className="metric-grid">
      <MetricCard language={language} icon={ThermometerSun} color="orange" label="TEMPERATURE" value={temperature != null ? `${Math.round(temperature)}°` : '—'} unit={weather?.current?.temperature_2m != null ? 'C' : 'Awaiting weather'} foot={weather ? 'Open-Meteo · live' : weatherError ? 'Weather unavailable' : 'Connecting to weather'} />
      <MetricCard language={language} icon={Leaf} color="green" label="CROP HEALTH" value={diagnosis ? tr(diagnosis.disease, language) : '—'} unit={diagnosis ? `${Math.round((diagnosis.confidence || 0) * 100)}% model score` : 'not assessed'} foot={diagnosis ? `${tr(diagnosis.crop, language)} · ${tr('verify in the field', language)}` : 'No saved model diagnosis'} />
      <MetricCard language={language} icon={ShieldCheck} color="purple" label="ACTIVE ALERTS" value={weather ? weather.risks.length : '—'} unit={weather ? 'weather risks' : 'no data yet'} foot="Based on available forecast" />
      <MetricCard language={language} icon={Activity} color="blue" label="FARM RECORDS" value={summary?.totals?.history ?? '—'} unit="saved entries" foot={language === 'hi' ? `${summary?.totals?.activities ?? 0} खेत की गतिविधियां दर्ज` : `${summary?.totals?.activities ?? 0} field activities recorded`} />
    </div>
    <div className="content-grid dashboard-content">
      <section className="panel chart-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('LAST 7 DAYS', language)}</div><h3>{tr('Farm activity records', language)}</h3></div><div className="select-small"><span>{tr('SQLite history', language)}</span></div></div>
        {hasActivity ? <><div className="chart-legend"><span><i className="legend-green" /> {tr('Saved events', language)}</span></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={dailyActivity} margin={{ top: 8, right: 4, left: -22, bottom: 0 }}><defs><linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3b8c5a" stopOpacity={0.19} /><stop offset="100%" stopColor="#3b8c5a" stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="#edf0eb" vertical={false} /><XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fill: '#8a958e', fontSize: 11 }} dy={10} /><YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: '#8a958e', fontSize: 11 }} /><Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e8ede8', boxShadow: '0 8px 24px #17251f14' }} /><Area type="monotone" dataKey="count" name={tr('Saved records', language)} stroke="#39885a" strokeWidth={2.5} fill="url(#activityFill)" /></AreaChart></ResponsiveContainer></div><div className="chart-note"><Activity size={14} /> {tr('Counts are calculated from saved SQLite history; they are not sensor measurements.', language)}</div></> : <div className="chart-empty">{tr(summary ? 'No farm records in the last seven days yet.' : 'Loading saved farm activity…', language)}</div>}
      </section>
      <section className="panel weather-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('LOCAL FORECAST', language)}</div><h3>{t.weatherTitle}</h3></div><button className="text-button" onClick={() => navigate('weather')}>{t.seeAll}<ArrowRight size={15} /></button></div>
        <div className="weather-location"><span><span className="location-dot" /> {locationName}</span><span className="weather-source">{weather ? tr('Open-Meteo live', language) : tr('Waiting for data', language)}</span></div>
        {weather ? <div className="weather-now"><CloudSun size={45} strokeWidth={1.3} /><div><strong>{Math.round(weather.current.temperature_2m)}°</strong><span>{weather.current.weather_description || tr('Current conditions', language)}</span></div><div className="weather-highlow"><span>{tr('Wind', language)} {Math.round(weather.current.wind_speed_10m)} km/h</span><span>{tr('Rain', language)} {rain ?? 0}% {tr('today', language)}</span></div></div> : <div className="weather-empty"><Cloud size={26} /><div><strong>{weatherError ? tr('Weather data unavailable', language) : tr('Fetching local conditions', language)}</strong><span>{weatherError ? tr(weatherError, language) : tr('Connecting to Open-Meteo', language)}</span></div></div>}
        {weather && <><div className="weather-week">{(weather.daily?.time || []).slice(0, 5).map((day, index) => <div className="day-forecast" key={day}><span>{index === 0 ? tr('Today', language) : new Date(day).toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en', { weekday: 'short' })}</span><CloudSun size={17} /><strong>{Math.round(weather.daily.temperature_2m_max[index])}°</strong></div>)}</div><p className="fine-print">{weather.irrigation_guidance}</p></>}
      </section>
      <section className="panel alerts-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('PAY ATTENTION', language)}</div><h3>{t.alerts}</h3></div><span className="count-pill">{weather ? weather.risks.length : '—'}</span></div>
        {weather?.risks?.length ? weather.risks.slice(0, 2).map((risk) => <div className="alert-item" key={risk.title}><div className="alert-icon"><AlertTriangle size={17} /></div><div><strong>{risk.title}</strong><p>{risk.message}</p><small>{risk.severity} · {tr('Forecast-based', language)}</small></div></div>) : <div className="empty-alert"><div className="empty-check"><Check size={18} /></div><div><strong>{weather ? t.good : tr('No verified alerts yet', language)}</strong><p>{tr(weather ? 'No significant weather risks in the forecast.' : 'Weather risk checks appear when live forecast is available.', language)}</p></div></div>}
        <button className="panel-link" onClick={() => navigate('weather')}>{tr('View weather intelligence', language)} <ArrowRight size={15} /></button>
      </section>
      <section className="panel recommendations-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('PERSONALIZED GUIDANCE', language)}</div><h3>{t.recommendations}</h3></div><button className="icon-btn subtle" onClick={() => navigate('advisory')} aria-label={tr('More recommendations', language)}><ArrowRight size={18} /></button></div>
        <div className="recommendation-card"><div className="rec-icon"><Droplets size={18} /></div><div><strong>{tr('Build your crop advisory', language)}</strong><p>{tr('Add your crop, soil and growth stage to get tailored guidance.', language)}</p><button className="inline-action" onClick={() => navigate('advisory')}>{tr('Get recommendations', language)} <ArrowRight size={14} /></button></div></div>
        <div className="recommendation-card"><div className="rec-icon light"><Activity size={18} /></div><div><strong>{tr('Check crop health', language)}</strong><p>{tr('Upload a leaf photo. Diagnosis needs a configured model.', language)}</p><button className="inline-action" onClick={() => navigate('doctor')}>{tr('Open crop doctor', language)} <ArrowRight size={14} /></button></div></div>
      </section>
      <section className="panel activity-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('RECENT UPDATES', language)}</div><h3>{t.activity}</h3></div><button className="text-button" onClick={() => navigate('farm')}>{t.seeAll}<ArrowRight size={15} /></button></div>
        {history.length ? history.slice(0, 3).map((entry) => <div className="activity-row" key={entry.id}><span className="activity-dot" /><div><strong>{tr(entry.title, language)}</strong><p>{tr(entry.details, language)}</p><small>{new Date(entry.created_at).toLocaleString(language === 'hi' ? 'hi-IN' : 'en-IN')}</small></div></div>) : <div className="activity-empty"><Activity size={20} /><span>{tr('Your farm activity will show here as you use the app.', language)}</span></div>}
      </section>
    </div>
  </>
}

function MetricCard({ icon: Icon, color, label, value, unit, foot, language = 'en' }) {
  return <div className="metric-card"><div className={`metric-icon ${color}`}><Icon size={18} /></div><div className="metric-label">{tr(label, language)}</div><div className="metric-value">{value}<span>{tr(unit, language)}</span></div><div className="metric-foot">{tr(foot, language)}</div></div>
}

function Doctor({ language, notify, onHistoryUpdate }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState('')
  const previewRef = useRef('')
  const fileInputRef = useRef(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [modelStatus, setModelStatus] = useState({ loading: true, available: false, message: 'Checking model availability…' })
  useEffect(() => () => {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current)
  }, [])
  useEffect(() => {
    let active = true
    api.cropDiagnosisStatus()
      .then((status) => { if (active) setModelStatus({ ...status, loading: false }) })
      .catch((statusError) => {
        if (active) setModelStatus({ loading: false, available: false, message: statusError.message })
      })
    return () => { active = false }
  }, [])
  const clearSelection = () => {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current)
    previewRef.current = ''
    setPreview('')
    setFile(null)
    setResult(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }
  const onFile = (selected) => {
    if (!selected) return
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(selected.type)) {
      clearSelection()
      setError('Choose a JPG, PNG or WebP image.')
      return
    }
    if (selected.size > 10 * 1024 * 1024) {
      clearSelection()
      setError('Image must be 10 MB or smaller.')
      return
    }
    if (previewRef.current) URL.revokeObjectURL(previewRef.current)
    setFile(selected)
    previewRef.current = URL.createObjectURL(selected)
    setPreview(previewRef.current)
    setResult(null)
    setError('')
  }
  const analyze = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    try { setResult(await api.analyzeCrop(file, language)); await onHistoryUpdate() }
    catch (e) { setError(e.message); notify('Crop diagnosis could not be completed.') }
    finally { setLoading(false) }
  }
  const modelBadge = modelStatus.loading
    ? tr('CHECKING MODEL', language)
    : modelStatus.available
      ? tr('MODEL READY', language)
      : tr('DEMO MODE · NO MODEL', language)
  return <>
    <PageHeading language={language} eyebrow="AI CROP DOCTOR" title="A closer look at crop health" description="Upload a clear leaf photo for a model-assisted classification. Results require field confirmation." />
    <div className="doctor-grid"><section className="panel upload-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('LEAF IMAGE', language)}</div><h3>{tr('Upload a crop photo', language)}</h3></div><span className={`model-status ${modelStatus.available ? 'model-ready' : ''}`}><span /> {modelBadge}</span></div>
      {preview ? <div className="image-preview"><img src={preview} alt={tr('Selected crop leaf', language)} /><button className="remove-image" onClick={() => { clearSelection(); setError('') }}><X size={16} /> {tr('Remove', language)}</button></div> :
        <label className="upload-drop"><input ref={fileInputRef} type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => onFile(e.target.files?.[0])} /><div className="upload-icon"><Upload size={23} /></div><strong>{tr('Drop a leaf photo here', language)}</strong><span>{language === 'hi' ? <>या <u>फाइल चुनें</u></> : <>or <u>browse files</u></>}</span><small>{tr('JPG, PNG or WebP · Max 10 MB', language)}</small></label>}
      {error && <div className="error-box"><AlertTriangle size={17} />{tr(error, language)}</div>}
      {result && <div className="diagnosis-results" aria-live="polite">
        <div className="result-box"><BadgeCheck size={19} /><div><strong>{tr(result.prediction.crop, language)} · {tr(result.prediction.disease, language)}</strong><p>{tr('Model score:', language)} {(result.prediction.confidence * 100).toFixed(1)}%{result.prediction.uncertain ? ` · ${tr('uncertain result', language)}` : ''}</p></div></div>
        <div className="confidence-warning"><strong>{tr('Important:', language)}</strong> {tr(result.confidence_warning, language)}</div>
        <div className="diagnosis-guidance">
          <div><strong>{tr('Possible symptoms', language)}</strong><p>{tr(result.guidance.symptoms, language)}</p></div>
          <div><strong>{tr('Safer next steps', language)}</strong><p>{tr(result.guidance.treatment, language)}</p></div>
          <div><strong>{tr('Prevention', language)}</strong><p>{tr(result.guidance.prevention, language)}</p></div>
        </div>
        <p className="fine-print">{result.model.name} · {result.model.dataset} · {result.model.class_count} classes</p>
        <p className="fine-print">{tr(result.disclaimer, language)}</p>
      </div>}
      <button className="button button-primary full-button" disabled={!file || loading || modelStatus.loading || !modelStatus.available} onClick={analyze}>{loading ? tr('Analyzing leaf…', language) : modelStatus.available ? tr('Analyze leaf', language) : tr('Analysis unavailable', language)} <ArrowRight size={16} /></button>
      {!modelStatus.available && <div className="model-unavailable" role="status">{tr(modelStatus.message, language)} {tr('Install a trained model to enable classification.', language)}</div>}
      <div className="disclaimer"><ShieldCheck size={16} /><span>{tr('Model scores are not guaranteed accuracy. Predictions need local expert confirmation; no pesticide dosage is provided. Images are not retained by the app.', language)}</span></div>
    </section>
    <aside className="doctor-aside"><div className="panel how-panel"><div className="eyebrow">{tr('HOW TO GET A GOOD PHOTO', language)}</div><h3>{tr('A few tips for a clearer check', language)}</h3>{[['01','Show the whole leaf','Include both healthy and affected parts.'],['02','Use natural light','Avoid heavy shadows and blur.'],['03','One leaf at a time','Keep the leaf in focus against a plain background.']].map(([n, title, desc]) => <div className="tip-row" key={n}><span>{n}</span><div><strong>{tr(title, language)}</strong><p>{tr(desc, language)}</p></div></div>)}</div>
      <div className="trust-card"><div className="trust-icon"><ShieldCheck size={21} /></div><div><strong>{tr('Designed for responsible advice', language)}</strong><p>{tr('Predictions require local confirmation. The current model is trained for PlantVillage classes and may not generalize to field conditions.', language)}</p></div></div></aside></div>
  </>
}

function WeatherPage({ language, weather, error, selectedLocation, locationSaveError, onLocationSelect }) {
  const [query, setQuery] = useState('')
  const [locations, setLocations] = useState([])
  const [searching, setSearching] = useState(false)
  const [locationError, setLocationError] = useState('')
  const searchLocations = async (event) => {
    event.preventDefault()
    if (query.trim().length < 2) { setLocationError('Enter at least 2 characters to search.'); return }
    setSearching(true)
    setLocationError('')
    try {
      const response = await api.locations(query.trim())
      setLocations(response.results)
      if (!response.results.length) setLocationError('No matching locations found.')
    } catch (searchError) {
      setLocations([])
      setLocationError(searchError.message)
    } finally {
      setSearching(false)
    }
  }
  return <>
    <PageHeading language={language} eyebrow="WEATHER INTELLIGENCE" title="Know what’s coming" description="Live conditions and forecast from Open-Meteo. Weather risks are guidance, not a substitute for local alerts." action={<div className="source-tag"><span className="live-dot" /> {weather ? tr('LIVE · OPEN-METEO', language) : tr('DATA UNAVAILABLE', language)}</div>} />
    <form className="location-search-panel" onSubmit={searchLocations}><label htmlFor="weather-location-search">{tr('Choose a forecast location', language)}</label><div className="location-search-controls"><input id="weather-location-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={tr('Search city or district', language)} /><button className="button button-primary" disabled={searching}>{searching ? tr('Searching…', language) : tr('Search locations', language)}</button></div><span className="selected-location">{tr('Selected:', language)} {selectedLocation.name}</span>{locationSaveError && <p className="location-error" role="alert">{tr(locationSaveError, language)}</p>}{locationError && <p className="location-error" role="alert">{tr(locationError, language)}</p>}{locations.length > 0 && <div className="location-results" role="listbox" aria-label={tr('Location results', language)}>{locations.map((location) => <button type="button" role="option" aria-selected={selectedLocation.name === location.name} key={`${location.latitude}-${location.longitude}`} onClick={() => { onLocationSelect(location); setLocations([]); setQuery('') }}>{location.name}</button>)}</div>}</form>
    {weather ? <><div className="weather-summary"><div className="weather-summary-main"><div className="weather-current-icon"><CloudSun size={42} /></div><div><span>{language === 'hi' ? 'अभी' : 'NOW'} · {weather.location_name || tr('Your selected location', language)}</span><strong>{Math.round(weather.current.temperature_2m)}°C</strong><p>{weather.current.weather_description}</p></div></div><div className="weather-facts"><div><Droplets size={18} /><span>{tr('Humidity', language)}</span><strong>{weather.current.relative_humidity_2m}%</strong></div><div><Wind size={18} /><span>{tr('Wind speed', language)}</span><strong>{Math.round(weather.current.wind_speed_10m)} km/h</strong></div><div><CloudDrizzle size={18} /><span>{tr('Rain chance today', language)}</span><strong>{weather.daily.precipitation_probability_max?.[0] ?? '—'}%</strong></div><div><ThermometerSun size={18} /><span>{tr('Feels like', language)}</span><strong>{Math.round(weather.current.apparent_temperature)}°C</strong></div></div></div>
      <section className="panel forecast-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('NEXT 7 DAYS', language)}</div><h3>{tr('Daily forecast', language)}</h3></div><span className="weather-source">{tr('Source: Open-Meteo', language)}</span></div><div className="forecast-list">{weather.daily.time.map((day, index) => <div className="forecast-row" key={day}><strong>{index === 0 ? tr('Today', language) : new Date(day).toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en', { weekday: 'long' })}</strong><span>{new Date(day).toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en', { month: 'short', day: 'numeric' })}</span><CloudSun size={20} /><span className="rain-chance"><Droplets size={14} /> {weather.daily.precipitation_probability_max?.[index] ?? 0}%</span><div className="temp-range"><b>{Math.round(weather.daily.temperature_2m_max[index])}°</b><i /><span>{Math.round(weather.daily.temperature_2m_min[index])}°</span></div><span className="rain-mm">{weather.daily.precipitation_sum?.[index] ?? 0} mm {tr('rain', language)}</span></div>)}</div></section>
      <section className="panel irrigation-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('IRRIGATION CHECK', language)}</div><h3>{tr('Forecast-informed irrigation check', language)}</h3></div><Droplets className="heading-plant" size={21} /></div><p>{weather.irrigation_guidance}</p><p className="fine-print">{tr('Check field soil moisture and follow local agronomic advice; this weather rule is informational.', language)}</p></section>
      <section className="panel risk-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('FIELD READINESS', language)}</div><h3>{tr('Weather risk analysis', language)}</h3></div><span className="rules-tag">{tr('RULE-BASED', language)}</span></div>{weather.risks?.length ? weather.risks.map((risk) => <div className="risk-row" key={risk.title}><div className="alert-icon"><AlertTriangle size={17} /></div><div><strong>{risk.title}</strong><p>{risk.message}</p></div><span className="severity">{risk.severity}</span></div>) : <div className="no-risk"><BadgeCheck size={20} /><span>{tr('No high weather risks detected in this forecast.', language)}</span></div>}<p className="fine-print">{tr('Rules use the available 7-day forecast and are informational. Follow official IMD and local advisories.', language)}</p></section>
    </> : <div className="panel unavailable-panel"><Cloud size={30} /><h3>{tr('Live weather isn’t available', language)}</h3><p>{error ? tr(error, language) : tr('Waiting for the backend to connect to Open-Meteo.', language)}</p><p>{tr('Start the FastAPI service and check your internet connection. No weather values are filled in with estimates.', language)}</p></div>}
  </>
}

function Advisory({ language, farm, selectedLocation, notify, onHistoryUpdate }) {
  const [form, setForm] = useState({
    crop: farm.crop || 'Wheat',
    soil_type: farm.soil_type || 'Loamy',
    location: selectedLocation.name,
    growth_stage: farm.growth_stage || 'Vegetative',
    farm_size_acres: farm.farm_size_acres || 2,
    latitude: selectedLocation.latitude,
    longitude: selectedLocation.longitude,
    language
  })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  useEffect(() => {
    setForm((current) => ({ ...current, language }))
  }, [language])
  const submit = async (e) => {
    e.preventDefault(); setLoading(true); setError('')
    try { setResult(await api.advisory(form)); await onHistoryUpdate() } catch (e) { setError(e.message); notify('Could not load crop guidance.') } finally { setLoading(false) }
  }
  return <>
    <PageHeading language={language} eyebrow="SMART CROP ADVISORY" title="Advice that starts with your field" description="Tell us what you’re growing. Recommendations are rule-based and should be confirmed locally." />
    <div className="advisory-grid"><form className="panel advisory-form" onSubmit={submit}><div className="panel-heading"><div><div className="eyebrow">{tr('YOUR FIELD DETAILS', language)}</div><h3>{tr('Personalize your guidance', language)}</h3></div><Sprout className="heading-plant" size={22} /></div>
      <div className="form-grid"><label>{tr('Crop', language)}<select value={form.crop} onChange={(e) => setForm({ ...form, crop: e.target.value })}>{['Wheat','Rice','Maize','Cotton','Tomato','Chickpea','Soybean','Other'].map((x) => <option key={x} value={x}>{tr(x, language)}</option>)}</select></label><label>{tr('Soil type', language)}<select value={form.soil_type} onChange={(e) => setForm({ ...form, soil_type: e.target.value })}>{['Loamy','Clay','Sandy','Black cotton','Red','Alluvial','Other'].map((x) => <option key={x} value={x}>{tr(x, language)}</option>)}</select></label><label>{tr('Forecast location', language)}<input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value, latitude: null, longitude: null })} required /><small>{tr('Forecast-aware guidance uses the selected Weather location. Edit the name to request general guidance without a forecast.', language)}</small></label><label>{tr('Farm size (acres)', language)}<input type="number" min="0.1" max="100000" step="0.1" value={form.farm_size_acres} onChange={(e) => setForm({ ...form, farm_size_acres: Number(e.target.value) })} required /></label><label>{tr('Growth stage', language)}<select value={form.growth_stage} onChange={(e) => setForm({ ...form, growth_stage: e.target.value })}>{['Sowing','Seedling','Vegetative','Flowering','Fruiting','Harvest'].map((x) => <option key={x} value={x}>{tr(x, language)}</option>)}</select></label></div>
      {error && <div className="error-box"><AlertTriangle size={17} />{tr(error, language)}</div>}<button className="button button-primary" disabled={loading}>{loading ? tr('Preparing guidance…', language) : tr('Get my crop guidance', language)} <ArrowRight size={16} /></button><div className="fine-print">{tr('General educational guidance only. It is not a diagnosis or pesticide prescription.', language)}</div></form>
      <div className="advisory-result">{result ? <div className="panel guidance-panel"><div className="result-heading"><div className="result-badge"><Sprout size={20} /></div><div><div className="eyebrow">{result.label}</div><h3>{tr(result.crop, language)} · {tr(result.growth_stage, language)}</h3></div></div><p className="result-summary">{result.summary}</p>{result.recommendations.map((item, index) => <div className="guidance-item" key={item.title}><span>{String(index + 1).padStart(2, '0')}</span><div><strong>{item.title}</strong><p>{item.detail}</p></div></div>)}{result.weather_note && <div className="error-box" role="status">{result.weather_note}</div>}<p className="fine-print">{result.disclaimer}</p><p className="fine-print">{tr('References:', language)} {result.references?.join(' · ')}</p></div> : <div className="advisory-blank"><div className="advisory-illustration"><Sprout size={38} /><span>+</span><Leaf size={29} /></div><h3>{tr('Good guidance begins with context', language)}</h3><p>{tr('Choose your crop, soil and growth stage to get practical, general recommendations for your field.', language)}</p></div>}</div></div>
  </>
}

function Assistant({ language, status, statusError, initialQuestion, onInitialQuestionConsumed, onHistoryUpdate }) {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const initialQuestionSent = useRef(false)
  const suggestions = language === 'hi' ? ['गेहूं में पीली पत्तियों का क्या करें?', 'सिंचाई कब करनी चाहिए?', 'मिट्टी की सेहत कैसे सुधारें?'] : ['How can I improve soil health?', 'When should I irrigate wheat?', 'What can cause yellow leaves?']
  const send = async (value = question) => {
    if (!value.trim() || loading) return
    const prompt = value.trim(); setQuestion(''); setMessages((items) => [...items, { role: 'user', text: prompt }]); setLoading(true); setError('')
    try {
      const response = await api.ask(prompt, language)
      setMessages((items) => [...items, { role: 'assistant', text: response.answer, label: response.label }])
      await onHistoryUpdate()
    } catch (e) { setError(e.message) } finally { setLoading(false) }
  }
  useEffect(() => {
    if (initialQuestion && !initialQuestionSent.current) {
      initialQuestionSent.current = true
      send(initialQuestion)
      onInitialQuestionConsumed()
    }
  }, [initialQuestion, onInitialQuestionConsumed])
  return <>
    <PageHeading language={language} eyebrow="FARM ASSISTANT" title={language === 'hi' ? 'खेती के बारे में पूछें' : 'Ask a question about farming'} description={language === 'hi' ? 'अंग्रेज़ी या हिंदी में सवाल पूछें। AI उपलब्ध न होने पर नियम-आधारित सलाह दी जाएगी।' : 'Ask in English or Hindi. A configured AI provider is used when available; otherwise the assistant uses curated fallback guidance.'} />
    <div className="assistant-layout"><section className="panel chat-panel"><div className="chat-top"><div className="assistant-avatar"><Sprout size={20} /></div><div><strong>FasalSetu Farm Guide</strong><span><i /> {statusError ? tr('Assistant status unavailable', language) : status?.generative_available ? `${tr('AI available', language)} · ${status.provider || 'configured provider'}` : tr('Curated fallback available', language)}</span></div><span className="curated-tag">{statusError ? tr('ASSISTANT UNAVAILABLE', language) : status?.generative_available ? tr('AI + FALLBACK', language) : tr('FALLBACK MODE', language)}</span></div>
      <div className="chat-body">{messages.length === 0 ? <div className="chat-welcome"><div className="chat-welcome-icon"><MessageCircle size={24} /></div><h3>{language === 'hi' ? 'नमस्ते! आज खेत में क्या चल रहा है?' : 'Namaste! What’s happening in your field?'}</h3><p>{language === 'hi' ? 'नीचे दिए सवालों से शुरू करें या अपना सवाल लिखें।' : tr('Start with a suggestion or type your own question below.', language)}</p><div className="suggestion-list">{suggestions.map((item) => <button key={item} onClick={() => send(item)}>{item}<ArrowUpRight size={15} /></button>)}</div></div> : <div className="message-list">{messages.map((message, index) => <div className={`message ${message.role}`} key={index}><div className="message-avatar">{message.role === 'assistant' ? <Sprout size={15} /> : 'F'}</div><div className="message-content"><p>{message.text}</p>{message.label && <span>{tr(message.label, language)}</span>}</div></div>)}{loading && <div className="typing-state"><span /><span /><span /> {tr('Checking guidance…', language)}</div>}</div>}</div>
      {error && <div className="error-box chat-error">{tr(error, language)}</div>}<form className="chat-composer" onSubmit={(e) => { e.preventDefault(); send() }}><input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder={language === 'hi' ? 'खेती से जुड़ा सवाल पूछें…' : tr('Ask a farming question…', language)} /><button className="send-button" disabled={loading || !question.trim()} aria-label={tr('Send question', language)}><ArrowRight size={18} /></button></form></section>
      <aside className="assistant-aside"><div className="panel aside-info"><div className="guide-icon"><BookOpen size={19} /></div><h3>{tr('Practical guidance, with context', language)}</h3><p>{tr('AI replies are labeled when a provider is configured. If unavailable, a curated rule-based fallback answers common questions.', language)}</p><div className="info-divider" /><div className="info-line"><ShieldCheck size={16} /><span>{tr('Farm crop and soil context may be sent to the configured provider', language)}</span></div><div className="info-line"><Globe2 size={16} /><span>{tr('English & Hindi questions', language)}</span></div><div className="info-line"><AlertTriangle size={16} /><span>{tr('Verify critical decisions locally', language)}</span></div></div><div className="local-help"><strong>{tr('Need crop-specific help?', language)}</strong><p>{tr('Talk to your local Krishi Vigyan Kendra (KVK) or agriculture extension officer.', language)}</p></div></aside></div>
  </>
}

function FarmPage({ language, farm, setFarm, crops, history, notify, onHistoryUpdate }) {
  const [form, setForm] = useState(farm)
  const [saving, setSaving] = useState(false)
  const [cropForm, setCropForm] = useState({ crop: 'Wheat', variety: '', area_acres: '', planting_date: '', growth_stage: 'Sowing' })
  const [activityForm, setActivityForm] = useState({ activity_type: 'other', details: '', crop: farm.crop || '' })
  const [recordError, setRecordError] = useState('')
  const [recordSaving, setRecordSaving] = useState(false)
  useEffect(() => setForm(farm), [farm])
  useEffect(() => setActivityForm((current) => ({ ...current, crop: farm.crop || '' })), [farm.crop])
  const submit = async (e) => {
    e.preventDefault(); setSaving(true)
    try { const saved = await api.saveFarm(form); setFarm(saved); await onHistoryUpdate(); notify('Farm profile saved.') }
    catch (e) { notify(`Could not save profile: ${e.message}`) }
    finally { setSaving(false) }
  }
  const addCrop = async (event) => {
    event.preventDefault()
    setRecordSaving(true)
    setRecordError('')
    try {
      await api.addFarmCrop({
        ...cropForm,
        area_acres: cropForm.area_acres ? Number(cropForm.area_acres) : null,
        planting_date: cropForm.planting_date || null
      })
      setCropForm({ crop: 'Wheat', variety: '', area_acres: '', planting_date: '', growth_stage: 'Sowing' })
      await onHistoryUpdate()
      notify('Crop record saved.')
    } catch (error) {
      setRecordError(error.message)
    } finally {
      setRecordSaving(false)
    }
  }
  const removeCrop = async (crop) => {
    if (!window.confirm(`${tr('Remove crop record?', language)} (${crop.crop})`)) return
    try {
      await api.deleteFarmCrop(crop.id)
      await onHistoryUpdate()
      notify('Crop record removed.')
    } catch (error) {
      setRecordError(error.message)
    }
  }
  const addActivity = async (event) => {
    event.preventDefault()
    setRecordSaving(true)
    setRecordError('')
    try {
      await api.addFarmActivity({
        ...activityForm,
        crop: activityForm.crop || null
      })
      setActivityForm((current) => ({ ...current, details: '' }))
      await onHistoryUpdate()
      notify('Farm activity saved.')
    } catch (error) {
      setRecordError(error.message)
    } finally {
      setRecordSaving(false)
    }
  }
  return <>
    <PageHeading language={language} eyebrow="YOUR FARM" title="A little about your field" description="Keep your farm details up to date to make future guidance more relevant." />
    <div className="farm-page-grid"><form className="panel farm-form" onSubmit={submit}><div className="panel-heading"><div><div className="eyebrow">{tr('FARM PROFILE', language)}</div><h3>{tr('Farmer & field details', language)}</h3></div><div className="profile-big"><Sprout size={22} /></div></div><div className="form-grid"><label>{tr('Farmer name', language)}<input value={form.farmer_name || ''} onChange={(e) => setForm({ ...form, farmer_name: e.target.value })} placeholder={tr('Your name', language)} /></label><label>{tr('Location', language)}<input value={form.location || ''} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder={tr('Village, district, state', language)} required /></label><label>{tr('Farm size (acres)', language)}<input type="number" min="0.1" step="0.1" value={form.farm_size_acres || ''} onChange={(e) => setForm({ ...form, farm_size_acres: Number(e.target.value) })} required /></label><label>{tr('Main crop', language)}<select value={form.crop || 'Wheat'} onChange={(e) => setForm({ ...form, crop: e.target.value })}>{['Wheat','Rice','Maize','Cotton','Tomato','Chickpea','Soybean','Other'].map((x) => <option key={x} value={x}>{tr(x, language)}</option>)}</select></label><label>{tr('Soil type', language)}<select value={form.soil_type || 'Loamy'} onChange={(e) => setForm({ ...form, soil_type: e.target.value })}>{['Loamy','Clay','Sandy','Black cotton','Red','Alluvial','Other'].map((x) => <option key={x} value={x}>{tr(x, language)}</option>)}</select></label><label>{tr('Growth stage', language)}<select value={form.growth_stage || 'Vegetative'} onChange={(e) => setForm({ ...form, growth_stage: e.target.value })}>{['Sowing','Seedling','Vegetative','Flowering','Fruiting','Harvest'].map((x) => <option key={x} value={x}>{tr(x, language)}</option>)}</select></label></div><button className="button button-primary" disabled={saving}>{saving ? tr('Saving…', language) : tr('Save farm profile', language)} <Check size={16} /></button></form>
      {recordError && <div className="error-box" role="alert">{tr(recordError, language)}</div>}
      <section className="panel crop-record-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('CROP RECORDS', language)}</div><h3>{tr('Track crops in your farm', language)}</h3></div><span className="count-pill">{crops.length}</span></div>
        <form className="record-form" onSubmit={addCrop}><label>{tr('Crop', language)}<select value={cropForm.crop} onChange={(event) => setCropForm({ ...cropForm, crop: event.target.value })}>{['Wheat','Rice','Maize','Cotton','Tomato','Chickpea','Soybean','Other'].map((item) => <option key={item} value={item}>{tr(item, language)}</option>)}</select></label><label>{tr('Variety', language)}<input value={cropForm.variety} onChange={(event) => setCropForm({ ...cropForm, variety: event.target.value })} maxLength="100" /></label><label>{tr('Area (acres)', language)}<input type="number" min="0.1" step="0.1" value={cropForm.area_acres} onChange={(event) => setCropForm({ ...cropForm, area_acres: event.target.value })} /></label><label>{tr('Planting date', language)}<input type="date" value={cropForm.planting_date} onChange={(event) => setCropForm({ ...cropForm, planting_date: event.target.value })} /></label><label>{tr('Growth stage', language)}<select value={cropForm.growth_stage} onChange={(event) => setCropForm({ ...cropForm, growth_stage: event.target.value })}>{['Sowing','Seedling','Vegetative','Flowering','Fruiting','Harvest'].map((item) => <option key={item} value={item}>{tr(item, language)}</option>)}</select></label><button className="button button-primary" disabled={recordSaving}>{recordSaving ? tr('Saving…', language) : tr('Add crop', language)} <Check size={15} /></button></form>
        {crops.length ? <div className="crop-record-list">{crops.map((crop) => <div className="crop-record" key={crop.id}><div><strong>{tr(crop.crop, language)}{crop.variety ? ` · ${crop.variety}` : ''}</strong><p>{crop.area_acres ? `${crop.area_acres} ${tr('acres', language)} · ` : ''}{tr(crop.growth_stage, language)}{crop.planting_date ? ` · ${tr('planted', language)} ${crop.planting_date}` : ''}</p></div><button className="text-button" type="button" onClick={() => removeCrop(crop)} aria-label={`${tr('Remove', language)} ${crop.crop}`}>{tr('Remove', language)}</button></div>)}</div> : <p className="record-empty">{tr('No crop records yet. Add one above to track field progress.', language)}</p>}
      </section>
      <form className="panel activity-form" onSubmit={addActivity}><div className="panel-heading"><div><div className="eyebrow">{tr('FIELD JOURNAL', language)}</div><h3>{tr('Record farm activity', language)}</h3></div><Activity className="heading-plant" size={21} /></div><div className="record-form"><label>{tr('Activity', language)}<select value={activityForm.activity_type} onChange={(event) => setActivityForm({ ...activityForm, activity_type: event.target.value })}>{[['planting','Planting'],['irrigation','Irrigation'],['fertilizing','Fertilizing'],['scouting','Field scouting'],['harvest','Harvest'],['other','Other']].map(([value,label]) => <option key={value} value={value}>{tr(label, language)}</option>)}</select></label><label>{tr('Crop', language)}<select value={activityForm.crop} onChange={(event) => setActivityForm({ ...activityForm, crop: event.target.value })}><option value="">{tr('Not specified', language)}</option>{[...new Set([farm.crop, ...crops.map((crop) => crop.crop)].filter(Boolean))].map((crop) => <option key={crop} value={crop}>{tr(crop, language)}</option>)}</select></label></div><label className="activity-details">{tr('Notes', language)}<textarea value={activityForm.details} onChange={(event) => setActivityForm({ ...activityForm, details: event.target.value })} minLength="2" maxLength="1000" required placeholder={tr('What did you do or observe?', language)} /></label><button className="button button-primary" disabled={recordSaving || activityForm.details.trim().length < 2}>{recordSaving ? tr('Saving…', language) : tr('Save activity', language)} <Check size={15} /></button></form>
      <section className="panel diagnosis-history-panel"><div className="panel-heading"><div><div className="eyebrow">{tr('SAVED RECORDS', language)}</div><h3>{tr('Advisory, diagnosis & activity history', language)}</h3></div><span className="count-pill">{history.length}</span></div>{history.length ? history.map((entry) => <div className="history-item" key={entry.id}><div className="history-icon"><Activity size={16} /></div><div><strong>{tr(entry.title, language)}</strong><p>{tr(entry.details, language)}</p><span>{new Date(entry.created_at).toLocaleString(language === 'hi' ? 'hi-IN' : 'en-IN')}</span></div></div>) : <div className="history-empty"><BarChart3 size={24} /><strong>{tr('No saved history yet', language)}</strong><p>{tr('Advisories, completed model diagnoses and farm activities will appear here.', language)}</p></div>}<div className="history-note"><ShieldCheck size={16} /><span>{tr('Records persist in the local SQLite database. Uploaded images are not stored.', language)}</span></div></section>
    </div>
  </>
}

export default App
