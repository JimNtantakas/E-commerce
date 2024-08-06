const description = document.querySelector('.description');
const characters_count = document.querySelector('.char-count');
const max_characters = description.getAttribute('maxlength');

description.addEventListener('input', ()=>{
    const current_description_length = description.value.length;
    characters_count.textContent = `${current_description_length}/${max_characters}`
});