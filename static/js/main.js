(function () {
    document.addEventListener("DOMContentLoaded", function () {
        console.log('==== DOM loaded - JS called ====');

        // Initialize the Ripple effect
        const Ripple = window.Ripple; // Ensure Ripple is available globally
        const initTE = window.initTE; // Ensure initTE is available globally
        initTE({ Ripple });

        document.getElementById('hamburger').addEventListener('click', function () {
            var menu = document.getElementById('mobileMenu');
            menu.classList.toggle('hidden');
        });
    });
})();

