    function processExport() {
        const element = document.querySelector('.a4-paper');
        const btn = document.getElementById('export-btn');
        btn.innerHTML = '⏳ Processing Layout...';
        btn.disabled = true;

        // 1. Take the picture
        html2canvas(element, { scale: 2, useCORS: true }).then(canvas => {
            // 2. Turn it into text (Base64 string)
            const imageData = canvas.toDataURL('image/png');
            
            // 3. Send it to Django!
            fetch("{% url 'save_export' template.id %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}' // Django security requirement
                },
                body: JSON.stringify({ image_data: imageData })
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === 'success') {
                    // 4. Hide Step 1, Show Step 2!
                    document.getElementById('step-1-controls').style.display = 'none';
                    document.getElementById('step-2-controls').style.display = 'block';
                } else {
                    alert('Error saving export to server.');
                    btn.innerHTML = '⚙️ Generate Exports';
                    btn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong!');
            });
        });
    }

    function resetExport() {
        document.getElementById('step-2-controls').style.display = 'none';
        document.getElementById('step-1-controls').style.display = 'block';
        const btn = document.getElementById('export-btn');
        btn.innerHTML = '⚙️ Generate Exports';
        btn.disabled = false;
    }