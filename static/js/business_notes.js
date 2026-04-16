/**
 * Business Notes Auto-Save Logic
 * Handles debounced auto-saving for the dashboard scratchpad.
 */

document.addEventListener('DOMContentLoaded', function() {
    const noteArea = document.getElementById('business-note-area');
    const statusIndicator = document.getElementById('note-status');
    let timeout = null;

    if (noteArea) {
        noteArea.addEventListener('input', function() {
            clearTimeout(timeout);
            statusIndicator.innerText = 'Saving...';
            statusIndicator.classList.remove('opacity-0');
            
            timeout = setTimeout(function() {
                const noteContent = noteArea.value;
                const saveUrl = noteArea.getAttribute('data-url');

                fetch(saveUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: `content=${encodeURIComponent(noteContent)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        statusIndicator.innerText = 'Saved';
                        setTimeout(() => statusIndicator.classList.add('opacity-0'), 2000);
                    } else {
                        statusIndicator.innerText = 'Error';
                        statusIndicator.classList.add('text-red-500');
                    }
                })
                .catch(error => {
                    console.error('Error saving note:', error);
                    statusIndicator.innerText = 'Failed';
                    statusIndicator.classList.add('text-red-500');
                });
            }, 1000); // 1-second debounce
        });
    }

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
