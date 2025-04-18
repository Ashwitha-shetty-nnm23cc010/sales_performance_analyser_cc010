// Function to show the dashboard options and sales data
function showDashboard() {
    // Hide the welcome section
    document.querySelector('.welcome-container').style.display = 'none';

    // Show the dashboard options
    document.querySelector('.actions').style.display = 'block';

    // Show the sales data
    document.querySelector('.sales-data').style.display = 'block';
}

// Optional: Add animations using GSAP (if GSAP is included in your project)
if (typeof gsap !== 'undefined') {
    gsap.from(".welcome-container img", { duration: 1, opacity: 0, y: -50 });
    gsap.from(".quote", { duration: 1.5, opacity: 0, delay: 0.5 });
    gsap.from(".proceed-button", { duration: 1, opacity: 0, scale: 0, delay: 1 });
}