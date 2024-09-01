const description = document.querySelector('.description');
const characters_count = document.querySelector('.char-count');
const max_characters = description.getAttribute('maxlength');

description.addEventListener('input', ()=>{
    const current_description_length = description.value.length;
    characters_count.textContent = `${current_description_length}/${max_characters}`
});


document.getElementById('images').addEventListener("change", function(event){
    const fileList = this.files;
    const fileListDiv = document.getElementById('file-list');
    const maxFiles = 10;
    fileListDiv.innerHTML = '';

    if (fileList.length > 0) {
        const ul = document.createElement('ul');

        let iterations = fileList.length;
        if (fileList.length > maxFiles){
            iterations = maxFiles;
        }

        for (let i = 0; i < iterations; i++) {
            const li = document.createElement('li');
            li.textContent = fileList[i].name; 
            ul.appendChild(li);
        }
        fileListDiv.appendChild(ul);
        } 
    else {
        fileListDiv.textContent = 'No files selected.';
    }    

});



const categories_btn = document.querySelector(".categories_btn");
const arrow_icon = document.querySelector(".bx-chevron-up");

categories_btn.addEventListener("click", (event) => {
    arrow_icon.style.transition = "transform 0.2s ease";
    
    if (categories_btn.classList.contains('open')) {
        arrow_icon.style.transform = "rotate(0deg)";
        categories_btn.classList.add('closed');
        categories_btn.classList.remove('open');
    } else {
        arrow_icon.style.transform = "rotate(180deg)";
        categories_btn.classList.remove('closed');
        categories_btn.classList.add('open');
    }

});


const all_checkboxes = document.querySelectorAll('input[name="categories[]"]');
const container = document.querySelector('.dropdown-container');

all_checkboxes.forEach(checkbox =>{
    li_item = checkbox.closest('li');
    li_item.addEventListener("click", (event)=>{
        if (event.target !== checkbox ){

            if (document.querySelectorAll('input[name="categories[]"]:checked').length > 3){
                checkbox.checked = false
                alert('You can select a maximum of 3 categories.');
                return;
            }

            checkbox.checked = !checkbox.checked;
            const changeEvent = new Event('change', { bubbles: true });
            checkbox.dispatchEvent(changeEvent);
        }
    });
});

container.addEventListener("change", function(event){
    if (event.target.type === "checkbox"){
        const checkbox = event.target;
        const selected_categories_list = document.getElementById('selected_categories_list');

        if (document.querySelectorAll('input[name="categories[]"]:checked').length > 3){
            checkbox.checked = false
            alert('You can select a maximum of 3 categories.');
            return;
        }

        if (event.target.checked){
            const selected_category = document.createElement('li');
            selected_category.id = checkbox.value;
            selected_category.textContent = checkbox.value;
            selected_category.classList.add('selected_category');
            selected_categories_list.appendChild(selected_category);
        }
        else{
            const item_to_remove = document.getElementById(checkbox.value);
            selected_categories_list.removeChild(item_to_remove);
        }
    }
});

document.getElementById('product-form').addEventListener('submit', function(event) {
    const images = document.getElementById('images');
    if (images.files.length === 0) {
        event.preventDefault(); 
        alert('Please upload at least one photo.');
    }
    const checkboxes = document.querySelectorAll('input[name="categories[]"]:checked');
    if (checkboxes.length === 0) {
        event.preventDefault(); 
        alert('Please select at least one category.');
    }
});
