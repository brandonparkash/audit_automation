document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('form');
    const btn = document.querySelector('.btn.primary');
    const originalText = btn.innerText;

    form.addEventListener('submit', function() {
        // 1. Disable the button so they can't double-click
        btn.disabled = true;
        btn.style.opacity = "0.7";
        btn.style.cursor = "wait";

        // 2. Change text to show activity
        btn.innerText = "Uploading Evidence... Please Wait";

        // Optional: You could add a spinner here if you wanted to get fancy
    });
});