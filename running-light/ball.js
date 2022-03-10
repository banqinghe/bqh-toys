class Ball {
  constructor(x, y, radius, speed) {
    this.x = x;
    this.y = y;
    this.speed = speed;
    this.radius = radius;
  }

  draw(ctx, color = '#fff') {
    ctx.beginPath();
    ctx.fillStyle = color;
    ctx.shadowBlur = 15;
    ctx.shadowColor = color;
    ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
    ctx.fill();
  }

  update() {
  }
}

class PlayerBall extends Ball {
  constructor(x, y, radius, speed) {
    super(x, y, radius, speed);
  }

  update(targetX, targetY) {
    const dx = Math.abs(targetX - this.x);
    const dy = Math.abs(targetY - this.y);
    const tan = dy / dx;
    const cos = Math.sqrt(1 / (tan ** 2 + 1));
    const sin = Math.sqrt(tan ** 2 / (1 + tan ** 2));

    this.x = targetX > this.x ?
      this.x + this.speed * cos :
      this.x - this.speed * cos;
    this.y = targetY > this.y ?
      this.y + this.speed * sin :
      this.y - this.speed * sin;
  }
}

export { Ball, PlayerBall };
