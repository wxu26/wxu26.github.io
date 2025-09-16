// Function to load and include HTML files
function includeHTML() {
    const elements = document.querySelectorAll('[data-include]');
    
    elements.forEach(element => {
        const file = element.getAttribute('data-include');
        
        fetch(file)
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    throw new Error('File not found: ' + file);
                }
            })
            .then(data => {
                element.innerHTML = data;
            })
            .catch(error => {
                console.error('Error loading include:', error);
                element.innerHTML = '<p>Error loading content</p>';
            });
    });
}

// Load includes when the page loads
document.addEventListener('DOMContentLoaded', includeHTML);

/*
// Resize image (the scale factor is based on how notion exports file)
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('img').forEach(img => {
    function resizeImage() {
      img.style.width = (img.naturalWidth / 5) + 'px';
      // img.style.height = (img.naturalHeight / 2) + 'px';
    }
    
    if (img.complete && img.naturalWidth > 0) {
      // Image already loaded
      resizeImage();
    } else {
      // Image still loading
      img.onload = resizeImage;
    }
  });
});
*/