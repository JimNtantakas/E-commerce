const main_image = document.querySelector('#main-image');

const li = document.querySelectorAll('.image-element');
li.forEach(element =>{
    const image = element.querySelector('img');
    element.addEventListener("click", ()=>{
        main_image.src = image.src;
    });
});


images = document.querySelectorAll('.product-images');
images.forEach(image =>{
    image.addEventListener("click", ()=>{
        //alert(image.id);
        main_image.src = image.src;
    });
});