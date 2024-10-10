const form = document.getElementById('apiForm');
const loadingIndicator = document.getElementById('loading');

form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    loadingIndicator.classList.remove('hidden');
    
    Array.from(form.elements).forEach(element => element.disabled = true);
    
    window.electron.send('submit-form', data);
});

window.electron.receive('form-response', (response) => {
    loadingIndicator.classList.add('hidden');
    
    Array.from(form.elements).forEach(element => element.disabled = false);
    
    if (response.success) {
        console.log('Success:', response.data);
        alert('Data submitted successfully!');
    } else {
        console.error('Error:', response.error);
        alert('An error occurred while submitting the data.');
    }
});