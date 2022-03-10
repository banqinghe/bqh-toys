import { Ball, PlayerBall } from './ball.js';
import { distance, getRandomInt } from './utils.js';

const canvas = document.getElementById('canvas');

const width = canvas.width = document.documentElement.clientWidth;
const height = canvas.height = document.documentElement.clientHeight - 4;

const ctx = canvas.getContext('2d');

let pointX = 1;
let pointY = 1;

let isRunning = true;

canvas.addEventListener('mousemove', e => {
  pointX = e.offsetX;
  pointY = e.offsetY;
});

canvas.addEventListener('touchdown', e => {
  pointX = e.offsetX;
  pointY = e.offsetY;
});

let balls = Array.from({ length: 20 }, () => new Ball(
  getRandomInt(0, width), getRandomInt(0, height), getRandomInt(3, 15), 0)
);

let bombs = Array.from({ length: 20 }, () => new Ball(
  getRandomInt(0, width), getRandomInt(0, height), getRandomInt(3, 10), 0)
);

const playerBall = new PlayerBall(0, 0, 5, 1);

function clearCanvas() {
  ctx.fillStyle = '#111';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function checkCollision(player, balls) {
  const result = {
    cnt: 0,
    indexList: [],
  }

  balls.forEach((ball, index) => {
    if (distance(player, ball) < player.radius + ball.radius) {
      result.cnt++;
      result.indexList.push(index);
    }
  });
  return result.cnt ? result : null;
}

function animate() {
  clearCanvas();
  balls.forEach(ball => ball.draw(ctx, '#ffb'));
  bombs.forEach(bomb => bomb.draw(ctx, '#f11'));

  if (!balls.length) {
    alert('你赢了！');
    return;
  }

  const collisionStatus = checkCollision(playerBall, balls);
  if (collisionStatus) {
    playerBall.radius += collisionStatus.cnt;
    playerBall.speed += 0.2;
    balls = balls.filter((_, index) => !collisionStatus.indexList.includes(index));
  }

  const bombCollisionStatus = checkCollision(playerBall, bombs);
  if (bombCollisionStatus) {
    bombs[bombCollisionStatus.indexList[0]].radius += 7;
    // setTimeout(() => {
    //   isRunning = false;
    // }, 1000);
  } else {
    playerBall.draw(ctx);
    playerBall.update(pointX, pointY);
  }

  if (isRunning) {
    requestAnimationFrame(animate);
  }
}

function main() {
  animate();
}

main();