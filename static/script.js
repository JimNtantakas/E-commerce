
const sell_button = document.querySelector('#sell-button');
sell_button.addEventListener("click", () => {
    window.location.href = "/selling"
});


/* 
const like_button = document.querySelectorAll("#like-button");
like_button.forEach((like_button) =>{
    like_button.addEventListener("click", () =>{
        like_button.color = red;
    });
});  
*/

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
                } else {
                    button.classList.remove('liked');  // Remove class for unliked state
                }
            }
            else{
                alert(data.message)
            }
        });
    });
});