document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('image-slider');
    const displayedImage = document.getElementById('displayed-image');

    const imageMap = [
        '1630',
        '1795',
        '1852',
        '1880',
        '1916',
        '1934',
        '1950'
    ];

    slider.addEventListener('input', function() {
        const imageIndex = slider.value;
        displayedImage.src = `../assets/2024-07-13-boston-map/boston_${imageMap[imageIndex]}.png`;
    });
});
