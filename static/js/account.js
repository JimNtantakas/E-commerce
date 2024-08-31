const orders_btn = document.querySelector('#orders-btn');
const wishlist_btn = document.querySelector('#wishlist-btn');
const cart_btn = document.querySelector('#cart-btn');
const ratings_btn = document.querySelector('#ratings-btn');
const my_products_btn = document.querySelector('#published-products-btn');
const logout_btn = document.querySelector("#logout-btn");

const mainContent_div = document.querySelector('#main-content');

orders_btn.addEventListener("click", function(){
    mainContent_div.innerHTML = '';
});


wishlist_btn.addEventListener("click", function(){
    mainContent_div.innerHTML = '';
    this.disabled = true;
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
            list.classList.add('products-list');
            data.forEach(product => {
                const listItem = document.createElement('li');
                const like_button = document.createElement('button');
                like_button.id = `like-button-${product._id}`;
                like_button.classList.add('like-button','liked');
                like_button.type = 'submit';
                const like_icon = document.createElement('i');
                like_icon.classList.add('bx', 'bx-heart');
                like_button.appendChild(like_icon);

                const image_link = document.createElement('a');
                image_link.href = `/products/${product._id}`;
                const image = document.createElement('img');
                image.classList.add('product-image');

                const title = document.createElement('a');
                title.text = product.title;
                title.classList.add('product-title','product-details-link');
                title.href = `/products/${product._id}`;

                const price = document.createElement('a');
                price.text = product.price+' €';
                price.classList.add('product-price','product-details-link');
                price.href = `'/products/${product._id}'`;
            
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
                listItem.appendChild(price);
                listItem.classList.add('product-item');
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
    })
    .finally( ()=> {
        this.disabled = false;
    });
});


cart_btn.addEventListener("click", function(){
    mainContent_div.innerHTML = '';
    this.disabled = true;
    fetch('/cart-products', {
        method: 'GET',
        headers: {
                'Content-Type': 'application/json'
            }
    })
    .then(response => response.json())
    .then(data => {
        if (data.length !=0 ){
            const list = document.createElement('ul');
            list.classList.add('products-list');
            data.forEach(product => {
                const listItem = document.createElement('li');
                const like_button = document.createElement('button');
                like_button.id = `like-button-${product._id}`;
                if (product.liked){       
                    like_button.classList.add('like-button','liked');
                }
                else{
                    like_button.classList.add('like-button','unliked');
                }
                
                like_button.type = 'submit';
                const like_icon = document.createElement('i');
                like_icon.classList.add('bx', 'bx-heart');
                like_button.appendChild(like_icon);

                //add the links to the products
                const image_link = document.createElement('a');
                image_link.href = `/products/${product._id}`;
                const image = document.createElement('img');
                image.classList.add('product-image');

                const title = document.createElement('a');
                title.text = product.title;
                title.classList.add('product-title','product-details-link');
                title.href = `/products/${product._id}`;

                const price = document.createElement('a');
                price.text = product.price+' €';
                price.classList.add('product-price','product-details-link');
                price.href = `'/products/${product._id}'`;
            
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
                listItem.appendChild(price);
                listItem.classList.add('product-item');
                list.appendChild(listItem);
            });
            mainContent_div.appendChild(list);
        }
        else{
            const message = document.createElement('p');
            message.classList.add('empty-message');
            message.textContent = "Your cart is empty!"
            mainContent_div.appendChild(message);
        }
    })
    .finally( ()=> {
        this.disabled = false;
    });
});


ratings_btn.addEventListener("click", function(){
    mainContent_div.innerHTML = '';
});


my_products_btn.addEventListener("click", function(){
    mainContent_div.innerHTML = '';
    this.disabled = true;
    fetch('/published-products', {
        method: 'GET',
        headers: {
                'Content-Type': 'application/json'
            }
    })
    .then(response => response.json())
    .then(data => {
        if (data.length !=0 ){
            const list = document.createElement('ul');
            list.classList.add('products-list');
            data.forEach(product => {
                const listItem = document.createElement('li');
                const like_button = document.createElement('button');
                like_button.id = `like-button-${product._id}`;
                if (product.liked){       
                    like_button.classList.add('like-button','liked');
                }
                else{
                    like_button.classList.add('like-button','unliked');
                }
                
                like_button.type = 'submit';
                const like_icon = document.createElement('i');
                like_icon.classList.add('bx', 'bx-heart');
                like_button.appendChild(like_icon);

                //add the links to the products
                const image_link = document.createElement('a');
                image_link.href = `/products/${product._id}`;
                const image = document.createElement('img');
                image.classList.add('product-image');

                const title = document.createElement('a');
                title.text = product.title;
                title.classList.add('product-title','product-details-link');
                title.href = `/products/${product._id}`;

                const price = document.createElement('a');
                price.text = product.price+' €';
                price.classList.add('product-price','product-details-link');
                price.href = `'/products/${product._id}'`;
            
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
                listItem.appendChild(price);
                listItem.classList.add('product-item');
                list.appendChild(listItem);
            });
            mainContent_div.appendChild(list);
        }
        else{
            const message = document.createElement('p');
            message.classList.add('empty-message');
            message.textContent = "Your cart is empty!";
            mainContent_div.appendChild(message);
        }
    })
    .finally( ()=> {
        this.disabled = false;
    });
});


logout_btn.addEventListener("click", function(){
    window.location.href = "/logout";
});


// Function to get query parameter values
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Check if 'section' is set to 'cart' in the URL
const section = getQueryParam('section');
if (section === 'cart') {
    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('cart-btn').click();
    });
}