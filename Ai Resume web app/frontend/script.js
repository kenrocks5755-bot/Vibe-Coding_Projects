const API_BASE = "";

// Navigation
const navAnalyze = document.getElementById('nav-analyze');
const navBuild = document.getElementById('nav-build');
const sectionAnalyze = document.getElementById('section-analyze');
const sectionBuild = document.getElementById('section-build');
const loading = document.getElementById('loading');

navAnalyze.addEventListener('click', () => {
    console.log("Switching to Analyze");
    navAnalyze.classList.add('active');
    navBuild.classList.remove('active');
    sectionAnalyze.classList.add('active');
    sectionAnalyze.style.display = 'flex'; // Explicit display set
    sectionBuild.classList.remove('active');
    sectionBuild.style.display = 'none';
});

navBuild.addEventListener('click', () => {
    console.log("Switching to Build");
    navBuild.classList.add('active');
    navAnalyze.classList.remove('active');
    sectionBuild.classList.add('active');
    sectionBuild.style.display = 'flex'; // Explicit display set
    sectionAnalyze.classList.remove('active');
    sectionAnalyze.style.display = 'none';
});

// File Upload Logic
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const analyzeResult = document.getElementById('analyze-result');

uploadBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        loading.style.display = 'flex';
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                displayAnalysis(data);
            } else {
                alert('Analysis failed. Is Ollama running?');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during analysis.');
        } finally {
            loading.style.display = 'none';
        }
    }
});

function displayAnalysis(data) {
    analyzeResult.style.display = 'block';
    analyzeResult.innerHTML = `
        <h2 style="margin-bottom: 20px;">Analysis Report</h2>
        <div style="font-size: 2.5rem; font-weight: 800; color: var(--primary-purple); margin-bottom: 20px;">Score: ${data.score}/10</div>
        <div style="margin-bottom: 20px;">
            <p><strong>Strengths:</strong> ${data.strengths}</p>
        </div>
        <div style="margin-bottom: 20px;">
            <p><strong>Weaknesses:</strong> ${data.weaknesses}</p>
        </div>
        <div>
            <p><strong>Suggestions:</strong> ${data.suggestions}</p>
        </div>
    `;
}

// Build Logic
const generateBtn = document.getElementById('generate-btn');
const buildResult = document.getElementById('build-result');
const buildResultContainer = document.getElementById('build-result-container');
const downloadBtn = document.getElementById('download-btn');
let currentResumeContent = '';

generateBtn.addEventListener('click', async () => {
    const payload = {
        name: document.getElementById('name').value,
        title: document.getElementById('job-title').value,
        contact: document.getElementById('contact').value,
        education: document.getElementById('education').value,
        skills: document.getElementById('skills').value,
        experience: document.getElementById('experience').value,
        projects: document.getElementById('projects').value
    };

    if (!payload.name) {
        alert('Please enter your name.');
        return;
    }

    loading.style.display = 'flex';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            currentResumeContent = data.resume_content;
            buildResult.innerText = currentResumeContent;
            buildResultContainer.style.display = 'block';
        } else {
            alert('AI resume generation failed. Is Ollama running?');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during generation.');
    } finally {
        loading.style.display = 'none';
    }
});

downloadBtn.addEventListener('click', async () => {
    if (!currentResumeContent) return;

    try {
        const response = await fetch('/download-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_content: currentResumeContent })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'resume.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            alert('PDF generation failed.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during PDF generation.');
    }
});
