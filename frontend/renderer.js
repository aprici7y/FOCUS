document.addEventListener('DOMContentLoaded', async () => {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const loadingIndicator = document.getElementById('loading');
    const successIcon = document.getElementById('success');
    const errorIcon = document.getElementById('error');
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    const apiForm = document.getElementById('apiForm');
    const playlistForm = document.getElementById('playlistForm');
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Tab switching
    tabButtons.forEach(button => {
      button.addEventListener('click', () => {
        const tabId = button.getAttribute('data-tab');
        
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        button.classList.add('active');
        document.getElementById(tabId).classList.add('active');
      });
    });
  
    // Password visibility toggle
    togglePasswordButtons.forEach(button => {
      button.addEventListener('click', () => {
        const targetId = button.getAttribute('data-target');
        const inputField = document.getElementById(targetId);
        
        if (inputField.type === 'password') {
          inputField.type = 'text';
          button.classList.remove('fa-eye');
          button.classList.add('fa-eye-slash');
        } else {
          inputField.type = 'password';
          button.classList.remove('fa-eye-slash');
          button.classList.add('fa-eye');
        }
      });
    });
  
    // Load saved API keys
    try {
      const result = await window.electron.getApiKeys();
      console.log(result)
      if (result.success) {
        Object.entries(result.keys).forEach(([id, value]) => {
          const input = document.getElementById(id);
          console.log(id)
          if (input) {
            input.value = value;
          }
        });
      }
    } catch (error) {
      console.error('Error loading API keys:', error);
    }
  
    // API key form submission
    apiForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        
        // Show loading indicator
        loadingIndicator.classList.remove('hidden');
        await delay(2000)
        // Disable form inputs and submit button
        Array.from(this.elements).forEach(element => element.disabled = true);
        
        try {
            const result = await window.electron.saveApiKeys(data);
            console.log(result);
            
            // Clear visibility state
            successIcon.classList.add('hidden'); // Hide success icon
            errorIcon.classList.add('hidden'); // Hide error icon
            
            if (result.success) {
                // Show success icon
                successIcon.classList.remove('hidden'); 
                successIcon.classList.add('visible'); // Make it visible
                
                // Optionally hide error icon if previously shown
                errorIcon.classList.add('hidden');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Error saving API keys:', error);
            
            // Show error icon if an error occurs
            errorIcon.classList.remove('hidden'); 
            errorIcon.classList.add('visible'); // Make it visible
    
            // Hide the success icon if it was previously shown
            successIcon.classList.add('hidden');
        } finally {
            // Hide loading indicator
            loadingIndicator.classList.add('hidden'); // Hide the loading indicator
            Array.from(this.elements).forEach(element => element.disabled = false); // Re-enable inputs
        }
        setTimeout(() => {
            successIcon.classList.remove('visible'); // Hide the success icon
            successIcon.classList.add('hidden'); // Ensure it is hidden in the DOM
            errorIcon.classList.remove('visible'); // Hide the success icon
            errorIcon.classList.add('hidden'); // Ensure it is hidden in the DOM
        }, 2000); // 3000 milliseconds = 3 seconds
    });

   
// Playlist form submission
playlistForm.addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const formData = new FormData(this);
  const data = Object.fromEntries(formData.entries());
  
  // Show loading indicator
  loadingIndicator.classList.remove('hidden');
  await delay(2000); // Consistent with API key saving logic
  
  // Disable form inputs and submit button
  Array.from(this.elements).forEach(element => element.disabled = true);
  
  try {
      // Send data to the backend
      const result = await window.electron.submitPlaylist(data);
      
      // Clear visibility state
      successIcon.classList.add('hidden'); // Hide success icon
      errorIcon.classList.add('hidden'); // Hide error icon
      
      if (result.success) {
          // Show success icon
          successIcon.classList.remove('hidden'); 
          successIcon.classList.add('visible'); // Make it visible
          
          // Optionally hide error icon if previously shown
          errorIcon.classList.add('hidden');
      } else {
          throw new Error(result.error);
      }
  } catch (error) {
      console.error('Error submitting playlist:', error);
      
      // Show error icon if an error occurs
      errorIcon.classList.remove('hidden'); 
      errorIcon.classList.add('visible'); // Make it visible

      // Hide the success icon if it was previously shown
      successIcon.classList.add('hidden');
  } finally {
      // Hide loading indicator
      loadingIndicator.classList.add('hidden'); // Hide the loading indicator
      Array.from(this.elements).forEach(element => element.disabled = false); // Re-enable inputs
  }
  
  setTimeout(() => {
      successIcon.classList.remove('visible'); // Hide the success icon
      successIcon.classList.add('hidden'); // Ensure it is hidden in the DOM
      errorIcon.classList.remove('visible'); // Hide the error icon
      errorIcon.classList.add('hidden'); // Ensure it is hidden in the DOM
  }, 2000); // 2000 milliseconds = 2 seconds
});

});