(function () {
  document.addEventListener("DOMContentLoaded", function () {
    console.log('==== DOM loaded - JS called ====');

    // === Hamburger menu toggle ===
    const hamburger = document.getElementById('hamburger');
    if (hamburger) {
      hamburger.addEventListener('click', function () {
        const menu = document.getElementById('mobileMenu');
        if (menu) {
          menu.classList.toggle('hidden');
        }
      });
    }

    // === Role Selection Toggle ===
    const studentBtn = document.getElementById('student-btn');
    const teacherBtn = document.getElementById('teacher-btn');
    const roleInput = document.getElementById('role');

    if (studentBtn && teacherBtn && roleInput) {
      function selectRole(role) {
        if (role === 'student') {
          studentBtn.classList.add('bg-deep-teal', 'text-white', 'ring-deep-teal');
          studentBtn.classList.remove('bg-white', 'text-gray-900', 'ring-gray-300', 'hover:bg-teal-600');
          teacherBtn.classList.add('bg-white', 'text-gray-900', 'ring-gray-300', 'hover:bg-teal-600');
          teacherBtn.classList.remove('bg-deep-teal', 'text-white', 'ring-deep-teal');
        } else if (role === 'teacher') {
          teacherBtn.classList.add('bg-deep-teal', 'text-white', 'ring-deep-teal');
          teacherBtn.classList.remove('bg-white', 'text-gray-900', 'ring-gray-300', 'hover:bg-teal-600');
          studentBtn.classList.add('bg-white', 'text-gray-900', 'ring-gray-300', 'hover:bg-teal-600');
          studentBtn.classList.remove('bg-deep-teal', 'text-white', 'ring-deep-teal');
        }
        roleInput.value = role;
      }

      // Auto-select role based on URL parameter
      const urlParams = new URLSearchParams(window.location.search);
      const selectedRole = urlParams.get("role") || "student"; // Default to student
      selectRole(selectedRole);

      // Add click event listeners for manual selection
      studentBtn.addEventListener('click', () => selectRole('student'));
      teacherBtn.addEventListener('click', () => selectRole('teacher'));
    }

    // === Update file name and avatar preview for file input ===
    const fileInput = document.getElementById('id_profile_picture');
    const fileNameDisplay = document.getElementById('file-name');
    const avatarPreview = document.getElementById('profile-picture-preview');

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

    // === Search input "X" clear functionality ===
    const searchInput = document.getElementById('search-input');
    const searchForm = document.getElementById('search-form');

    if (searchInput && searchForm) {
      searchInput.addEventListener('input', function () {
        if (this.value === '') {
          searchForm.submit();
        }
      });
    }

    // === Delete Student Modal Functionality ===
    const openModalButton = document.getElementById('open-delete-modal'); // Button to open modal
    const closeModalButton = document.getElementById('close-delete-modal'); // Close button in modal
    const cancelModalButton = document.getElementById('cancel-delete-modal'); // Cancel button in modal
    const modal = document.getElementById('delete-modal'); // Modal container
    const modalBackdrop = modal; // Backdrop is the modal itself

    if (openModalButton && modal) {
      // Open modal event
      openModalButton.addEventListener('click', function (e) {
        e.preventDefault();
        modal.classList.remove('hidden');
      });

      // Function to close modal
      function closeModal() {
        modal.classList.add('hidden');
      }

      // Close modal on button clicks
      if (closeModalButton) closeModalButton.addEventListener('click', closeModal);
      if (cancelModalButton) cancelModalButton.addEventListener('click', closeModal);

      // Close modal when clicking on the backdrop
      modalBackdrop.addEventListener('click', function (e) {
        if (e.target === modalBackdrop) {
          closeModal();
        }
      });
    }

    // === Hide Email Error on Input ===
    const emailInput = document.getElementById('email');
    const emailError = document.getElementById('email-error');

    if (emailInput && emailError) {
      emailInput.addEventListener('input', function () {
        // Hide the error message when the input is modified or cleared
        if (this.value.trim() === '' || emailError.textContent) {
          emailError.style.display = 'none';
        }
      });
    }
  });
})();
