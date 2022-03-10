function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}

function distance(a, b) {
  return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
}

export { getRandomInt, distance };