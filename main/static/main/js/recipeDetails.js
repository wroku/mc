//Function for adding/removing servings

function changeServingsNumber(factor){
    let servings = parseInt(document.getElementById('numberOfServings').innerHTML);
    if(!((servings===1) && (factor === -1)) ){
        document.getElementById('numberOfServings').innerHTML = servings+factor;
        let quantities =  document.getElementsByClassName("quantity");
        for(let i=0; i<quantities.length; i++){
            let newQ = (parseFloat(quantities[i].innerHTML)/servings)*(servings+factor);
            quantities[i].innerHTML = newQ;
            }
    }
    setTimeout(function(){$(".btn").blur()}, 500);
}

