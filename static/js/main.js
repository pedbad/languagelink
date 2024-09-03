(function () {
    document.addEventListener("DOMContentLoaded", function () {
        console.log('==== DOM loaded - JS called ====');

        document.getElementById('hamburger').addEventListener('click', function () {
            var menu = document.getElementById('mobileMenu');
            menu.classList.toggle('hidden');
        });
    });
})();

