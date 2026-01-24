const img = document.getElementById("imagen");

img.addEventListener("click", () => {
  if (img.style.animationPlayState === "paused") {
    img.style.animationPlayState = "running";
  } else {
    img.style.animationPlayState = "paused";
  }
});

setTimeout(() => {
  window.location.href = "/clasificacion"; 
}, 2200);