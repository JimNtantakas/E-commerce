document.querySelectorAll(".like-button").forEach(button =>{
    button.addEventListener("click", ()=>{
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
                    button.classList.add('liked');  // Use class to set liked state
                    button.classList.remove('unliked');
                } else {
                    button.classList.remove('liked');  // Remove class for unliked state
                    button.classList.add('unliked');
                }
            }
            else{
                alert(data.message)
            }
        });
    });
});