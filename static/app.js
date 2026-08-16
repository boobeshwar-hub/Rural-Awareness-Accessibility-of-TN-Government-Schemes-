// Global state holding only dynamically detected user attributes
let currentProfile = {};

// ============================================================================
// 1. CORE MATCHING FUNCTION (Sends Only Real Extracted Data)
// ============================================================================
async function checkEligibility(profileToSend = null) {
  const resultsContainer = document.getElementById('results');
  
  // Use passed profile or the current dynamic state
  const activeProfile = profileToSend || currentProfile;

  // Ensure user has provided at least one parameter via Voice, OCR, or Form
  if (!activeProfile || Object.keys(activeProfile).length === 0) {
    resultsContainer.innerHTML = `
      <div style="background:#fff3cd; color:#856404; padding:12px; border-radius:6px; margin-top:10px;">
        ⚠️ தயவுசெய்து முதலில் <b>குரல் மூலம் பேசுங்கள்</b> அல்லது <b>ஆவணத்தைப் பதிவேற்றவும்</b>.
      </div>`;
    return;
  }

  resultsContainer.innerHTML = "<p>🔍 திட்டங்கள் சரிபார்க்கப்படுகின்றன... (Matching schemes...)</p>";

  try {
    const response = await fetch('/api/match-schemes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(activeProfile)
    });

    const data = await response.json();

    // 1. Render Summary Text
    let html = `<h3>பொருத்தமான திட்டங்கள் (${data.matched_count || 0}):</h3>`;
    if (data.text_summary_ta) {
      html += `<p style="font-size: 14px; color: #333; margin-bottom: 10px;">${data.text_summary_ta}</p>`;
    }

    // 2. Play Tamil Voice Audio
    if (data.audio_url) {
      html += `<audio controls autoplay src="${data.audio_url}?t=${new Date().getTime()}"></audio>`;
    }

    // 3. Render Scheme Cards
    if (data.schemes && data.schemes.length > 0) {
      data.schemes.forEach(s => {
        const docs = s.required_documents || [];
        const stipendBadge = s.monthly_stipend > 0 
          ? `<span style="background:#28a745; color:white; padding:3px 8px; border-radius:4px; font-size:12px;">மாதம் ₹${s.monthly_stipend}</span>` 
          : '';

        html += `
          <div class="card" style="background:#e7f3fe; border-left:6px solid #2196F3; padding:12px; margin-top:10px; border-radius:6px; text-align:left;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <h4 style="color:#0056b3; margin:0;">${s.scheme_name_ta}</h4>
              ${stipendBadge}
            </div>
            <p style="font-size:13px; color:#444; margin-bottom:6px;">${s.description_ta}</p>
            <small style="color:#666;"><b>தேவையான சான்றிதழ்கள்:</b> ${docs.join(', ')}</small>
          </div>
        `;
      });
    } else {
      html += "<p style='color:#666; margin-top:10px;'>உங்கள் விவரங்களுக்குப் பொருத்தமான திட்டங்கள் எதுவும் கண்டறியப்படவில்லை.</p>";
    }

    resultsContainer.innerHTML = html;

  } catch (err) {
    console.error("Eligibility check error:", err);
    resultsContainer.innerHTML = "<p style='color:red;'>சேவையகத்தை இணைப்பதில் பிழை ஏற்பட்டது.</p>";
  }
}

// ============================================================================
// 2. DYNAMIC VOICE RECOGNITION & PARSING (Tamil Speech -> JSON)
// ============================================================================
function startVoiceRecognition() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = 'ta-IN'; // Tamil (India)

  const micBtn = document.getElementById('micBtn');
  if (micBtn) micBtn.innerText = "🎙️ கேட்டுக்கொண்டிருக்கிறது... (Listening...)";

  recognition.start();

  recognition.onresult = function(event) {
    if (micBtn) micBtn.innerText = "🎙️ குரல் மூலம் கேட்க (Tamil Speech)";
    const speechResult = event.results[0][0].transcript;
    
    // Parse Tamil speech text dynamically without hardcoded defaults
    const extractedVoiceData = parseTamilVoiceToProfile(speechResult);
    
    // Merge extracted voice data into active profile
    currentProfile = { ...currentProfile, ...extractedVoiceData };
    console.log("Dynamically Extracted Profile from Voice:", currentProfile);

    // Show what parameters were detected
    displayExtractedSummary(currentProfile, speechResult);

    // Run scheme matching with dynamic data
    checkEligibility(currentProfile);
  };

  recognition.onerror = function(event) {
    if (micBtn) micBtn.innerText = "🎙️ குரல் மூலம் கேட்க (Tamil Speech)";
    console.error("Speech Recognition Error:", event.error);
  };
}

// Dynamic Tamil NLP Extractor
function parseTamilVoiceToProfile(text) {
  const dynamicData = {};

  // 1. Gender Extraction
  if (/மாணவி|பெண்|தாய்|மகளிர்|அம்மா|மனைவி/i.test(text)) {
    dynamicData.gender = "female";
    dynamicData.is_head_of_family = true;
  } else if (/மாணவர்|ஆண்|விவசாயி|தந்தை|அப்பா|கணவர்/i.test(text)) {
    dynamicData.gender = "male";
  }

  // 2. Occupation & Farming Status
  if (/விவசாயி|விவசாயம்|உழவர்|நிலம்/i.test(text)) {
    dynamicData.is_agricultural_laborer = true;
    dynamicData.is_landholding_farmer = true;
  }

  // 3. School & College Education Status
  if (/அரசுப் பள்ளி|அரசு பள்ளி|கவர்மெண்ட் பள்ளி/i.test(text)) {
    dynamicData.is_govt_school_studied = true;
  }
  if (/கல்லூரி|படிக்கிறேன்|உயர்கல்வி|காலேஜ்|படிக்கும்/i.test(text)) {
    dynamicData.pursuing_higher_education = true;
  }

  // 4. Special Welfare Categories
  if (/விதவை/i.test(text)) {
    dynamicData.is_widow = true;
    dynamicData.gender = "female";
  }
  if (/மாற்றுத்திறனாளி|ஊனம்/i.test(text)) {
    dynamicData.is_differently_abled = true;
  }
  if (/கர்ப்பிணி|கர்ப்பம்|தாய்மை/i.test(text)) {
    dynamicData.is_pregnant = true;
    dynamicData.gender = "female";
  }

  // 5. Dynamic Age Extraction (e.g., "வயது 20" or "20 வயது")
  const ageMatch = text.match(/(?:வயது|age)\s*(\d+)|(\d+)\s*(?:வயது|age)/i);
  if (ageMatch) {
    dynamicData.age = parseInt(ageMatch || ageMatch);
  }

  // 6. Dynamic Income Extraction (e.g., "வருமானம் 80000" or "ரூபாய் 120000")
  const incomeMatch = text.match(/(?:வருமானம்|சம்பளம்|income|ரூபாய்)\s*:?\s*(\d+[\d,]*)|(\d+[\d,]*)\s*(?:வருமானம்|ரூபாய்)/i);
  if (incomeMatch) {
    const rawVal = (incomeMatch || incomeMatch).replace(/,/g, '');
    dynamicData.annual_income = parseInt(rawVal);
  }

  return dynamicData;
}

// ============================================================================
// 3. DYNAMIC DOCUMENT OCR UPLOAD (Image -> OCR -> JSON)
// ============================================================================
async function uploadDocument() {
  const input = document.getElementById('documentInput');
  if (!input.files[0]) return;

  const resultsContainer = document.getElementById('results');
  resultsContainer.innerHTML = "<p>📄 ஆவணம் படிக்கப்படுகிறது... (Scanning document with OCR...)</p>";

  const formData = new FormData();
  formData.append('file', input.files[0]);

  try {
    const response = await fetch('/api/ocr-scan', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (data.status === "success" && data.extracted_data) {
      // Merge OCR extracted fields directly into the active profile
      currentProfile = { ...currentProfile, ...data.extracted_data };
      console.log("Dynamically Extracted Profile from Document:", currentProfile);

      // Display what was detected from the scan
      displayExtractedSummary(currentProfile);

      // Automatically evaluate schemes with real OCR data
      checkEligibility(currentProfile);
    } else {
      resultsContainer.innerHTML = "<p style='color:red;'>ஆவணத்தைப் பகுப்பாய்வு செய்ய முடியவில்லை.</p>";
    }
  } catch (err) {
    console.error("OCR upload error:", err);
    resultsContainer.innerHTML = "<p style='color:red;'>ஆவணம் பதிவேற்றுவதில் பிழை ஏற்பட்டது.</p>";
  }
}

// Helper: Show Extracted Parameters to User
function displayExtractedSummary(profile, spokenText = null) {
  const summaryBox = document.createElement('div');
  summaryBox.style.cssText = "background:#e2f0d9; border:1px solid #c5e1a5; padding:10px; border-radius:6px; margin:10px 0; font-size:13px; text-align:left;";
  
  let content = "<b>✅ கண்டறியப்பட்ட தகவல்கள் (Detected Data):</b><br>";
  if (spokenText) content += `<i>குரல்: "${spokenText}"</i><br>`;
  if (profile.gender) content += `• பாலினம் (Gender): <b>${profile.gender}</b><br>`;
  if (profile.age) content += `• வயது (Age): <b>${profile.age}</b><br>`;
  if (profile.annual_income) content += `• ஆண்டு வருமானம் (Income): <b>₹${profile.annual_income.toLocaleString()}</b><br>`;
  if (profile.ration_card_type) content += `• அட்டை வகை (Ration Card): <b>${profile.ration_card_type}</b><br>`;
  if (profile.is_govt_school_studied) content += `• அரசுப் பள்ளி படிப்பு: <b>ஆம் (Yes)</b><br>`;
  if (profile.is_agricultural_laborer) content += `• தொழில்: <b>விவசாயி (Farmer)</b><br>`;

  summaryBox.innerHTML = content;
  
  const resultsContainer = document.getElementById('results');
  resultsContainer.prepend(summaryBox);
}

// Variable to store all fetched schemes in memory
let allSchemesList = [];

// Fetch all schemes from the backend
async function fetchAllSchemes() {
  const resultsContainer = document.getElementById('results');
  resultsContainer.innerHTML = "<p>⏳ அனைத்து திட்டங்களும் ஏற்றப்படுகின்றன... (Loading schemes catalog...)</p>";

  try {
    const response = await fetch('/api/all-schemes');
    const data = await response.json();

    if (data.status === "success" && data.schemes) {
      allSchemesList = data.schemes;
      renderSchemesCatalog(allSchemesList);
    } else {
      resultsContainer.innerHTML = "<p style='color:red;'>திட்டங்களைப் பெற முடியவில்லை.</p>";
    }
  } catch (err) {
    console.error("Error fetching all schemes:", err);
    resultsContainer.innerHTML = "<p style='color:red;'>சேவையகத்தை இணைப்பதில் பிழை ஏற்பட்டது.</p>";
  }
}

// Render the scheme cards with a search box
function renderSchemesCatalog(schemes) {
  const resultsContainer = document.getElementById('results');

  let html = `
    <div style="background:#ffffff; padding:15px; border-radius:10px; margin-top:15px; border:1px solid #e0e6ed;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h3 style="color:#0056b3; font-size:17px; margin:0;">📚 அனைத்து திட்டங்கள் (${schemes.length})</h3>
      </div>
      
      <!-- Live Search Box -->
      <input type="text" id="schemeSearchBox" placeholder="🔍 திட்டங்களைத் தேடவும் (எ.கா. மாணவர், விவசாயி, மகளிர்)..." 
             onkeyup="filterSchemesList()" 
             style="width:100%; padding:10px; border:1px solid #008CBA; border-radius:6px; font-size:14px; margin-bottom:12px; box-sizing:border-box;">
      
      <div id="schemesCardsContainer">
  `;

  schemes.forEach(s => {
    const stipendBadge = s.monthly_stipend > 0 
      ? `<span style="background:#28a745; color:white; padding:3px 8px; border-radius:4px; font-size:12px; font-weight:bold;">மாதம் ₹${s.monthly_stipend}</span>` 
      : `<span style="background:#17a2b8; color:white; padding:3px 8px; border-radius:4px; font-size:12px;">மானியம் / காப்பீடு</span>`;
    
    const docs = s.required_documents || [];

    html += `
      <div class="card" style="background:#f8faff; border-left:5px solid #0056b3; padding:14px; margin-bottom:12px; border-radius:8px; text-align:left; box-shadow:0 1px 4px rgba(0,0,0,0.05);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <h4 style="color:#0056b3; margin:0 0 3px 0; font-size:16px;">${s.scheme_name_ta}</h4>
            <span style="font-size:12px; color:#6c757d;">${s.scheme_name_en}</span>
          </div>
          ${stipendBadge}
        </div>
        <p style="font-size:13px; color:#333; margin:8px 0 6px 0;">${s.description_ta}</p>
        <small style="color:#666; display:block; font-size:12px;"><b>📄 தேவையான ஆவணங்கள்:</b> ${docs.join(', ')}</small>
      </div>
    `;
  });

  html += `</div></div>`;
  resultsContainer.innerHTML = html;
}

// Live Search Filter Function
function filterSchemesList() {
  const query = document.getElementById('schemeSearchBox').value.toLowerCase();
  const filtered = allSchemesList.filter(s => 
    s.scheme_name_ta.toLowerCase().includes(query) ||
    s.scheme_name_en.toLowerCase().includes(query) ||
    s.description_ta.toLowerCase().includes(query)
  );

  const container = document.getElementById('schemesCardsContainer');
  if (filtered.length === 0) {
    container.innerHTML = "<p style='color:#888; text-align:center; padding:15px;'>பொருத்தமான திட்டங்கள் எதுவும் இல்லை.</p>";
    return;
  }

  let html = "";
  filtered.forEach(s => {
    const stipendBadge = s.monthly_stipend > 0 
      ? `<span style="background:#28a745; color:white; padding:3px 8px; border-radius:4px; font-size:12px;">மாதம் ₹${s.monthly_stipend}</span>` 
      : `<span style="background:#17a2b8; color:white; padding:3px 8px; border-radius:4px; font-size:12px;">மானியம் / காப்பீடு</span>`;
    
    html += `
      <div class="card" style="background:#f8faff; border-left:5px solid #0056b3; padding:14px; margin-bottom:12px; border-radius:8px; text-align:left;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <h4 style="color:#0056b3; margin:0 0 3px 0; font-size:16px;">${s.scheme_name_ta}</h4>
            <span style="font-size:12px; color:#6c757d;">${s.scheme_name_en}</span>
          </div>
          ${stipendBadge}
        </div>
        <p style="font-size:13px; color:#333; margin:8px 0 6px 0;">${s.description_ta}</p>
        <small style="color:#666;"><b>📄 தேவையான ஆவணங்கள்:</b> ${(s.required_documents || []).join(', ')}</small>
      </div>
    `;
  });
  container.innerHTML = html;
}

// Function: Locate nearest e-Sevai centers using citizen's GPS location
function findNearestEsevai() {
  if (!navigator.geolocation) {
    // Fallback if GPS is not available
    window.open("https://www.google.com/maps/search/e-Sevai+Maiyam+near+me", "_blank");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      // Opens Google Maps centered on the user's exact coordinates
      const mapsUrl = `https://www.google.com/maps/search/e+Sevai+Maiyam/@${lat},${lon},14z`;
      window.open(mapsUrl, "_blank");
    },
    (error) => {
      console.warn("GPS permission denied. Opening general search.");
      window.open("https://www.google.com/maps/search/e-Sevai+Maiyam+near+me", "_blank");
    }
  );
}