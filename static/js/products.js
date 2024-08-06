main_image = document.querySelector('#main-image');

images = document.querySelectorAll('.product-images');
images.forEach(image =>{
    image.addEventListener("click", ()=>{
        //alert(image.id);
        main_image.src = image.src;
    });
});