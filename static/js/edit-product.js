const description = document.querySelector('.description');
const characters_count = document.querySelector('.char-count');
const max_characters = description.getAttribute('maxlength');

const updateCharacterCount = () => {
    const current_description_length = description.value.length;
    characters_count.textContent = `${current_description_length}/${max_characters}`;
};

description.addEventListener('input', updateCharacterCount);
updateCharacterCount();


document.getElementById('main-image').addEventListener("change", function(event){
    const main_img = this.files;
    const fileDiv = document.getElementById('main-image-name');
    fileDiv.innerHTML = '';
    if (main_img.length > 0){
        fileDiv.textContent = main_img[0].name;
    }

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
        ul.classList.add('images-name-list');
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
const selected_categories_list = document.getElementById('selected_categories_list');

const checked_checkboxes = document.querySelectorAll('input[name="categories[]"]:checked');
checked_checkboxes.forEach(checkbox =>{
    const selected_category = document.createElement('li');
    selected_category.id = checkbox.value;
    selected_category.textContent = checkbox.value;
    selected_category.classList.add('selected_category');
    selected_categories_list.appendChild(selected_category);
});



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
        const checked_checkboxes = document.querySelectorAll('input[name="categories[]"]:checked');
        for (let i=0;i<checked_checkboxes.length-1;i++){
            if (checked_checkboxes[i].closest('li').getAttribute('categoryClass') != checked_checkboxes[i+1].closest('li').getAttribute('categoryClass')){
                checkbox.checked = false
                alert("Select from the same category only");
                return 
            }
        }

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
    const main_image = document.getElementById('main-image');
    const main_img_checkbox = document.getElementById('0');

    if (main_image.files.length === 0  && main_img_checkbox.checked) {
        event.preventDefault(); 
        alert('Please upload at least one main image.');
    }
    const checkboxes = document.querySelectorAll('input[name="categories[]"]:checked');
    if (checkboxes.length === 0) {
        event.preventDefault(); 
        alert('Please select at least one category.');
    }
});
