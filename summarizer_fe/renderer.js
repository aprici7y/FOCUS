document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const loadingIndicator = document.getElementById('loading');

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

    // Form submissions
    const forms = {
        apiForm: document.getElementById('apiForm'),
        playlistForm: document.getElementById('playlistForm'),
        transcriptForm: document.getElementById('transcriptForm')
    };

    Object.values(forms).forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());
            
            // Show loading indicator
            loadingIndicator.classList.remove('hidden');
            
            // Disable form inputs and submit button
            Array.from(form.elements).forEach(element => element.disabled = true);
            
            // We'll use IPC to send this data to the main process
            window.electron.send('submit-form', { formId: this.id, data });
        });
    });

    // Listen for the response from the main process
    window.electron.receive('form-response', (response) => {
        // Hide loading indicator
        loadingIndicator.classList.add('hidden');
        
        // Re-enable form inputs and submit button for all forms
        Object.values(forms).forEach(form => {
            Array.from(form.elements).forEach(element => element.disabled = false);
        });
        
        if (response.success) {
            console.log('Success:', response.data);
            alert('Data submitted successfully!');
        } else {
            console.error('Error:', response.error);
            alert('An error occurred while submitting the data.');
        }
    });
});