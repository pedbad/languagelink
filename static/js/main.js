(function () {
  document.addEventListener("DOMContentLoaded", function () {
    console.log('==== DOM loaded - JS called ====');

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
  });
})();
