// Dark Mode Toggle
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the theme on page load
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
    
    // Create toggle button if it doesn't exist
    createThemeToggle();
});

function createThemeToggle() {
    // Check if toggle already exists
    if (document.getElementById('theme-toggle')) return;
    
    // Create toggle button
    const toggle = document.createElement('button');
    toggle.id = 'theme-toggle';
    toggle.innerHTML = '🌙';
    toggle.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #9333ea;
        color: white;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        transition: all 0.3s ease;
    `;
    
    // Add hover effect
    toggle.onmouseenter = function() {
        this.style.transform = 'scale(1.1)';
    };
    
    toggle.onmouseleave = function() {
        this.style.transform = 'scale(1)';
    };
    
    // Add click handler
    toggle.onclick = toggleDarkMode;
    
    // Add to page
    document.body.appendChild(toggle);
    
    // Update icon based on current theme
    updateToggleIcon();
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    
    // Save preference
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Update icon
    updateToggleIcon();
}

function updateToggleIcon() {
    const toggle = document.getElementById('theme-toggle');
    if (!toggle) return;
    
    const isDark = document.body.classList.contains('dark-mode');
    toggle.innerHTML = isDark ? '☀️' : '🌙';
}

// Export functions for use in other scripts if needed
window.toggleDarkMode = toggleDarkMode;