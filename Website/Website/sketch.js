/* Ant trails background — soft pastel, behind UI */
let trails = [];

function setup(){
  const c = createCanvas(window.innerWidth, window.innerHeight);
  c.parent('bg-canvas');
  c.style('z-index','0'); c.style('position','fixed'); c.style('top','0'); c.style('left','0');
  c.style('pointer-events','none');
  noFill(); strokeWeight(1.2);
  initTrails();
}

function windowResized(){
  resizeCanvas(window.innerWidth, window.innerHeight);
  initTrails();
}

function initTrails(){
  trails = [];
  const n = Math.max(8, Math.floor((width * height) / 220000));
  for (let i=0;i<n;i++){
    trails.push({
      x: random(width), y: random(height),
      dx: random(-0.6, 0.6), dy: random(-0.6, 0.6),
      hue: random([ color(255,143,171, 28), color(174,226,221, 28) ]),
      life: random(220, 460)
    });
  }
}

function draw(){
  clear();
  for (const t of trails){
    stroke(t.hue);
    beginShape();
    for (let k=0;k<10;k++){
      const nx = t.x + noise(t.x*0.002, frameCount*0.002)*14 - 7;
      const ny = t.y + noise(t.y*0.002, frameCount*0.002)*14 - 7;
      curveVertex(nx, ny);
    }
    endShape();

    // tiny ant bodies
    noStroke();
    fill(0, 30);
    ellipse(t.x, t.y, 2.5, 2.5);
    ellipse(t.x+3, t.y, 1.8, 1.8);
    ellipse(t.x-3, t.y, 1.8, 1.8);

    t.x += t.dx; t.y += t.dy; t.life--;
    if (t.x<0||t.x>width) t.dx*=-1;
    if (t.y<0||t.y>height) t.dy*=-1;
    if (t.life<=0) Object.assign(t, { x:random(width), y:random(height), life: random(220,460) });
  }
}
