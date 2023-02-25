$(function(){
    var sct = document.getElementsByClassName("section");
    var i;
  
    for (i = 0; i < sct.length; i++) {
    sct[i].addEventListener("click", function() {
      this.classList.toggle("active");
      var panel = this.nextElementSibling;
      if (panel.style.display == "block") {
        panel.style.display = "none";
      } else {
        panel.style.display = "block";
      }
    });
  }
  })
  