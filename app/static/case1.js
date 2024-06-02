document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('estimate_slider');
    const img = document.getElementById('estimate_img');
    const currentPriceSpan = document.getElementById('current-price');
    const currentSalesSpan = document.getElementById('total-sales');
    const currentRevenueSpan = document.getElementById('total-revenue');


    isProcessing = false;

    function updateSliderFill() {
        const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
        slider.style.setProperty('--slider-fill-width', `${value}%`);
    }

    slider.addEventListener('input', function() {
        updateSliderFill();
    });

    slider.addEventListener('input', function() {
        if(!isProcessing){
            isProcessing = true;
            const value = slider.value;
            fetch('/update_estimate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ value: value })
            })
            .then(response => response.json())
            .then(data => {
                // Update the image source with the new image data
                img.src = 'data:image/png;base64,' + data.img;
                currentPriceSpan.textContent=value;
                currentSalesSpan.textContent=data.total_sales;
                currentRevenueSpan.textContent=data.total_sales*value;
                isProcessing = false;
                //document.getElementById('other_variable_element').innerText = data.other_variable;
            });
        }
    });
    updateSliderFill();
});