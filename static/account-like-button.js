const main_div = document.querySelector('#main-content')

main_div.addEventListener("click", (event) => {
    if (event.target && event.target.matches(".like-button, .like-button *")) {
        const button = event.target.closest(".like-button");
        const productId = button.id.replace("like-button-", "");
        fetch('/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_id: productId })
        }).then(response => response.json())
        .then(data =>{
            if (data.success){
                if (data.liked) {
                    button.classList.add('liked');  
                    button.classList.remove('unliked');
                } else {
                    button.classList.add('unliked');  // Remove class for unliked state
                    button.classList.remove('liked'); 
                }
            }
            else{
                alert(data.message)
            }
        });
    }
});