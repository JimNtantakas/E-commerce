const textarea = document.querySelector('.review-text');
const characters_count = document.querySelector('.char-count');
const max_characters = textarea.getAttribute('maxlength');


const updateCharacterCount = () => {
    const text_length = textarea.value.replace(/\s+/g, '').length;
    characters_count.textContent = `${text_length}/${max_characters}`
};

textarea.addEventListener('input', updateCharacterCount);
updateCharacterCount();