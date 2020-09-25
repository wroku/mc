//Simple functions triggering css animations on the front page

window.onscroll = function() {slideIn()};
function slideIn(){
    console.log(document.documentElement.scrollTop)
    if (document.documentElement.scrollTop > 100){
    document.getElementById("question").style.animationName="moveQ";
    }
}
function darken(id){
    let image = document.getElementById(id);
    image.style.animationName="shadow";
    let button = document.getElementById("btn_" + id);
    button.style.animationName="move";
}
function lighten(id){
    let image = document.getElementById(id);
    image.style.animationName="";
    let button = document.getElementById("btn_" + id);
    button.style.animationName="";
}