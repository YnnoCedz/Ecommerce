function displayStars(rating) {
    const starContainer = doscument.getElementsById('shop-rating');
    starContainer.innerHTML = '' //
    
    for (let i=1; i<=5; i++){
        if (rating >= i) {
            starContainer.innerHTML += '<span class="star full">&#9733</span>'
        } else if (rating > i-1) {
            starContainer.innerHTML += '<span class="star half">&#9733</span>'
        } else {
            starContainer.innerHTML += '<span class="star empty">&#9733</span>'
        }
    }
}

displayStars(3.5);