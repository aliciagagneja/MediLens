// Smooth navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Add active class to nav links
document.querySelectorAll('.nav-links a').forEach(link => {
    if (link.href === window.location.href) {
        link.style.color = 'var(--primary)';
    }
});

// Enhance drag-and-drop for file input
const fileInput = document.getElementById('fileInput');
if (fileInput) {
    const dropArea = document.querySelector('.file-label');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        dropArea.style.borderColor = 'var(--primary)';
        dropArea.style.background = '#eff6ff';
    }
    
    function unhighlight(e) {
        dropArea.style.borderColor = 'var(--border)';
        dropArea.style.background = 'var(--light)';
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        
        const event = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(event);
    }
}

console.log('MediLens loaded successfully');
