const orders_btn = document.querySelector('#orders-btn');
const wishlist_btn = document.querySelector('#wishlist-btn');
const ratings_btn = document.querySelector('#ratings-btn');

const mainContent_div = document.querySelector('#main-content')


orders_btn.addEventListener("click", () =>{
    mainContent_div.innerHTML = '';
});



wishlist_btn.addEventListener("click", ()=>{
    mainContent_div.innerHTML = '';
    fetch('/liked-products', {
        method: 'GET',
        headers: {
                'Content-Type': 'application/json'
            }
    })
    .then(response => response.json())
    .then(data => {
        if (data.length !=0 ){
            const list = document.createElement('ul');
            list.classList.add('liked-products-list');
            data.forEach(product => {
                const listItem = document.createElement('li');
                const like_button = document.createElement('button');
                like_button.id = `like-button-${product._id}`;
                like_button.classList.add('like-button','liked');
                like_button.type = 'submit';
                const like_icon = document.createElement('i');
                like_icon.classList.add('bx', 'bx-heart');
                like_button.appendChild(like_icon);

                //add the links to the products
                const image_link = document.createElement('a');
                image_link.href = `/products/${product._id}`;
                const image = document.createElement('img');
                image.classList.add('liked-product-image');

                const title = document.createElement('a');
                title.text = product.title;
                title.classList.add('liked-product-title','product-delails-link');
                title.href = `/products/${product._id}`;
            
                if (product.photos.length > 0) {
                    const photo_id = product.photos[0];  // Assuming you only want the first photo
                    image.src = `/photo/${photo_id}`;
                } else {
                    image.alt = 'No image available';
                }
                
                image_link.appendChild(image);
                listItem.appendChild(like_button);
                listItem.appendChild(image_link);
                listItem.appendChild(title);
                listItem.classList.add('liked-product-item');
                list.appendChild(listItem);
            });
            mainContent_div.appendChild(list);
        }
        else{
            const message = document.createElement('p');
            message.classList.add('empty-message');
            message.textContent = "Your wishlist is empty!"
            mainContent_div.appendChild(message);
        }
    });
});


ratings_btn.addEventListener("click", () =>{
    mainContent_div.innerHTML = '';
});
