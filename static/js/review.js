const textarea = document.querySelector('.review-text');
const characters_count = document.querySelector('.char-count');
const max_characters = textarea.getAttribute('maxlength');

textarea.addEventListener('input', ()=>{
    const text_length = textarea.value.length;
    characters_count.textContent = `${text_length}/${max_characters}`
});