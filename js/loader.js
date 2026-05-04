function showLoader(text) {
    text = text || 'Загрузка...';
    
    hideLoader();
    
    const overlay = document.createElement('div');
    overlay.className = 'loader-overlay';
    overlay.id = 'loader';
    overlay.innerHTML = '<div class="loader-spinner"></div><div class="loader-text">' + text + '</div>';
    document.body.appendChild(overlay);
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.remove();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    hideLoader();
});