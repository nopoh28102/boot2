document.addEventListener('DOMContentLoaded', function() {
    const typeSelect = document.getElementById('type');
    const mediaSection = document.getElementById('mediaSection');
    const mediaTypeSelect = document.getElementById('media_type');
    const mediaUrlInput = document.getElementById('media_url');
    const mediaFileInput = document.getElementById('media_file');

    function toggleMediaFields() {
        if (typeSelect.value === 'media') {
            mediaSection.style.display = 'block';
        } else {
            mediaSection.style.display = 'none';
        }
    }

    typeSelect.addEventListener('change', toggleMediaFields);
    toggleMediaFields();

    mediaTypeSelect.addEventListener('change', function() {
        if (mediaTypeSelect.value === 'file') {
            mediaUrlInput.style.display = 'none';
            mediaFileInput.style.display = 'block';
        } else {
            mediaUrlInput.style.display = 'block';
            mediaFileInput.style.display = 'none';
        }
    });
});
