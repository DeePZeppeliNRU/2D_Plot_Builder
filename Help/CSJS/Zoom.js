document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.zoomable-image'); // Все изображения
    const overlay = document.querySelector('.overlay'); // Единственный overlay

    images.forEach((image) => {
        const container = image.closest('.image-container'); // Контейнер изображения

        image.addEventListener('click', function() {
            // Убираем увеличение у всех других картинок
            images.forEach((img) => {
                if (img !== image) {
                    img.classList.remove('zoomed');
                    img.closest('.image-container').classList.remove('zoomed');
                }
            });

            // Увеличиваем текущую картинку
            container.classList.toggle('zoomed');
            image.classList.toggle('zoomed');
            overlay.classList.toggle('active');
        });
    });

    // Закрытие по клику на overlay
    overlay.addEventListener('click', function() {
        images.forEach((image) => {
            const container = image.closest('.image-container');
            container.classList.remove('zoomed'); // Возвращаем контейнер к исходному размеру
            image.classList.remove('zoomed'); // Возвращаем изображение к исходному размеру
        });
        overlay.classList.remove('active'); // Скрываем overlay
    });
});