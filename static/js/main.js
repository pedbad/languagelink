(function () {
    document.addEventListener("DOMContentLoaded", function () {
        console.log('==== DOM loaded - JS called ====');

        // Hamburger menu toggle
        document.getElementById('hamburger').addEventListener('click', function () {
            var menu = document.getElementById('mobileMenu');
            menu.classList.toggle('hidden');
        });

        // Update file name for file input
        const fileInput = document.getElementById('id_profile_picture');
        const fileNameDisplay = document.getElementById('file-name');
        const avatarPreview = document.getElementById('profile-picture-preview'); // Corrected selector

        if (fileInput) {
            fileInput.addEventListener('change', function () {
                if (fileInput.files && fileInput.files.length > 0) {
                    // Update file name
                    fileNameDisplay.textContent = fileInput.files[0].name;

                    // Update avatar preview
                    const file = fileInput.files[0];
                    const objectUrl = URL.createObjectURL(file);

                    if (avatarPreview) {
                        avatarPreview.src = objectUrl;

                        // Revoke the object URL after the image is loaded
                        avatarPreview.onload = function () {
                            URL.revokeObjectURL(objectUrl);
                        };
                    }
                } else {
                    fileNameDisplay.textContent = 'No file chosen';

                    // Reset avatar preview to default if no file is selected
                    if (avatarPreview) {
                        avatarPreview.src = avatarPreview.dataset.defaultSrc;
                    }
                }
            });
        }
    });
})();
