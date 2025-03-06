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



    // === Toggle In-Person Hosting Availability Dynamically ===
    const inPersonCheckbox = document.getElementById('can_host_in_person');
    const inPersonLabel = document.getElementById('in-person-toggle-label');
    const inPersonStatusText = document.getElementById('in-person-status-text'); // Find the Current Status element

    if (inPersonCheckbox && inPersonLabel) {
      inPersonCheckbox.addEventListener('change', function () {
        if (this.checked) {
          inPersonLabel.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5 mr-2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path> <!-- ❌ X Icon (Disable) -->
            </svg>
            <span>Disable In-Person Meetings</span>
          `;
          inPersonLabel.classList.remove("bg-[#10454F]", "hover:bg-[#0d3a45]", "focus:ring-[#10454F]");
          inPersonLabel.classList.add("bg-[#B02907]", "hover:bg-[#992405]", "focus:ring-[#B02907]");

          // Update Current Status Text
          inPersonStatusText.textContent = "Available for in-person meetings";
          inPersonStatusText.classList.remove("text-[#B02907]");
          inPersonStatusText.classList.add("text-[#10454F]");
        } else {
          inPersonLabel.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5 mr-2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 12l5 5L19 7"></path> <!-- ✔ Checkmark Icon (Enable) -->
            </svg>
            <span>Enable In-Person Meetings</span>
          `;
          inPersonLabel.classList.remove("bg-[#B02907]", "hover:bg-[#992405]", "focus:ring-[#B02907]");
          inPersonLabel.classList.add("bg-[#10454F]", "hover:bg-[#0d3a45]", "focus:ring-[#10454F]");

          // Update Current Status Text
          inPersonStatusText.textContent = "Not available for in-person meetings";
          inPersonStatusText.classList.remove("text-[#10454F]");
          inPersonStatusText.classList.add("text-[#B02907]");
        }
      });
    }





    // === Toggle Online Hosting Availability Dynamically ===
    const onlineCheckbox = document.getElementById('can_host_online');
    const onlineLabel = document.getElementById('online-toggle-label');
    const onlineStatusText = document.getElementById('online-status-text'); // Find the Current Status element

    if (onlineCheckbox && onlineLabel) {
      onlineCheckbox.addEventListener('change', function () {
        if (this.checked) {
          onlineLabel.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5 mr-2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path> <!-- ❌ X Icon (Disable) -->
            </svg>
            <span>Disable Online Meetings</span>
          `;
          onlineLabel.classList.remove("bg-[#10454F]", "hover:bg-[#0d3a45]", "focus:ring-[#10454F]");
          onlineLabel.classList.add("bg-[#B02907]", "hover:bg-[#992405]", "focus:ring-[#B02907]");

          // Update Current Status Text
          onlineStatusText.textContent = "Available for online meetings";
          onlineStatusText.classList.remove("text-[#B02907]");
          onlineStatusText.classList.add("text-[#10454F]");
        } else {
          onlineLabel.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5 mr-2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 12l5 5L19 7"></path> <!-- ✔ Checkmark Icon (Enable) -->
            </svg>
            <span>Enable Online Meetings</span>
          `;
          onlineLabel.classList.remove("bg-[#B02907]", "hover:bg-[#992405]", "focus:ring-[#B02907]");
          onlineLabel.classList.add("bg-[#10454F]", "hover:bg-[#0d3a45]", "focus:ring-[#10454F]");

          // Update Current Status Text
          onlineStatusText.textContent = "Not available for online meetings";
          onlineStatusText.classList.remove("text-[#10454F]");
          onlineStatusText.classList.add("text-[#B02907]");
        }
      });
    }



    // === Toggle Advising Status Dynamically ===
    const checkbox = document.getElementById('is_active_advisor');
    const label = document.getElementById('toggle-label');
    const statusText = document.getElementById('status-text'); // Find the Current Status element

    if (checkbox && label) {
      checkbox.addEventListener('change', function () {
        if (this.checked) {
          label.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5 mr-2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path> <!-- ❌ X Icon -->
            </svg>
            <span>Deactivate Advising</span>
          `;
          label.classList.remove("bg-[#10454F]", "hover:bg-[#0d3a45]", "focus:ring-[#10454F]");
          label.classList.add("bg-[#B02907]", "hover:bg-[#992405]", "focus:ring-[#B02907]");
 
          statusText.textContent = "Active";
          statusText.classList.remove("text-[#B02907]"); // Remove red color
          statusText.classList.add("text-[#10454F]"); // Add green color
        } else {
          label.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5 mr-2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 12l5 5L19 7"></path> <!-- ✔ Checkmark Icon -->
            </svg>
            <span>Activate Advising</span>
          `;
          label.classList.remove("bg-[#B02907]", "hover:bg-[#992405]", "focus:ring-[#B02907]");
          label.classList.add("bg-[#10454F]", "hover:bg-[#0d3a45]", "focus:ring-[#10454F]");

          statusText.textContent = "Inactive";
          statusText.classList.remove("text-[#10454F]"); // Remove green color
          statusText.classList.add("text-[#B02907]"); // Add red color
        }
      });
    }

    // === Toggle Availability Slots Dynamically ===
    const availabilityButtons = document.querySelectorAll('.toggle-slot');

    availabilityButtons.forEach(button => {
      button.addEventListener('click', async function () {
        const date = this.getAttribute('data-date');
        const startTime = this.getAttribute('data-start-time');
        const endTime = this.getAttribute('data-end-time');

        // Prevent toggling past dates
        if (new Date(date) < new Date().setHours(0, 0, 0, 0)) {
          return;
        }

        // ✅ Disable button during request to prevent spam clicking
        this.disabled = true;

        try {
          const response = await fetch('/booking/toggle-availability/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ 
              date: date, 
              start_time: startTime, 
              end_time: endTime 
            }),
          });

          const data = await response.json();

          if (data.success) {
            // ✅ Instantly update button UI
            if (data.is_available) {
              this.classList.remove('bg-red-500', 'hover:bg-red-600');
              this.classList.add('bg-green-500', 'hover:bg-green-600');
              this.innerHTML = `
                <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M5 12l5 5L20 7"/>
                </svg>`;
            } else {
              this.classList.remove('bg-green-500', 'hover:bg-green-600');
              this.classList.add('bg-red-500', 'hover:bg-red-600');
              this.innerHTML = `
                <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M6 6l12 12M18 6l-12 12"/>
                </svg>`;
            }

            // ✅ Refresh availability_dict **in the template**
            updateAvailabilityUI(data.availability_dict);
          } else {
            console.error('Failed to toggle availability:', data.error);
          }
        } catch (error) {
          console.error('Error:', error);
        } finally {
          // ✅ Re-enable button after request completes
          this.disabled = false;
        }
      });
    });

    // ✅ Function to update the availability UI based on new data from the backend
    function updateAvailabilityUI(availabilityDict) {
      document.querySelectorAll('.toggle-slot').forEach(button => {
        const date = button.getAttribute('data-date');
        const startTime = button.getAttribute('data-start-time');

        const key = `${date},${startTime}`;  // ✅ Match Django's new string key format
        const isAvailable = availabilityDict[key];

        if (isAvailable) {
          button.classList.remove('bg-red-500', 'hover:bg-red-600');
          button.classList.add('bg-green-500', 'hover:bg-green-600');
          button.innerHTML = `
            <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12l5 5L20 7"/>
            </svg>`;
        } else {
          button.classList.remove('bg-green-500', 'hover:bg-green-600');
          button.classList.add('bg-red-500', 'hover:bg-red-600');
          button.innerHTML = `
            <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 6l12 12M18 6l-12 12"/>
            </svg>`;
        }
      });
    }


    
    // Function to get CSRF token from cookies
    function getCSRFToken() {
      const name = 'csrftoken=';
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith(name)) {
          return cookie.substring(name.length, cookie.length);
        }
      }
      return '';
    }




  });
})();
