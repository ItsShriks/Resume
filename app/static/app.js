document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // State
  let masterProfile = null;
  let currentResumePdfUrl = null;
  let currentCoverLetterPdfUrl = null;
  let activePreviewMode = 'resume'; // 'resume' or 'cover_letter'

  // DOM Elements
  const jdInput = document.getElementById('jdInput');
  const roleTitleInput = document.getElementById('roleTitleInput');
  const companyInput = document.getElementById('companyInput');
  const languageSelect = document.getElementById('languageSelect');
  const focusSelect = document.getElementById('focusSelect');

  const analyzeBtn = document.getElementById('analyzeBtn');
  const tailorResumeBtn = document.getElementById('tailorResumeBtn');
  const generateCoverLetterBtn = document.getElementById('generateCoverLetterBtn');
  const loadSampleJDBtn = document.getElementById('loadSampleJDBtn');

  const scoreDialProgress = document.getElementById('scoreDialProgress');
  const scoreValue = document.getElementById('scoreValue');
  const analysisJobTitle = document.getElementById('analysisJobTitle');
  const analysisCompanyBadge = document.getElementById('analysisCompanyBadge');
  const analysisSummary = document.getElementById('analysisSummary');
  const matchingStrengthsTags = document.getElementById('matchingStrengthsTags');
  const requiredKeywordsTags = document.getElementById('requiredKeywordsTags');
  const actionableTipsList = document.getElementById('actionableTipsList');

  const sectionSummaryTex = document.getElementById('sectionSummaryTex');
  const sectionExperienceTex = document.getElementById('sectionExperienceTex');
  const sectionProjectsTex = document.getElementById('sectionProjectsTex');
  const sectionSkillsTex = document.getElementById('sectionSkillsTex');
  const coverLetterTex = document.getElementById('coverLetterTex');

  const recompileResumeBtn = document.getElementById('recompileResumeBtn');
  const recompileCoverLetterBtn = document.getElementById('recompileCoverLetterBtn');

  const pdfFrame = document.getElementById('pdfFrame');
  const pdfPlaceholder = document.getElementById('pdfPlaceholder');
  const pdfLoadingSpinner = document.getElementById('pdfLoadingSpinner');
  const spinnerText = document.getElementById('spinnerText');

  const viewResumePdfBtn = document.getElementById('viewResumePdfBtn');
  const viewCoverLetterPdfBtn = document.getElementById('viewCoverLetterPdfBtn');
  const downloadPdfBtn = document.getElementById('downloadPdfBtn');

  const statusDot = document.getElementById('statusDot');
  const statusMessage = document.getElementById('statusMessage');

  // Settings & Candidate Profile Elements
  const settingsBtn = document.getElementById('settingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const closeSettingsBtn = document.getElementById('closeSettingsBtn');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const modelSelect = document.getElementById('modelSelect');

  const candidateNameInput = document.getElementById('candidateNameInput');
  const candidateTitleInput = document.getElementById('candidateTitleInput');
  const candidateLocationInput = document.getElementById('candidateLocationInput');
  const candidateEmailInput = document.getElementById('candidateEmailInput');
  const candidatePillText = document.querySelector('.candidate-pill span:last-child');

  // Theme Toggle
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');

  // --- Load Settings from LocalStorage ---
  apiKeyInput.value = localStorage.getItem('GEMINI_API_KEY') || '';
  let savedModel = localStorage.getItem('GEMINI_MODEL');
  if (!savedModel || savedModel === 'gemini-2.5-flash') {
    savedModel = 'gemini-3.6-flash';
    localStorage.setItem('GEMINI_MODEL', savedModel);
  }
  modelSelect.value = savedModel;

  // Load Custom Candidate Profile if saved
  candidateNameInput.value = localStorage.getItem('CANDIDATE_NAME') || '';
  candidateTitleInput.value = localStorage.getItem('CANDIDATE_TITLE') || '';
  candidateLocationInput.value = localStorage.getItem('CANDIDATE_LOCATION') || '';
  candidateEmailInput.value = localStorage.getItem('CANDIDATE_EMAIL') || '';

  function updateCandidateDisplay() {
    const customName = candidateNameInput.value.trim();
    if (candidatePillText) {
      candidatePillText.textContent = customName || (masterProfile ? masterProfile.name : 'Candidate');
    }
  }

  function getApiKey() {
    return localStorage.getItem('GEMINI_API_KEY') || apiKeyInput.value.trim() || undefined;
  }

  function getModel() {
    return localStorage.getItem('GEMINI_MODEL') || modelSelect.value || 'gemini-3.6-flash';
  }

  function getCandidateData() {
    return {
      candidate_name: candidateNameInput.value.trim() || (masterProfile ? masterProfile.name : undefined),
      candidate_title: candidateTitleInput.value.trim() || (masterProfile ? masterProfile.title : undefined),
      candidate_location: candidateLocationInput.value.trim() || (masterProfile ? masterProfile.location : undefined),
      candidate_email: candidateEmailInput.value.trim() || (masterProfile ? masterProfile.email : undefined),
    };
  }

  // --- Status Helper ---
  function setStatus(message, state = 'ready') {
    statusMessage.textContent = message;
    statusDot.className = `dot ${state}`;
  }

  function showSpinner(text = 'Processing...') {
    spinnerText.textContent = text;
    pdfLoadingSpinner.style.display = 'flex';
  }

  function hideSpinner() {
    pdfLoadingSpinner.style.display = 'none';
  }

  // --- Load Master Profile on Init ---
  async function fetchMasterProfile() {
    try {
      setStatus('Loading Master Profile...', 'busy');
      const res = await fetch('/api/master-profile');
      const data = await res.json();
      if (data.status === 'success') {
        masterProfile = data.profile;
        if (!candidateNameInput.value) candidateNameInput.value = masterProfile.name || '';
        if (!candidateTitleInput.value) candidateTitleInput.value = masterProfile.title || '';
        if (!candidateLocationInput.value) candidateLocationInput.value = masterProfile.location || '';
        if (!candidateEmailInput.value) candidateEmailInput.value = masterProfile.email || '';

        updateCandidateDisplay();

        const sections = masterProfile.sections || {};
        sectionSummaryTex.value = sections.personal_info || '';
        sectionExperienceTex.value = sections.work_experience || '';
        sectionProjectsTex.value = sections.projects || '';
        sectionSkillsTex.value = sections.skills || '';
        coverLetterTex.value = masterProfile.cover_letter_tex || '';
        setStatus('Master Profile Ready', 'ready');
      }
    } catch (err) {
      console.error('Error fetching master profile:', err);
      setStatus('Failed to load master profile', 'error');
    }
  }

  fetchMasterProfile();

  // --- Diverse Multi-Domain Sample JDs ---
  const SAMPLE_JDS = [
    {
      title: "Senior Full Stack Software Engineer",
      company: "Stripe / CloudScale Labs",
      domain: "Software Engineering & Cloud",
      text: `Role: Senior Full Stack Software Engineer
Company: CloudScale Labs
Location: Remote / Berlin, Germany

About the Role:
We are seeking an experienced Full Stack Engineer to architect high-throughput web applications, design RESTful/GraphQL APIs, and scale cloud infrastructure.

Key Responsibilities:
- Build robust microservices and backend APIs in Python, Node.js, or Go.
- Develop interactive, accessible web frontends using React, TypeScript, and modern design systems.
- Containerize services with Docker and manage deployment pipelines on AWS / Kubernetes.
- Optimize database performance (PostgreSQL, Redis), monitoring telemetry, and automated testing.
- Collaborate in an agile Scrum team to deliver production-grade software with 99.9% uptime.

Requirements:
- Degree in Computer Science, Software Engineering, or equivalent practical experience.
- Strong software development experience in Python, TypeScript/JavaScript, or C++.
- Hands-on experience with Docker, CI/CD, Git, and Linux systems.
- Fluency in English.`
    },
    {
      title: "Data Scientist & AI Specialist",
      company: "DeepMind / Applied AI Solutions",
      domain: "Data Science & AI/ML",
      text: `Role: Data Scientist & AI Specialist
Company: Applied AI Solutions
Location: Munich / Remote, Germany

About the Role:
Join our AI core team to build, evaluate, and deploy machine learning models and multimodal data pipelines for high-impact production applications.

Key Responsibilities:
- Design end-to-end data acquisition, cleaning, feature engineering, and annotation QA pipelines.
- Train and fine-tune deep learning models using PyTorch, TensorFlow, and CUDA acceleration.
- Conduct statistical evaluations, pairwise model comparisons, and root-cause error diagnostics.
- Develop RESTful API endpoints and Docker containers to deploy models into production.

Requirements:
- Degree in Computer Science, Data Science, Mathematics, or engineering discipline.
- Strong programming skills in Python, Pandas, NumPy, and PyTorch.
- Experience with data quality assurance, annotation workflows, and metric benchmarking.
- Excellent analytical and problem-solving skills.`
    },
    {
      title: "Technical Product & Project Manager",
      company: "InnovateTech Global",
      domain: "Product & Project Management",
      text: `Role: Technical Product Manager
Company: InnovateTech Global
Location: Frankfurt / Remote, Germany

About the Role:
We are looking for a Technical Product Manager to bridge engineering and business teams, define product roadmaps, and lead cross-functional product launches.

Key Responsibilities:
- Own the product lifecycle from requirement discovery to release and iterative optimization.
- Lead Scrum/Agile ceremonies (sprint planning, backlog grooming, retrospectives).
- Translate complex technical requirements into user stories, PRDs, and acceptance criteria.
- Monitor KPIs, user engagement metrics, and system stability with engineering teams.

Requirements:
- Background in Tech, Engineering, or Business Informatics.
- Proven experience managing software/hardware products and technical teams.
- Strong stakeholder management and communication skills in English and German.`
    },
    {
      title: "Robotics Software & Perception Engineer",
      company: "Autonomous Mobility AI Labs",
      domain: "Robotics & Autonomous Systems",
      text: `Role: Robotics Software & Perception Engineer
Company: Autonomous Mobility AI Labs
Location: Munich / Bonn, Germany

About the Role:
We are seeking a Robotics Engineer with expertise in ROS 2, C++17, Python, and Multi-Sensor Perception (LiDAR, Camera, IMU) to develop autonomous navigation and 3D perception pipelines.

Key Responsibilities:
- Design, integrate, and benchmark autonomous robot navigation stacks using ROS 2 and Nav2.
- Develop real-time 3D point cloud segmentation and object detection algorithms using PyTorch and CUDA.
- Curate, label, and validate multi-sensor robotic datasets ensuring sensor calibration.
- Conduct root-cause analysis on system logs, rosbags, and edge-case anomalies.

Requirements:
- Degree in Robotics, Autonomous Systems, Mechatronics, or Computer Science.
- Hands-on experience with ROS/ROS 2, Nav2, SLAM, and sensor fusion.
- Strong proficiency in Python and Modern C++ (C++17).`
    }
  ];

  let sampleIndex = 0;
  loadSampleJDBtn.addEventListener('click', () => {
    const sample = SAMPLE_JDS[sampleIndex % SAMPLE_JDS.length];
    sampleIndex++;

    jdInput.value = sample.text;
    roleTitleInput.value = sample.title;
    companyInput.value = sample.company;
    focusSelect.value = sample.domain;
    setStatus(`Sample Loaded: ${sample.title}`, 'ready');
  });

  // --- ATS Score Dial Animation ---
  function updateScoreDial(score) {
    const clampedScore = Math.max(0, Math.min(100, score));
    scoreValue.textContent = clampedScore;

    const circumference = 2 * Math.PI * 42;
    const offset = circumference - (clampedScore / 100) * circumference;
    scoreDialProgress.style.strokeDashoffset = offset;

    if (clampedScore >= 80) {
      scoreDialProgress.style.stroke = 'var(--color-success)';
    } else if (clampedScore >= 60) {
      scoreDialProgress.style.stroke = 'var(--color-warning)';
    } else {
      scoreDialProgress.style.stroke = 'var(--color-danger)';
    }
  }

  // --- 1. Analyze Job Spec ---
  analyzeBtn.addEventListener('click', async () => {
    const jdText = jdInput.value.trim();
    if (!jdText) {
      alert('Please paste a Job Description first.');
      return;
    }

    try {
      setStatus('Analyzing Job Spec with Gemini AI...', 'busy');
      showSpinner('Analyzing ATS Fit & Keywords...');

      const candidateData = getCandidateData();

      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jd_text: jdText,
          candidate_name: candidateData.candidate_name,
          candidate_title: candidateData.candidate_title,
          api_key: getApiKey(),
          model: getModel()
        })
      });

      const data = await res.json();
      hideSpinner();

      if (!res.ok || data.status !== 'success') {
        throw new Error(data.detail || 'Analysis failed');
      }

      const a = data.analysis;
      updateScoreDial(a.match_score || 85);
      analysisJobTitle.textContent = a.job_title || roleTitleInput.value || 'Target Role';
      analysisCompanyBadge.textContent = a.company_name || companyInput.value || 'Company';
      analysisSummary.textContent = a.match_summary || '';

      if (a.job_title && !roleTitleInput.value) roleTitleInput.value = a.job_title;
      if (a.company_name && !companyInput.value) companyInput.value = a.company_name;

      // Render Matching Strengths
      matchingStrengthsTags.innerHTML = '';
      (a.matching_strengths || []).forEach(s => {
        const tag = document.createElement('span');
        tag.className = 'tag tag-success';
        tag.textContent = s;
        matchingStrengthsTags.appendChild(tag);
      });

      // Render Required Keywords
      requiredKeywordsTags.innerHTML = '';
      (a.required_keywords || []).forEach(k => {
        const tag = document.createElement('span');
        tag.className = 'tag tag-warning';
        tag.textContent = k;
        requiredKeywordsTags.appendChild(tag);
      });

      // Render Actionable Tips
      actionableTipsList.innerHTML = '';
      (a.actionable_tips || []).forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        actionableTipsList.appendChild(li);
      });

      // Switch to analysis tab
      switchTab('analysisTab');
      switchMobilePanel('center');
      setStatus('Analysis Complete', 'ready');
      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      hideSpinner();
      console.error(err);
      alert(`Analysis Error: ${err.message}`);
      setStatus('Analysis failed', 'error');
    }
  });

  // --- 2. Tailor Resume & Compile PDF ---
  tailorResumeBtn.addEventListener('click', async () => {
    const jdText = jdInput.value.trim();
    if (!jdText) {
      alert('Please paste a Job Description first.');
      return;
    }

    try {
      setStatus('Tailoring Resume & Compiling LaTeX...', 'busy');
      showSpinner('Generating tailored LaTeX & Compiling PDF...');

      const candidateData = getCandidateData();

      const res = await fetch('/api/tailor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jd_text: jdText,
          target_role: roleTitleInput.value.trim(),
          language: languageSelect.value,
          focus_area: focusSelect.value,
          candidate_name: candidateData.candidate_name,
          candidate_title: candidateData.candidate_title,
          candidate_location: candidateData.candidate_location,
          candidate_email: candidateData.candidate_email,
          api_key: getApiKey(),
          model: getModel()
        })
      });

      const data = await res.json();
      hideSpinner();

      if (!res.ok || data.status !== 'success') {
        throw new Error(data.detail || 'Tailoring failed');
      }

      // Populate Editor Textareas
      if (data.updated_sections) {
        sectionSummaryTex.value = data.updated_sections.personal_info || '';
        sectionExperienceTex.value = data.updated_sections.work_experience || '';
        sectionProjectsTex.value = data.updated_sections.projects || '';
        sectionSkillsTex.value = data.updated_sections.skills || '';
      }

      // Render PDF preview
      if (data.pdf_base64) {
        setPdfPreview(data.pdf_base64, 'resume');
      }

      switchTab('resumeEditorTab');
      switchMobilePanel('right');
      setStatus('Resume Tailored & Compiled Successfully', 'ready');
    } catch (err) {
      hideSpinner();
      console.error(err);
      alert(`Tailoring Error: ${err.message}`);
      setStatus('Tailoring failed', 'error');
    }
  });

  // --- 3. Generate Cover Letter ---
  generateCoverLetterBtn.addEventListener('click', async () => {
    const jdText = jdInput.value.trim();
    if (!jdText) {
      alert('Please paste a Job Description first.');
      return;
    }

    try {
      setStatus('Generating Cover Letter & Compiling...', 'busy');
      showSpinner('Drafting Cover Letter & Building PDF...');

      const candidateData = getCandidateData();

      const res = await fetch('/api/cover-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jd_text: jdText,
          company_name: companyInput.value.trim(),
          role_title: roleTitleInput.value.trim(),
          language: languageSelect.value,
          candidate_name: candidateData.candidate_name,
          candidate_location: candidateData.candidate_location,
          candidate_email: candidateData.candidate_email,
          api_key: getApiKey(),
          model: getModel()
        })
      });

      const data = await res.json();
      hideSpinner();

      if (!res.ok || data.status !== 'success') {
        throw new Error(data.detail || 'Cover letter generation failed');
      }

      if (data.cover_letter_data && data.cover_letter_data.cover_letter_tex) {
        coverLetterTex.value = data.cover_letter_data.cover_letter_tex;
      }

      if (data.pdf_base64) {
        setPdfPreview(data.pdf_base64, 'cover_letter');
      }

      switchTab('coverLetterEditorTab');
      switchMobilePanel('right');
      setStatus('Cover Letter Generated & Compiled Successfully', 'ready');
    } catch (err) {
      hideSpinner();
      console.error(err);
      alert(`Cover Letter Error: ${err.message}`);
      setStatus('Cover letter failed', 'error');
    }
  });

  // --- Recompile Resume from Edited Code ---
  recompileResumeBtn.addEventListener('click', async () => {
    try {
      setStatus('Recompiling Resume LaTeX...', 'busy');
      showSpinner('Compiling Custom LaTeX...');

      const updatedSections = {
        personal_info: sectionSummaryTex.value,
        work_experience: sectionExperienceTex.value,
        projects: sectionProjectsTex.value,
        skills: sectionSkillsTex.value
      };

      const res = await fetch('/api/compile-resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sections: updatedSections
        })
      });

      const data = await res.json();
      hideSpinner();

      if (!res.ok || !data.compile_success) {
        throw new Error(data.compile_logs || 'LaTeX Compilation Failed');
      }

      if (data.pdf_base64) {
        setPdfPreview(data.pdf_base64, 'resume');
      }
      setStatus('Resume Recompiled Successfully', 'ready');
    } catch (err) {
      hideSpinner();
      console.error(err);
      alert(`Compilation Error:\n${err.message}`);
      setStatus('Compilation failed', 'error');
    }
  });

  // --- Recompile Cover Letter from Edited Code ---
  recompileCoverLetterBtn.addEventListener('click', async () => {
    try {
      setStatus('Recompiling Cover Letter LaTeX...', 'busy');
      showSpinner('Compiling Custom Cover Letter...');

      const res = await fetch('/api/compile-cover-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cover_letter_tex: coverLetterTex.value
        })
      });

      const data = await res.json();
      hideSpinner();

      if (!res.ok || !data.compile_success) {
        throw new Error(data.compile_logs || 'LaTeX Compilation Failed');
      }

      if (data.pdf_base64) {
        setPdfPreview(data.pdf_base64, 'cover_letter');
      }
      setStatus('Cover Letter Recompiled Successfully', 'ready');
    } catch (err) {
      hideSpinner();
      console.error(err);
      alert(`Compilation Error:\n${err.message}`);
      setStatus('Compilation failed', 'error');
    }
  });

  // --- PDF Preview Helper ---
  function setPdfPreview(base64Data, mode = 'resume') {
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);

    if (mode === 'resume') {
      currentResumePdfUrl = url;
    } else {
      currentCoverLetterPdfUrl = url;
    }

    activePreviewMode = mode;
    updatePreviewButtons();
    pdfFrame.src = url;
    pdfPlaceholder.style.display = 'none';
  }

  function updatePreviewButtons() {
    if (activePreviewMode === 'resume') {
      viewResumePdfBtn.className = 'btn btn-xs btn-primary';
      viewCoverLetterPdfBtn.className = 'btn btn-xs btn-ghost';
      if (currentResumePdfUrl) {
        pdfFrame.src = currentResumePdfUrl;
        pdfPlaceholder.style.display = 'none';
      }
    } else {
      viewResumePdfBtn.className = 'btn btn-xs btn-ghost';
      viewCoverLetterPdfBtn.className = 'btn btn-xs btn-primary';
      if (currentCoverLetterPdfUrl) {
        pdfFrame.src = currentCoverLetterPdfUrl;
        pdfPlaceholder.style.display = 'none';
      }
    }
  }

  viewResumePdfBtn.addEventListener('click', () => {
    activePreviewMode = 'resume';
    updatePreviewButtons();
  });

  viewCoverLetterPdfBtn.addEventListener('click', () => {
    activePreviewMode = 'cover_letter';
    updatePreviewButtons();
  });

  // --- Download PDF ---
  downloadPdfBtn.addEventListener('click', () => {
    if (activePreviewMode === 'resume') {
      window.location.href = '/api/download/resume.pdf';
    } else {
      window.location.href = '/api/download/cover-letter.pdf';
    }
  });

  // --- Tab Navigation ---
  function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.tab === tabId);
    });
    document.querySelectorAll('.tab-pane').forEach(p => {
      p.classList.toggle('active', p.id === tabId);
    });
  }

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // --- Accordions in Section Editor ---
  document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
      const content = header.nextElementSibling;
      const isOpen = content.style.display !== 'none';
      content.style.display = isOpen ? 'none' : 'block';
      const icon = header.querySelector('[data-lucide]');
      if (icon) {
        icon.style.transform = isOpen ? 'rotate(-90deg)' : 'rotate(0deg)';
      }
    });
  });

  // --- Settings Modal ---
  settingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'flex';
  });

  closeSettingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'none';
  });

  saveSettingsBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    const model = modelSelect.value;
    if (key) {
      localStorage.setItem('GEMINI_API_KEY', key);
    } else {
      localStorage.removeItem('GEMINI_API_KEY');
    }
    localStorage.setItem('GEMINI_MODEL', model);

    // Save candidate profile overrides
    const cName = candidateNameInput.value.trim();
    const cTitle = candidateTitleInput.value.trim();
    const cLoc = candidateLocationInput.value.trim();
    const cEmail = candidateEmailInput.value.trim();

    if (cName) localStorage.setItem('CANDIDATE_NAME', cName); else localStorage.removeItem('CANDIDATE_NAME');
    if (cTitle) localStorage.setItem('CANDIDATE_TITLE', cTitle); else localStorage.removeItem('CANDIDATE_TITLE');
    if (cLoc) localStorage.setItem('CANDIDATE_LOCATION', cLoc); else localStorage.removeItem('CANDIDATE_LOCATION');
    if (cEmail) localStorage.setItem('CANDIDATE_EMAIL', cEmail); else localStorage.removeItem('CANDIDATE_EMAIL');

    updateCandidateDisplay();
    settingsModal.style.display = 'none';
    setStatus('Settings & Profile saved', 'ready');
  });

  // --- Mobile Panel Navigation ---
  const panelLeft = document.querySelector('.panel-left');
  const panelCenter = document.querySelector('.panel-center');
  const panelRight = document.querySelector('.panel-right');
  const mobileTabBtns = document.querySelectorAll('.mobile-tab-btn');

  function switchMobilePanel(panelName) {
    if (panelLeft) panelLeft.classList.toggle('mobile-active', panelName === 'left');
    if (panelCenter) panelCenter.classList.toggle('mobile-active', panelName === 'center');
    if (panelRight) panelRight.classList.toggle('mobile-active', panelName === 'right');

    mobileTabBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.mobilePanel === panelName);
    });
  }

  // Initialize mobile active panel
  switchMobilePanel('left');

  mobileTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      switchMobilePanel(btn.dataset.mobilePanel);
    });
  });

  // --- Theme Toggle ---
  themeToggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
    const isLight = document.body.classList.contains('light-theme');
    themeIcon.setAttribute('data-lucide', isLight ? 'moon' : 'sun');
    if (window.lucide) window.lucide.createIcons();
  });
});
