
const sort_btn = document.querySelector(".sort-button");
const arrow_icon = document.querySelector(".bx-chevron-up");

sort_btn.addEventListener("click", (event)=>{
    event.preventDefault();
    arrow_icon.style.transition = "transform 0.2s ease";
    
    if (sort_btn.classList.contains('open')) {
        arrow_icon.style.transform = "rotate(0deg)";
        sort_btn.classList.add('closed');
        sort_btn.classList.remove('open');
    } else {
        arrow_icon.style.transform = "rotate(180deg)";
        sort_btn.classList.remove('closed');
        sort_btn.classList.add('open');
    }

});


const dropdownItems = document.querySelectorAll(".dropdown-list li");
const form = document.getElementById("filters-form");
const sort_by = document.getElementById("sort_by")

dropdownItems.forEach(item =>{
    item.addEventListener("click", (event) =>{
        const selected_value = event.target.dataset.value;

        sort_by.value = selected_value;
        sort_btn.textContent = selected_value;
        form.submit();
    });
});



const clear_filter_btn = document.querySelector('.clear-filters-button');
const min = document.querySelector('.price-input.min');
const max = document.querySelector('.price-input.max');

clear_filter_btn.addEventListener("click", (event)=>{
    event.preventDefault();
    min.value = '';
    max.value = '';
    sort_by.value = '';

    form.submit();
});
