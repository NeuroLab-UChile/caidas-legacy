(function () {
    document.addEventListener("DOMContentLoaded", function () {
        const weekInputs = document.querySelectorAll('input[type="week"]');
        weekInputs.forEach((input) => {
            input.addEventListener("change", (e) => {
                console.log(`Week selected: ${e.target.value}`);
            });
        });
    });
})(); 